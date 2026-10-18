export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface MenuItem {
  key: string;
  name_tr: string;
  name_en: string;
  category: string;
  portion_g: number;
  clip_prompt?: string;
}

export interface AnalyzeItem {
  key: string;
  name_tr: string;
  name_en: string;
  before_area_frac: number;
  after_area_frac: number;
  leftover_ratio: number;
  leftover_pct: number;
  estimated_leftover_g: number | null;
  portion_g: number | null;
  clip_confidence: number;
}

export interface AnalyzeResult {
  items: AnalyzeItem[];
  matched_items: number;
  total_estimated_leftover_g: number;
  warnings: string[];
  note: string;
  annotated_before_b64?: string;
  annotated_after_b64?: string;
}

export interface Simulation {
  reduction_pct: number;
  old_portion_g: number;
  new_portion_g: number;
  saved_kg_low: number;
  saved_kg_high: number;
  horizon_days: number;
  impact_low: { co2e_kg: number };
  impact_high: { co2e_kg: number };
}

export interface Recommendation {
  item_key: string;
  name_tr: string;
  avg_leftover_pct: number;
  top_reason: string | null;
  type: "portion" | "watch" | "kitchen";
  priority: "high" | "medium";
  text_tr: string;
  text_en: string;
  simulation: Simulation | null;
}

export interface StatsPayload {
  meta: {
    scenario_note: string;
    days: number;
    scenario_records: number;
  };
  summary: {
    meals_served: number;
    total_leftover_kg: number;
    g_per_meal: number;
    avg_leftover_pct: number;
    impact: {
      kg: number;
      co2e_kg: number;
      water_l: number;
      cost_tl: number;
    };
  };
  daily: { date: string; meals: number; leftover_kg: number; g_per_meal: number }[];
  items: {
    key: string;
    name_tr: string;
    category: string;
    portion_g: number | null;
    appearances: number;
    serving_freq?: number;
    avg_daily_meals: number;
    avg_leftover_pct: number;
    total_kg: number;
    trend: "up" | "down" | "flat";
    top_reason: string | null;
  }[];
  reasons: { code: string; name_tr: string; count: number; share: number }[];
  recommendations: Recommendation[];
  real: {
    trays_analyzed: number;
    total_kg: number;
    note: string;
    by_item: { key: string; name_tr: string; trays: number; total_g: number; avg_g_per_tray: number }[];
  };
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} ${detail.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchMenu(): Promise<MenuItem[]> {
  const res = await fetch(`${API_URL}/menu`, { cache: "no-store" });
  const data = await jsonOrThrow<{ items: MenuItem[] }>(res);
  return data.items;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return false;
    const d = (await res.json()) as { models_ready?: boolean };
    return Boolean(d.models_ready);
  } catch {
    return false;
  }
}

export async function analyzePair(
  before: Blob,
  after: Blob,
  menu: MenuItem[],
  save: boolean
): Promise<AnalyzeResult> {
  const form = new FormData();
  form.append("before", before, "before.png");
  form.append("after", after, "after.png");
  form.append("menu", JSON.stringify(menu));
  form.append("save", String(save));
  const res = await fetch(`${API_URL}/analyze`, { method: "POST", body: form });
  return jsonOrThrow<AnalyzeResult>(res);
}

export async function fetchStats(days = 56): Promise<StatsPayload> {
  const res = await fetch(`${API_URL}/stats?days=${days}`, { cache: "no-store" });
  return jsonOrThrow<StatsPayload>(res);
}

export async function postFeedback(reasonCode: string, itemKey?: string): Promise<void> {
  const form = new FormData();
  form.append("reason_code", reasonCode);
  if (itemKey) form.append("item_key", itemKey);
  const res = await fetch(`${API_URL}/feedback`, { method: "POST", body: form });
  await jsonOrThrow<unknown>(res);
}

export const REASON_CODES = [
  "porsiyon_buyuk",
  "tadi",
  "sicaklik",
  "cesit_tekrar",
  "acele",
  "diger",
] as const;
