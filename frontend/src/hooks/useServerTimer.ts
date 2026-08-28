import { useCallback, useEffect, useRef, useState } from "react";
import { parseUtc } from "../utils/format";

/**
 * Counts down to a server-provided deadline. The client clock is only a display;
 * the deadline is authoritative and can be resynced via sync(serverDeadlineIso).
 */
export function useServerTimer(deadlineIso: string | null) {
  const [remainingMs, setRemainingMs] = useState<number>(() =>
    deadlineIso ? Math.max(0, parseUtc(deadlineIso) - Date.now()) : 0
  );
  const deadlineRef = useRef<number | null>(deadlineIso ? parseUtc(deadlineIso) : null);

  useEffect(() => {
    if (!deadlineRef.current) return;
    const id = window.setInterval(() => {
      setRemainingMs(Math.max(0, deadlineRef.current! - Date.now()));
    }, 250);
    return () => window.clearInterval(id);
  }, []);

  const sync = useCallback((iso: string) => {
    deadlineRef.current = parseUtc(iso);
    setRemainingMs(Math.max(0, deadlineRef.current - Date.now()));
  }, []);

  const seconds = Math.ceil(remainingMs / 1000);
  return {
    seconds,
    expired: remainingMs <= 0,
    sync,
    deadline: deadlineRef.current,
  };
}
