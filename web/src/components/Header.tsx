"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useT } from "@/lib/i18n";

const links = [
  { href: "/istasyon", key: "station" },
  { href: "/panel", key: "panel" },
  { href: "/geri-bildirim", key: "feedback" },
  { href: "/yontem", key: "method" },
] as const;

export default function Header() {
  const { t, lang, setLang } = useT();
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-ink/10 bg-porcelain/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4">
        <Link href="/" className="flex items-center gap-2.5" aria-label="ARTIK ana sayfa">
          <span className="grid size-8 place-items-center rounded-lg bg-tray font-display text-lg font-bold text-well">
            A
          </span>
          <span className="font-display text-xl font-bold tracking-tight">ARTIK</span>
        </Link>
        <nav className="ml-auto flex items-center gap-1 overflow-x-auto text-sm font-medium">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`rounded-lg px-3 py-1.5 whitespace-nowrap transition-colors ${
                pathname === l.href
                  ? "bg-tray/10 text-traydeep font-semibold"
                  : "text-ink/70 hover:bg-ink/5 hover:text-ink"
              }`}
            >
              {t.nav[l.key]}
            </Link>
          ))}
        </nav>
        <div className="flex shrink-0 items-center rounded-lg border border-ink/15 p-0.5 font-mono text-xs font-semibold">
          {(["tr", "en"] as const).map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={`rounded-md px-2 py-1 uppercase transition-colors ${
                lang === l ? "bg-ink text-well" : "text-ink/60 hover:text-ink"
              }`}
              aria-pressed={lang === l}
            >
              {l}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
