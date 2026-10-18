"use client";

import { useT } from "@/lib/i18n";
import { Stamp } from "@/components/Badges";

export default function MethodPage() {
  const { t } = useT();
  const m = t.method;

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="font-display text-3xl font-bold tracking-tight md:text-4xl">{m.title}</h1>
      <p className="mt-2 text-ink/70">{m.sub}</p>

      <Section title={m.mTitle}>
        <Row badge="estimate" title={m.m1t} desc={m.m1d} />
        <Row badge="estimate" title={m.m2t} desc={m.m2d} />
        <Row badge="estimate" title={m.m3t} desc={m.m3d} />
        <Row badge="estimate" title={m.m4t} desc={m.m4d} />
      </Section>

      <Section title={m.vTitle}>
        <ul className="space-y-3">
          {[m.v1, m.v2, m.v3].map((v, i) => (
            <li key={i} className="flex gap-3 rounded-xl border border-ink/10 bg-well p-4 shadow-sm">
              <span className="font-mono text-xs font-bold text-tray">V{i + 1}</span>
              <p className="text-sm leading-relaxed text-ink/75">{v}</p>
            </li>
          ))}
        </ul>
      </Section>

      <Section title={m.sTitle}>
        <div className="space-y-2">
          {[m.s1, m.s2, m.s3].map((s, i) => (
            <p key={i} className="rounded-lg bg-wellin/60 p-3 font-mono text-xs leading-relaxed text-ink/70">
              {s}
            </p>
          ))}
        </div>
      </Section>

      <Section title={m.lTitle}>
        <ul className="space-y-2 text-sm leading-relaxed text-ink/75">
          <li>· {m.l1}</li>
          <li>· {m.l2}</li>
          <li>· {m.l3}</li>
        </ul>
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="font-display text-xl font-bold">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function Row({
  badge,
  title,
  desc,
}: {
  badge: "scenario" | "estimate" | "simulation" | "real";
  title: string;
  desc: string;
}) {
  return (
    <div className="mb-3 rounded-xl border border-ink/10 bg-well p-4 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="font-display font-bold">{title}</h3>
        <Stamp kind={badge} />
      </div>
      <p className="mt-2 text-sm leading-relaxed text-ink/70">{desc}</p>
    </div>
  );
}
