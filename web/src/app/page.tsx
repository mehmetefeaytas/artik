"use client";

import Link from "next/link";
import { useT } from "@/lib/i18n";
import { Stamp } from "@/components/Badges";

export default function Home() {
  const { t } = useT();

  return (
    <div>
      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 pt-14 pb-10 md:pt-20">
        <p className="mb-4 font-mono text-xs font-medium uppercase tracking-[0.18em] text-tray">
          {t.landing.eyebrow}
        </p>
        <h1 className="max-w-3xl font-display text-4xl font-bold leading-[1.05] tracking-tight md:text-6xl">
          {t.landing.title1}
          <br />
          <span className="text-paprika">{t.landing.title2}</span>
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-ink/70">{t.landing.sub}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/istasyon"
            className="rounded-xl bg-tray px-6 py-3 font-semibold text-well shadow-sm transition-colors hover:bg-traydeep focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-tray"
          >
            {t.landing.ctaStation} →
          </Link>
          <Link
            href="/panel"
            className="rounded-xl border-2 border-ink/15 bg-well px-6 py-3 font-semibold transition-colors hover:border-ink/30 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-tray"
          >
            {t.landing.ctaPanel}
          </Link>
        </div>
      </section>

      {/* Sayı şeridi — tepsi bölmeleri */}
      <section className="mx-auto max-w-6xl px-4 py-8">
        <div className="grid gap-4 rounded-2xl border border-ink/10 bg-well p-4 shadow-sm md:grid-cols-3 md:p-5">
          <StatWell
            value="80,3%"
            label={t.landing.s1}
            note={t.landing.s1note}
          />
          <StatWell
            value="290 Mt"
            label={t.landing.s2}
            note={t.landing.s2note}
          />
          <StatWell
            value="12.3"
            label={t.landing.s3}
            note={t.landing.s3note}
            display
          />
        </div>
      </section>

      {/* Nasıl çalışır — gerçek sıra */}
      <section className="mx-auto max-w-6xl px-4 py-10">
        <h2 className="font-display text-2xl font-bold tracking-tight md:text-3xl">
          {t.landing.howTitle}
        </h2>
        <ol className="mt-6 grid gap-4 md:grid-cols-3">
          {[
            { n: "01", title: t.landing.how1t, desc: t.landing.how1d },
            { n: "02", title: t.landing.how2t, desc: t.landing.how2d },
            { n: "03", title: t.landing.how3t, desc: t.landing.how3d },
          ].map((s) => (
            <li key={s.n} className="rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
              <span className="font-mono text-xs font-semibold tracking-widest text-paprika">
                {s.n}
              </span>
              <h3 className="mt-2 font-display text-lg font-bold">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink/70">{s.desc}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Dürüstlük — imza bölümü */}
      <section className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-2xl bg-ink p-6 text-well md:p-8">
          <h2 className="font-display text-2xl font-bold tracking-tight md:text-3xl">
            {t.landing.honestTitle}
          </h2>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <HonestCard
              badge={<Stamp kind="real" />}
              title={t.landing.h1t}
              desc={t.landing.h1d}
            />
            <HonestCard
              badge={<Stamp kind="estimate" />}
              title={t.landing.h2t}
              desc={t.landing.h2d}
            />
            <HonestCard
              badge={<Stamp kind="scenario" />}
              title={t.landing.h3t}
              desc={t.landing.h3d}
            />
          </div>
          <p className="mt-6 font-mono text-[11px] uppercase tracking-wider text-well/60">
            {t.landing.alignment}
          </p>
        </div>
      </section>
    </div>
  );
}

function StatWell({
  value,
  label,
  note,
  display = false,
}: {
  value: string;
  label: string;
  note: string;
  display?: boolean;
}) {
  return (
    <div className="well p-5">
      <p
        className={`font-display font-bold tracking-tight ${
          display ? "text-3xl md:text-4xl" : "text-4xl md:text-5xl"
        } ${display ? "text-tray" : "text-paprika"}`}
      >
        {value}
      </p>
      <p className="mt-2 text-sm font-medium leading-snug text-ink/80">{label}</p>
      <p className="mt-2 font-mono text-[11px] leading-snug text-ink/50">{note}</p>
    </div>
  );
}

function HonestCard({
  badge,
  title,
  desc,
}: {
  badge: React.ReactNode;
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-xl border border-well/15 bg-well/5 p-5">
      <div className="text-well">{badge}</div>
      <h3 className="mt-3 font-display text-lg font-bold">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-well/70">{desc}</p>
    </div>
  );
}
