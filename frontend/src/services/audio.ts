/**
 * Warning buzzer. Browser autoplay policies block audio before a user gesture,
 * so unlockAudio() must be called from a click handler before any tone plays.
 */

let ctx: AudioContext | null = null;
let continuousNodes: { osc: OscillatorNode; gain: GainNode }[] = [];

export function unlockAudio(): void {
  try {
    if (!ctx) {
      const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!AC) return;
      ctx = new AC();
    }
    if (ctx.state === "suspended") void ctx.resume();
  } catch {
    /* audio unavailable — visual warnings still work */
  }
}

export function beep(freq = 880, durationMs = 180, volume = 0.06): void {
  if (!ctx || ctx.state !== "running") return;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "square";
  osc.frequency.value = freq;
  gain.gain.value = volume;
  osc.connect(gain).connect(ctx.destination);
  const now = ctx.currentTime;
  gain.gain.setValueAtTime(volume, now);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + durationMs / 1000);
  osc.start(now);
  osc.stop(now + durationMs / 1000);
}

/** Continuous warning tone (used while a critical camera condition persists). */
export function startContinuousTone(): void {
  if (!ctx || ctx.state !== "running" || continuousNodes.length > 0) return;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sawtooth";
  osc.frequency.value = 440;
  gain.gain.value = 0.045;
  osc.connect(gain).connect(ctx.destination);
  osc.start();
  continuousNodes.push({ osc, gain });
}

export function stopContinuousTone(): void {
  for (const { osc, gain } of continuousNodes) {
    try {
      gain.gain.setValueAtTime(gain.gain.value, ctx!.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx!.currentTime + 0.15);
      osc.stop(ctx!.currentTime + 0.2);
    } catch {
      /* ignore */
    }
  }
  continuousNodes = [];
}
