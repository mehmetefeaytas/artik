import type { AnalyzeResult } from "./api";

/** API erişilemezse kullanılan ÖN-HESAPLANMIŞ demo sonucu (senaryo).
 *  Kaynak: api/scripts/test_pipeline.py çıktısı — kompozit test çifti,
 *  ground truth: çorba %5, fasulye %62, pilav %15, salata %85. */
export const DEMO_RESULT: AnalyzeResult = {
  items: [
    {
      key: "mercimek_corbasi",
      name_tr: "Mercimek Çorbası",
      name_en: "red lentil soup",
      before_area_frac: 0.036,
      after_area_frac: 0,
      leftover_ratio: 0,
      leftover_pct: 0,
      estimated_leftover_g: 0,
      portion_g: 250,
      clip_confidence: 0.99,
    },
    {
      key: "kuru_fasulye",
      name_tr: "Kuru Fasulye",
      name_en: "white bean stew",
      before_area_frac: 0.059,
      after_area_frac: 0.036,
      leftover_ratio: 0.614,
      leftover_pct: 61,
      estimated_leftover_g: 171.9,
      portion_g: 280,
      clip_confidence: 0.99,
    },
    {
      key: "pirinc_pilavi",
      name_tr: "Pirinç Pilavı",
      name_en: "rice pilaf",
      before_area_frac: 0.078,
      after_area_frac: 0.009,
      leftover_ratio: 0.116,
      leftover_pct: 12,
      estimated_leftover_g: 20.9,
      portion_g: 180,
      clip_confidence: 1,
    },
    {
      key: "coban_salata",
      name_tr: "Çoban Salata",
      name_en: "shepherd's salad",
      before_area_frac: 0.048,
      after_area_frac: 0.03,
      leftover_ratio: 0.631,
      leftover_pct: 63,
      estimated_leftover_g: 94.7,
      portion_g: 150,
      clip_confidence: 0.96,
    },
  ],
  matched_items: 4,
  total_estimated_leftover_g: 287.5,
  warnings: [],
  note: "DEMO MODU — önceden hesaplanmış örnek sonuç (kompozit test çifti).",
};

export const DEMO_MENU_KEYS = [
  "mercimek_corbasi",
  "kuru_fasulye",
  "pirinc_pilavi",
  "coban_salata",
];

export const DEMO_OVERLAYS = {
  before: "/demo/before.png",
  after: "/demo/after.png",
};
