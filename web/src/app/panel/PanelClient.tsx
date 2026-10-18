"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useT } from "@/lib/i18n";
import { fetchStats, type StatsPayload } from "@/lib/api";
import { Stamp } from "@/components/Badges";

const REASON_COLORS: Record<string, string> = {
  porsiyon_buyuk: "#c8451c",
  tadi: "#2f6b4f",
  sicaklik: "#7a5a00",
  cesit_tekrar: "#5b6bb5",
  acele: "#7d8878",
  diger: "#b0a894",
};

const CAT_COLORS: Record<string, string> = {
  corba: "#5b8f7b",
  ana: "#c8451c",
  garnitur: "#d9a441",
  yan: "#2f6b4f",
  tatli: "#7a5a00",
};

export default function PanelClient() {
  const { t, lang } = useT();
  const [stats, setStats] = useState<StatsPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchStats(56)
      .then(setStats)
      .catch((e) => setError(String(e)));
  }, []);

  if (error)
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <p className="rounded-xl bg-paprika/5 p-4 font-mono text-sm text-paprika">{error}</p>
      </div>
    );
  if (!stats)
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <p className="text-ink/50">{t.common.loading}</p>
      </div>
    );

  const s = stats.summary;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
          {t.panel.title}
        </h1>
        <p className="mt-2 text-ink/70">{t.panel.sub}</p>
      </header>

      {/* Özet kartları */}
      <section className="grid gap-4 rounded-2xl border border-ink/10 bg-well p-4 shadow-sm sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          value={`${s.total_leftover_kg.toLocaleString("tr-TR")} ${t.common.kg}`}
          label={t.panel.totalLeftover}
          badge="scenario"
          sub={`${s.meals_served.toLocaleString("tr-TR")} ${t.panel.mealsServed}`}
        />
        <SummaryCard
          value={`${s.g_per_meal} ${t.common.g}`}
          label={t.panel.gPerMeal}
          badge="scenario"
          sub={`≈ %${s.avg_leftover_pct} · ${t.panel.avgPct.toLowerCase()}`}
        />
        <SummaryCard
          value={`${s.impact.co2e_kg.toLocaleString("tr-TR")} kg`}
          label={t.panel.co2}
          badge="scenario"
          sub={`${s.impact.water_l.toLocaleString("tr-TR")} L ${t.panel.water.toLowerCase()}`}
        />
        <SummaryCard
          value={`${s.impact.cost_tl.toLocaleString("tr-TR")} ₺`}
          label={t.panel.cost}
          badge="scenario"
          sub={t.panel.trendNote}
        />
      </section>

      {/* Trend + Nedenler */}
      <section className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-ink/10 bg-well p-5 shadow-sm lg:col-span-2">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="font-display text-lg font-bold">{t.panel.trendTitle}</h2>
            <Stamp kind="scenario" />
          </div>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.daily} margin={{ top: 5, right: 10, bottom: 0, left: -18 }}>
                <CartesianGrid stroke="#1c2a2110" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: "#7d8878" }}
                  tickFormatter={(d: string) => d.slice(5)}
                  interval={4}
                />
                <YAxis tick={{ fontSize: 10, fill: "#7d8878" }} />
                <Tooltip
                  contentStyle={{
                    borderRadius: 12,
                    border: "1px solid #1c2a2122",
                    fontSize: 12,
                  }}
                  formatter={(v) => [`${v} g`, t.panel.gPerMeal]}
                />
                <Line
                  type="monotone"
                  dataKey="g_per_meal"
                  stroke="#c8451c"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-2 font-mono text-[11px] text-ink/50">{t.panel.trendNote}</p>
        </div>

        <div className="rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="font-display text-lg font-bold">{t.panel.reasonsTitle}</h2>
            <Stamp kind="scenario" />
          </div>
          <div className="mt-2 h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.reasons}
                  dataKey="count"
                  nameKey="name_tr"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={2}
                >
                  {stats.reasons.map((r) => (
                    <Cell key={r.code} fill={REASON_COLORS[r.code] ?? "#b0a894"} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ borderRadius: 12, fontSize: 12 }}
                  formatter={(v, n) => [v, n]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-2 space-y-1.5 text-sm">
            {stats.reasons.slice(0, 5).map((r) => (
              <li key={r.code} className="flex items-center gap-2">
                <span
                  className="size-2.5 rounded-sm"
                  style={{ background: REASON_COLORS[r.code] ?? "#b0a894" }}
                />
                <span className="text-ink/75">{r.name_tr}</span>
                <span className="ml-auto font-mono text-xs text-ink/50">
                  %{Math.round(r.share * 100)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Yemek sıralaması */}
      <section className="mt-6 rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="font-display text-lg font-bold">{t.panel.rankTitle}</h2>
          <Stamp kind="scenario" />
          <span className="font-mono text-[11px] text-ink/50">{t.panel.rankHint}</span>
        </div>
        <div className="mt-4 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={stats.items.slice(0, 10)}
              layout="vertical"
              margin={{ top: 0, right: 20, bottom: 0, left: 10 }}
            >
              <CartesianGrid stroke="#1c2a2110" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: "#7d8878" }} unit="%" />
              <YAxis
                type="category"
                dataKey="name_tr"
                width={130}
                tick={{ fontSize: 11, fill: "#1c2a21" }}
              />
              <Tooltip
                contentStyle={{ borderRadius: 12, fontSize: 12 }}
                formatter={(v) => [`%${v}`, t.panel.avgPct]}
              />
              <Bar dataKey="avg_leftover_pct" radius={[0, 6, 6, 0]}>
                {stats.items.slice(0, 10).map((it) => (
                  <Cell
                    key={it.key}
                    fill={CAT_COLORS[it.category] ?? "#7d8878"}
                    opacity={it.avg_leftover_pct >= 20 ? 1 : 0.65}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Öneriler */}
      <section className="mt-6">
        <h2 className="font-display text-lg font-bold">{t.panel.recsTitle}</h2>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {stats.recommendations.slice(0, 6).map((r) => (
            <RecCard key={r.item_key} rec={r} lang={lang} />
          ))}
        </div>
      </section>

      {/* Gerçek kayıtlar */}
      <section className="mt-6 rounded-2xl border border-traydeep/25 bg-tray/5 p-5">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="font-display text-lg font-bold text-traydeep">{t.panel.realTitle}</h2>
          <Stamp kind="real" />
          <Stamp kind="estimate" />
        </div>
        {stats.real.trays_analyzed === 0 ? (
          <p className="mt-3 text-sm text-ink/60">{t.panel.realEmpty}</p>
        ) : (
          <div className="mt-4 space-y-2">
            <p className="font-mono text-sm">
              {stats.real.trays_analyzed} {t.panel.trays} · {stats.real.total_kg}{" "}
              {t.common.kg}
            </p>
            {stats.real.by_item.map((it) => (
              <div
                key={it.key}
                className="flex items-baseline justify-between rounded-lg bg-well px-4 py-2.5 text-sm"
              >
                <span className="font-medium">{it.name_tr}</span>
                <span className="font-mono text-xs text-ink/60">
                  {it.trays} tepsi · ort {it.avg_g_per_tray} {t.common.g}/tepsi
                </span>
              </div>
            ))}
            <p className="font-mono text-[11px] text-ink/50">{stats.real.note}</p>
          </div>
        )}
      </section>
    </div>
  );
}

function SummaryCard({
  value,
  label,
  badge,
  sub,
}: {
  value: string;
  label: string;
  badge: "scenario" | "estimate";
  sub?: string;
}) {
  return (
    <div className="well p-4">
      <div className="flex items-start justify-between gap-2">
        <p className="font-display text-2xl font-bold tracking-tight">{value}</p>
        <Stamp kind={badge} />
      </div>
      <p className="mt-1 text-sm font-medium text-ink/75">{label}</p>
      {sub && <p className="mt-1 font-mono text-[11px] leading-snug text-ink/50">{sub}</p>}
    </div>
  );
}

function RecCard({ rec, lang }: { rec: StatsPayload["recommendations"][number]; lang: "tr" | "en" }) {
  const { t } = useT();
  const typeLabel =
    rec.type === "portion" ? t.panel.recPortion : rec.type === "kitchen" ? t.panel.recKitchen : t.panel.recWatch;
  const sim = rec.simulation;

  return (
    <div className="rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="font-display text-lg font-bold">{rec.name_tr}</h3>
        <span
          className={`stamp ${
            rec.priority === "high" ? "text-paprika" : "text-ink/60"
          }`}
        >
          {rec.priority === "high" ? t.panel.recHigh : t.panel.recMedium}
        </span>
        <span className="rounded-md bg-ink/5 px-2 py-1 font-mono text-[11px] font-semibold uppercase tracking-wide text-ink/60">
          {typeLabel}
        </span>
        <span className="ml-auto font-mono text-lg font-bold text-paprika">
          %{rec.avg_leftover_pct}
        </span>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-ink/75">
        {lang === "en" ? rec.text_en : rec.text_tr}
      </p>
      {sim && (
        <div className="mt-4 rounded-xl bg-wellin/70 p-4">
          <div className="flex items-center gap-2">
            <p className="font-mono text-xs font-semibold uppercase tracking-wide text-ink/60">
              {t.panel.simOldNew}: {sim.old_portion_g}g → {sim.new_portion_g}g (−%{sim.reduction_pct})
            </p>
            <Stamp kind="simulation" />
          </div>
          <p className="mt-2 font-mono text-sm">
            {t.panel.simSaved}:{" "}
            <strong className="text-traydeep">
              {sim.saved_kg_low}–{sim.saved_kg_high} {t.common.kg}
            </strong>{" "}
            · ≈{sim.impact_low.co2e_kg}–{sim.impact_high.co2e_kg} kg CO₂e · {sim.horizon_days}{" "}
            {t.panel.simDays}
          </p>
          <p className="mt-2 text-[11px] leading-snug text-ink/50">{t.panel.simNote}</p>
        </div>
      )}
    </div>
  );
}
