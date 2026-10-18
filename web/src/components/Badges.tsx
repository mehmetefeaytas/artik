"use client";

import { useT } from "@/lib/i18n";

type StampKind = "scenario" | "estimate" | "simulation" | "real";

const styles: Record<StampKind, string> = {
  scenario: "text-paprika bg-paprika/5",
  estimate: "text-traydeep bg-tray/5",
  simulation: "text-[#7a5a00] bg-[#7a5a00]/5",
  real: "text-traydeep border-traydeep/40 bg-tray/10",
};

export function Stamp({ kind }: { kind: StampKind }) {
  const { t } = useT();
  const labels: Record<StampKind, string> = {
    scenario: t.common.scenario,
    estimate: t.common.estimate,
    simulation: t.common.simulation,
    real: t.common.real,
  };
  return <span className={`stamp ${styles[kind]}`}>{labels[kind]}</span>;
}
