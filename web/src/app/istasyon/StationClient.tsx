"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useT } from "@/lib/i18n";
import {
  analyzePair,
  checkHealth,
  fetchMenu,
  type AnalyzeResult,
  type MenuItem,
} from "@/lib/api";
import { DEMO_MENU, DEMO_MENU_KEYS, DEMO_OVERLAYS, DEMO_PHOTOS, DEMO_RESULT } from "@/lib/demoResult";
import { Stamp } from "@/components/Badges";

type SlotKey = "before" | "after";

const CATEGORIES: Record<string, string> = {
  corba: "Çorbalar",
  ana: "Ana Yemek",
  garnitur: "Garnitür",
  yan: "Yan Ürün",
  tatli: "Tatlı",
};

export default function StationClient() {
  const { t } = useT();
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [menuError, setMenuError] = useState(false);
  const [slots, setSlots] = useState<Record<SlotKey, { blob: Blob; url: string } | null>>({
    before: null,
    after: null,
  });
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [save, setSave] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMenu()
      .then(setMenu)
      .catch(() => setMenuError(true));
  }, []);

  const toggle = (key: string) => {
    setSelected((prev) =>
      prev.includes(key)
        ? prev.filter((k) => k !== key)
        : prev.length >= 6
          ? prev
          : [...prev, key]
    );
  };

  const injectDemoMenu = () => {
    setMenu((prev) => {
      const keys = new Set(prev.map((m) => m.key));
      const extras = DEMO_MENU.filter((m) => !keys.has(m.key));
      return [...extras, ...prev];
    });
  };

  const quickDemo = () => {
    injectDemoMenu();
    setSelected(DEMO_MENU_KEYS);
  };

  const useDemoPair = async () => {
    const load = async (path: string) => {
      const res = await fetch(path);
      return res.blob();
    };
    try {
      const [b, a] = await Promise.all([load(DEMO_PHOTOS.before), load(DEMO_PHOTOS.after)]);
      setSlots({
        before: { blob: b, url: DEMO_PHOTOS.before },
        after: { blob: a, url: DEMO_PHOTOS.after },
      });
      injectDemoMenu();
      setSelected(DEMO_MENU_KEYS);
    } catch {
      setError(t.common.error);
    }
  };

  const runAnalysis = async () => {
    setError("");
    setResult(null);
    setAnalyzing(true);
    try {
      const ok = await checkHealth();
      if (!ok) throw new Error("API_DOWN");
      const items = menu.filter((m) => selected.includes(m.key));
      const res = await analyzePair(slots.before!.blob, slots.after!.blob, items, save);
      setResult(res);
      setDemoMode(false);
    } catch (e) {
      if (e instanceof Error && e.message.includes("API_DOWN")) {
        setResult(DEMO_RESULT);
        setDemoMode(true);
      } else {
        setError(e instanceof Error ? e.message : t.common.error);
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const canAnalyze = slots.before && slots.after && selected.length > 0 && !analyzing;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
          {t.station.title}
        </h1>
        <p className="mt-2 max-w-2xl text-ink/70">{t.station.sub}</p>
      </header>

      {/* 1 · Menü */}
      <section className="rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="font-display text-lg font-bold">{t.station.step1}</h2>
          <button
            onClick={quickDemo}
            className="rounded-lg border border-tray/30 bg-tray/5 px-3 py-1.5 text-sm font-medium text-traydeep transition-colors hover:bg-tray/10"
          >
            {t.station.quickDemo}
          </button>
        </div>
        <p className="mt-1 text-sm text-ink/60">{t.station.step1hint}</p>
        {menuError ? (
          <p className="mt-4 rounded-lg bg-paprika/5 p-3 text-sm text-paprika">
            {t.station.apiDown}
          </p>
        ) : menu.length === 0 ? (
          <p className="mt-4 text-sm text-ink/50">{t.common.loading}</p>
        ) : (
          <div className="mt-4 space-y-3">
            {Object.entries(CATEGORIES).map(([cat, label]) => {
              const items = menu.filter((m) => m.category === cat);
              if (!items.length) return null;
              return (
                <div key={cat}>
                  <p className="mb-1.5 font-mono text-[11px] font-semibold uppercase tracking-wider text-ink/50">
                    {label}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {items.map((m) => {
                      const on = selected.includes(m.key);
                      return (
                        <button
                          key={m.key}
                          onClick={() => toggle(m.key)}
                          aria-pressed={on}
                          className={`rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                            on
                              ? "border-tray bg-tray text-well"
                              : "border-ink/15 bg-well text-ink/75 hover:border-ink/35"
                          }`}
                        >
                          {m.name_tr}
                          <span className={`ml-1.5 font-mono text-[11px] ${on ? "text-well/70" : "text-ink/40"}`}>
                            {m.portion_g}g
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* 2 · Fotoğraflar */}
      <section className="mt-6 rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
        <h2 className="font-display text-lg font-bold">{t.station.step2}</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <PhotoSlot
            label={t.station.before}
            hint="01"
            photo={slots.before}
            onSet={(p) => setSlots((s) => ({ ...s, before: p }))}
            onClear={() => setSlots((s) => ({ ...s, before: null }))}
          />
          <PhotoSlot
            label={t.station.after}
            hint="02"
            photo={slots.after}
            onSet={(p) => setSlots((s) => ({ ...s, after: p }))}
            onClear={() => setSlots((s) => ({ ...s, after: null }))}
          />
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            onClick={useDemoPair}
            className="rounded-lg border border-ink/15 px-3 py-1.5 text-sm font-medium text-ink/70 transition-colors hover:border-ink/35 hover:text-ink"
          >
            {t.station.useDemoPair}
          </button>
          <span className="font-mono text-[11px] text-ink/45">{t.station.demoPairNote}</span>
        </div>
      </section>

      {/* 3 · Analiz */}
      <section className="mt-6 rounded-2xl border border-ink/10 bg-well p-5 shadow-sm">
        <h2 className="font-display text-lg font-bold">{t.station.step3}</h2>
        <div className="mt-4 flex flex-wrap items-center gap-4">
          <button
            onClick={runAnalysis}
            disabled={!canAnalyze}
            className="rounded-xl bg-paprika px-6 py-3 font-semibold text-well shadow-sm transition-colors hover:bg-[#a53a17] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-paprika disabled:cursor-not-allowed disabled:opacity-40"
          >
            {analyzing ? t.station.analyzing : t.station.analyze}
          </button>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-ink/70">
            <input
              type="checkbox"
              checked={save}
              onChange={(e) => setSave(e.target.checked)}
              className="size-4 accent-[#2f6b4f]"
            />
            {t.station.saveLabel}
          </label>
        </div>
        {analyzing && (
          <div className="mt-4">
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-wellin">
              <div className="h-full w-1/3 animate-pulse rounded-full bg-paprika" />
            </div>
            <p className="mt-2 text-sm text-ink/60">{t.station.analyzingHint}</p>
          </div>
        )}
        {error && (
          <p className="mt-4 rounded-lg bg-paprika/5 p-3 font-mono text-xs text-paprika">
            {error}
          </p>
        )}
      </section>

      {/* Sonuç */}
      {result && (
        <section className="mt-6 space-y-4">
          {demoMode && (
            <p className="rounded-xl border border-paprika/25 bg-paprika/5 p-3 text-sm text-paprika">
              {t.station.apiDown}
            </p>
          )}
          <ResultView result={result} demoMode={demoMode} onReset={() => setResult(null)} />
        </section>
      )}
    </div>
  );
}

function PhotoSlot({
  label,
  hint,
  photo,
  onSet,
  onClear,
}: {
  label: string;
  hint: string;
  photo: { blob: Blob; url: string } | null;
  onSet: (p: { blob: Blob; url: string }) => void;
  onClear: () => void;
}) {
  const { t } = useT();
  const [camOpen, setCamOpen] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const setFile = (f: File | undefined) => {
    if (f) onSet({ blob: f, url: URL.createObjectURL(f) });
  };

  return (
    <div className="well flex min-h-44 flex-col p-4">
      <div className="flex items-center justify-between">
        <p className="font-mono text-[11px] font-semibold uppercase tracking-widest text-ink/50">
          {hint} · {label}
        </p>
        {photo && (
          <button
            onClick={onClear}
            className="text-xs font-medium text-ink/50 underline hover:text-ink"
          >
            ✕
          </button>
        )}
      </div>
      {photo ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={photo.url}
          alt={label}
          className="mt-3 max-h-64 w-full rounded-lg object-cover"
        />
      ) : (
        <div className="mt-3 flex flex-1 flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-ink/15 py-8">
          <div className="flex gap-2">
            <button
              onClick={() => fileRef.current?.click()}
              className="rounded-lg bg-tray px-4 py-2 text-sm font-semibold text-well transition-colors hover:bg-traydeep"
            >
              {t.station.upload}
            </button>
            <button
              onClick={() => setCamOpen(true)}
              className="rounded-lg border border-ink/20 px-4 py-2 text-sm font-semibold text-ink/75 transition-colors hover:border-ink/40"
            >
              {t.station.camera}
            </button>
          </div>
        </div>
      )}
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => setFile(e.target.files?.[0])}
      />
      {camOpen && (
        <CameraModal
          onClose={() => setCamOpen(false)}
          onShot={(blob) => {
            onSet({ blob, url: URL.createObjectURL(blob) });
            setCamOpen(false);
          }}
        />
      )}
    </div>
  );
}

function CameraModal({
  onClose,
  onShot,
}: {
  onClose: () => void;
  onShot: (b: Blob) => void;
}) {
  const { t } = useT();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [err, setErr] = useState("");

  const shoot = useCallback(() => {
    const v = videoRef.current;
    if (!v) return;
    const c = document.createElement("canvas");
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    c.getContext("2d")?.drawImage(v, 0, 0);
    c.toBlob((b) => b && onShot(b), "image/jpeg", 0.92);
  }, [onShot]);

  useEffect(() => {
    let stream: MediaStream | null = null;
    navigator.mediaDevices
      ?.getUserMedia({ video: { facingMode: "environment", width: 1280 } })
      .then((s) => {
        stream = s;
        if (videoRef.current) {
          videoRef.current.srcObject = s;
          videoRef.current.play();
        }
      })
      .catch(() => setErr(t.common.error));
    return () => stream?.getTracks().forEach((tr) => tr.stop());
  }, [t.common.error]);

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ink/70 p-4" role="dialog">
      <div className="w-full max-w-lg rounded-2xl bg-well p-4 shadow-xl">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-ink/60">{t.station.cameraHint}</p>
          <button onClick={onClose} className="text-sm font-medium text-ink/60 hover:text-ink">
            {t.station.close}
          </button>
        </div>
        {err ? (
          <p className="mt-4 rounded-lg bg-paprika/5 p-3 text-sm text-paprika">{err}</p>
        ) : (
          <video ref={videoRef} className="mt-3 w-full rounded-xl bg-ink" playsInline muted />
        )}
        <button
          onClick={shoot}
          disabled={!!err}
          className="mt-4 w-full rounded-xl bg-paprika px-4 py-3 font-semibold text-well transition-colors hover:bg-[#a53a17] disabled:opacity-40"
        >
          {t.station.capture}
        </button>
      </div>
    </div>
  );
}

function ResultView({
  result,
  demoMode,
  onReset,
}: {
  result: AnalyzeResult;
  demoMode: boolean;
  onReset: () => void;
}) {
  const { t } = useT();
  const beforeSrc = result.annotated_before_b64
    ? `data:image/png;base64,${result.annotated_before_b64}`
    : DEMO_OVERLAYS.before;
  const afterSrc = result.annotated_after_b64
    ? `data:image/png;base64,${result.annotated_after_b64}`
    : DEMO_OVERLAYS.after;

  return (
    <div className="maskpop space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="font-display text-2xl font-bold">{t.station.resultTitle}</h2>
        <Stamp kind="estimate" />
        {demoMode && <Stamp kind="scenario" />}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {[
          { src: beforeSrc, label: t.station.before },
          { src: afterSrc, label: t.station.after },
        ].map((im) => (
          <figure key={im.label} className="rounded-2xl border border-ink/10 bg-well p-3 shadow-sm">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={im.src} alt={im.label} className="w-full rounded-lg" />
            <figcaption className="mt-2 font-mono text-[11px] uppercase tracking-wider text-ink/50">
              {im.label}
            </figcaption>
          </figure>
        ))}
      </div>

      {result.items.length === 0 ? (
        <p className="rounded-xl bg-paprika/5 p-4 text-sm text-paprika">{t.station.noItems}</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {result.items.map((it) => {
            const eaten = 100 - it.leftover_pct;
            return (
              <div key={it.key} className="rounded-2xl border border-ink/10 bg-well p-4 shadow-sm">
                <div className="flex items-baseline justify-between gap-2">
                  <h3 className="font-display font-bold">{it.name_tr}</h3>
                  <span className="font-mono text-xs text-ink/50">
                    conf {it.clip_confidence.toFixed(2)}
                  </span>
                </div>
                <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-wellin">
                  <div
                    className="h-full rounded-full bg-tray"
                    style={{ width: `${Math.min(eaten, 100)}%` }}
                  />
                </div>
                <div className="mt-2 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 text-sm">
                  <span className="text-traydeep">
                    <strong className="font-mono">%{eaten}</strong> {t.station.eaten}
                  </span>
                  <span className="text-paprika">
                    <strong className="font-mono">%{it.leftover_pct}</strong> {t.station.left}
                  </span>
                </div>
                <p className="mt-3 flex items-center gap-2 font-mono text-xs text-ink/60">
                  {t.station.estLeftover}:{" "}
                  <strong className="text-ink">
                    {it.estimated_leftover_g?.toFixed(0) ?? "—"} {t.common.g}
                  </strong>
                  <Stamp kind="estimate" />
                  <span className="text-ink/40">
                    / {it.portion_g} {t.common.g} {t.station.portionDefault}
                  </span>
                </p>
              </div>
            );
          })}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3 rounded-2xl bg-ink p-4 text-well">
        <p className="font-display text-lg font-bold">
          {t.common.total}:{" "}
          <span className="font-mono text-paprika">
            {result.total_estimated_leftover_g.toFixed(0)} {t.common.g}
          </span>
        </p>
        <Stamp kind="estimate" />
        <span className="text-sm text-well/60">{result.note}</span>
        <button
          onClick={onReset}
          className="ml-auto rounded-lg border border-well/25 px-3 py-1.5 text-sm font-medium hover:bg-well/10"
        >
          {t.station.fresh}
        </button>
      </div>

      {result.warnings.length > 0 && (
        <div className="rounded-2xl border border-paprika/25 bg-paprika/5 p-4">
          <p className="font-semibold text-paprika">{t.station.warnings}</p>
          <ul className="mt-2 list-inside list-disc text-sm text-ink/70">
            {result.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
