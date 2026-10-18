import type { AnalyzeResult, MenuItem } from "./api";

/**
 * GERÇEK VERİ SETİ DEMOSU — UNIMIB/Padova üniversite yemekhanesi tepsisi
 * (demo/real_dataset, MIT; bkz. repo README). İtalyan yemekhanesi fotoğrafı:
 * Türk yemekhanesi saha ölçümü değildir, "sahnelenmiş demo" olarak sunulur.
 *
 * DEMO_RESULT: tray6 leftover2 çiftinin GERÇEK pipeline çıktısı
 * (CLIP+EVREN VLM, 2026-10-18 çalıştırması). Ground-truth maskelere göre
 * öğe bazında hata: makarna 0,10 · pirzola 0,008 · fasulye 0,078 · salata 0,041.
 * API açıksa aynı fotoğraflar CANLI analiz edilir (~60-90 sn).
 */

export const DEMO_MENU: MenuItem[] = [
  {
    key: "midyeli_makarna",
    name_tr: "Midye İstiridyeli Makarna",
    name_en: "pasta with clams and mussels",
    category: "ana",
    portion_g: 200,
    clip_prompt: "a plate of pasta with clams and mussels",
  },
  {
    key: "izgara_pirzola",
    name_tr: "Izgara Pirzola",
    name_en: "grilled pork cutlet",
    category: "ana",
    portion_g: 180,
    clip_prompt: "a grilled pork cutlet on a plate",
  },
  {
    key: "fasulye",
    name_tr: "Fasulye",
    name_en: "beans",
    category: "yan",
    portion_g: 150,
    clip_prompt: "a plate of cooked white beans",
  },
  {
    key: "salata",
    name_tr: "Salata",
    name_en: "salad",
    category: "yan",
    portion_g: 100,
    clip_prompt: "a plate of fresh green salad",
  },
];

export const DEMO_MENU_KEYS = DEMO_MENU.map((m) => m.key);

/** Ham fotoğraflar (analiz girdisi olarak yüklenir) */
export const DEMO_PHOTOS = {
  before: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/demo/real_before.jpg`,
  after: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/demo/real_after.jpg`,
};

/** Annotate edilmiş overlay'ler (demo modu çıktısı) */
export const DEMO_OVERLAYS = {
  before: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/demo/real_overlay_before.png`,
  after: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/demo/real_overlay_after.png`,
};

/** Önceden hesaplanmış demo sonucu — API kapalıyken gösterilir. */
export const DEMO_RESULT: AnalyzeResult = {
  items: [
    {
      key: "midyeli_makarna",
      name_tr: "Midye İstiridyeli Makarna",
      name_en: "pasta with clams and mussels",
      before_area_frac: 1.0,
      after_area_frac: 0.714,
      leftover_ratio: 0.714,
      leftover_pct: 71,
      estimated_leftover_g: 142.8,
      portion_g: 200,
      clip_confidence: 0.8,
    },
    {
      key: "izgara_pirzola",
      name_tr: "Izgara Pirzola",
      name_en: "grilled pork cutlet",
      before_area_frac: 1.0,
      after_area_frac: 0.243,
      leftover_ratio: 0.243,
      leftover_pct: 24,
      estimated_leftover_g: 43.7,
      portion_g: 180,
      clip_confidence: 0.99,
    },
    {
      key: "fasulye",
      name_tr: "Fasulye",
      name_en: "beans",
      before_area_frac: 1.0,
      after_area_frac: 0.922,
      leftover_ratio: 0.922,
      leftover_pct: 92,
      estimated_leftover_g: 138.3,
      portion_g: 150,
      clip_confidence: 0.98,
    },
    {
      key: "salata",
      name_tr: "Salata",
      name_en: "salad",
      before_area_frac: 1.0,
      after_area_frac: 0.959,
      leftover_ratio: 0.959,
      leftover_pct: 96,
      estimated_leftover_g: 95.9,
      portion_g: 100,
      clip_confidence: 0.8,
    },
  ],
  matched_items: 4,
  total_estimated_leftover_g: 420.7,
  warnings: [],
  note: "DEMO MODU — önceden hesaplanmış sonuç (gerçek yemekhane fotoğrafı, UNIMIB tray6).",
};
