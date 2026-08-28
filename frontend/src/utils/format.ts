/** Parse a backend datetime (naive UTC ISO) as a UTC epoch millis timestamp. */
export function parseUtc(iso: string): number {
  // All backend datetimes are UTC but serialized without an offset — append Z.
  return new Date(iso.endsWith("Z") || /[+-]\d\d:\d\d$/.test(iso) ? iso : iso + "Z").getTime();
}

export function formatClock(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}

export function formatDuration(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  const mm = String(m).padStart(2, "0");
  const ss = String(r).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

export function formatDateTime(iso: string): string {
  const d = new Date(parseUtc(iso));
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function formatTimeOnly(iso: string): string {
  const d = new Date(parseUtc(iso));
  return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function experienceLabel(band: string): string {
  return (
    {
      "1-3": "1–3 YEARS",
      "4-7": "4–7 YEARS",
      "8-12": "8–12 YEARS",
      "13-20": "13–20 YEARS",
      "20+": "20+ YEARS",
    }[band] ?? band
  );
}

export function difficultyLabel(d: string): string {
  return (
    {
      hard: "Hard",
      very_hard: "Very Hard",
      expert: "Expert",
    }[d] ?? d
  );
}

export function questionTypeLabel(t: string): string {
  return (
    {
      single: "Single Correct",
      multiple: "Multiple Correct",
      assertion_reason: "Assertion / Reason",
      scenario: "Scenario",
      code: "Code-Based",
      numerical: "Numerical",
      debugging: "Debugging",
    }[t] ?? t
  );
}
