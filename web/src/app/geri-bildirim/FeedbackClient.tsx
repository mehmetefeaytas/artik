"use client";

import { useEffect, useState } from "react";
import { useT } from "@/lib/i18n";
import { fetchMenu, postFeedback, REASON_CODES, type MenuItem } from "@/lib/api";

export default function FeedbackClient() {
  const { t } = useT();
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [itemKey, setItemKey] = useState<string>("");
  const [reason, setReason] = useState<string>("");
  const [state, setState] = useState<"idle" | "sending" | "done" | "error">("idle");

  useEffect(() => {
    fetchMenu().then(setMenu).catch(() => {});
  }, []);

  const send = async (code: string) => {
    setReason(code);
    setState("sending");
    try {
      await postFeedback(code, itemKey || undefined);
      setState("done");
    } catch {
      setState("error");
    }
  };

  if (state === "done") {
    return (
      <div className="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center px-4 text-center">
        <div className="grid size-16 place-items-center rounded-2xl bg-tray font-display text-3xl text-well">
          ✓
        </div>
        <h1 className="mt-6 font-display text-2xl font-bold">{t.feedback.thanks}</h1>
        <button
          onClick={() => {
            setState("idle");
            setReason("");
            setItemKey("");
          }}
          className="mt-6 rounded-xl border-2 border-ink/15 px-6 py-3 font-semibold transition-colors hover:border-ink/35"
        >
          {t.feedback.another}
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-10">
      <h1 className="font-display text-3xl font-bold tracking-tight">{t.feedback.title}</h1>
      <p className="mt-2 text-ink/70">{t.feedback.sub}</p>

      <div className="mt-8 space-y-3">
        {REASON_CODES.map((code) => (
          <button
            key={code}
            onClick={() => send(code)}
            disabled={state === "sending"}
            className={`w-full rounded-2xl border-2 px-5 py-5 text-left font-display text-lg font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-tray ${
              reason === code
                ? "border-paprika bg-paprika text-well"
                : "border-ink/12 bg-well hover:border-paprika/50 hover:bg-paprika/5"
            } disabled:opacity-50`}
          >
            {t.feedback.reasons[code as keyof typeof t.feedback.reasons]}
          </button>
        ))}
      </div>

      {state === "error" && (
        <p className="mt-4 rounded-lg bg-paprika/5 p-3 text-sm text-paprika">
          {t.common.error} — {t.common.retry}
        </p>
      )}

      <details className="mt-8">
        <summary className="cursor-pointer text-sm font-medium text-ink/60">
          {t.feedback.pickItem}
        </summary>
        <div className="mt-3 flex flex-wrap gap-2">
          {menu.map((m) => (
            <button
              key={m.key}
              onClick={() => setItemKey(m.key === itemKey ? "" : m.key)}
              className={`rounded-full border px-3 py-1.5 text-sm transition-colors ${
                itemKey === m.key
                  ? "border-tray bg-tray text-well"
                  : "border-ink/15 bg-well text-ink/70 hover:border-ink/35"
              }`}
            >
              {m.name_tr}
            </button>
          ))}
        </div>
      </details>
    </div>
  );
}
