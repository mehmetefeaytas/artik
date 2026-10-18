"use client";

import { useT } from "@/lib/i18n";

export default function Footer() {
  const { t } = useT();
  return (
    <footer className="mt-16 border-t border-ink/10 bg-wellin/40">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-sm text-ink/60">
        <div className="flex items-center gap-2.5">
          <span className="grid size-6 place-items-center rounded-md bg-tray font-display text-sm font-bold text-well">
            A
          </span>
          <span className="font-display font-bold text-ink">{t.footer.tagline}</span>
        </div>
        <p className="font-mono text-xs">
          {t.footer.built} · {t.footer.license}
        </p>
      </div>
    </footer>
  );
}
