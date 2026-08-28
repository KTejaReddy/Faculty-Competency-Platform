/**
 * Browser-level anti-cheating monitor.
 *
 * Detects and reports: TAB_SWITCH, FOCUS_LOSS, COPY/PASTE/CUT_ATTEMPT,
 * CONTEXT_MENU, PRINT_ATTEMPT, KEYBOARD_SHORTCUT. Fullscreen exits and camera
 * conditions are reported by the exam page via report().
 *
 * Honest limitation: a browser cannot prevent phones, external cameras or
 * OS-level capture; this provides strong monitoring, logging and deterrence.
 */

export type ViolationType =
  | "TAB_SWITCH"
  | "FOCUS_LOSS"
  | "COPY_ATTEMPT"
  | "PASTE_ATTEMPT"
  | "CUT_ATTEMPT"
  | "CONTEXT_MENU"
  | "PRINT_ATTEMPT"
  | "KEYBOARD_SHORTCUT"
  | "FULLSCREEN_EXIT"
  | "CAMERA_OBSTRUCTED"
  | "CAMERA_TOO_DARK"
  | "CAMERA_TOO_BRIGHT"
  | "CAMERA_DISCONNECTED"
  | "CAMERA_PERMISSION_LOST";

export interface ViolationEvent {
  type: ViolationType;
  duration: number;
  metadata: Record<string, unknown>;
}

type Handler = (event: ViolationEvent) => void;

const THROTTLE_MS: Partial<Record<ViolationType, number>> = {
  TAB_SWITCH: 800,
  FOCUS_LOSS: 1500,
  COPY_ATTEMPT: 2500,
  PASTE_ATTEMPT: 2500,
  CUT_ATTEMPT: 2500,
  CONTEXT_MENU: 2500,
  PRINT_ATTEMPT: 2500,
  KEYBOARD_SHORTCUT: 2500,
};

export class ViolationMonitor {
  private handlers: Handler[] = [];
  private lastReported: Partial<Record<ViolationType, number>> = {};
  private hiddenSince: number | null = null;
  private attached = false;

  onViolation(handler: Handler): () => void {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter((h) => h !== handler);
    };
  }

  report(type: ViolationType, duration = 0, metadata: Record<string, unknown> = {}): void {
    const now = Date.now();
    const minGap = THROTTLE_MS[type] ?? 1000;
    if (now - (this.lastReported[type] ?? 0) < minGap) return;
    this.lastReported[type] = now;
    for (const h of this.handlers) h({ type, duration, metadata });
  }

  attach(): void {
    if (this.attached) return;
    this.attached = true;

    document.addEventListener("visibilitychange", this.onVisibility);
    window.addEventListener("blur", this.onBlur);
    document.addEventListener("copy", this.onCopy);
    document.addEventListener("cut", this.onCut);
    document.addEventListener("paste", this.onPaste);
    document.addEventListener("contextmenu", this.onContextMenu);
    window.addEventListener("beforeprint", this.onPrint);
    document.addEventListener("keydown", this.onKeyDown);
    window.addEventListener("mousedown", this.onMouseDown);
  }

  detach(): void {
    if (!this.attached) return;
    this.attached = false;
    document.removeEventListener("visibilitychange", this.onVisibility);
    window.removeEventListener("blur", this.onBlur);
    document.removeEventListener("copy", this.onCopy);
    document.removeEventListener("cut", this.onCut);
    document.removeEventListener("paste", this.onPaste);
    document.removeEventListener("contextmenu", this.onContextMenu);
    window.removeEventListener("beforeprint", this.onPrint);
    document.removeEventListener("keydown", this.onKeyDown);
    window.removeEventListener("mousedown", this.onMouseDown);
  }

  private onVisibility = (): void => {
    if (document.hidden) {
      this.hiddenSince = Date.now();
      this.report("TAB_SWITCH", 0, { state: "hidden" });
    } else if (this.hiddenSince !== null) {
      const duration = (Date.now() - this.hiddenSince) / 1000;
      this.hiddenSince = null;
      this.report("TAB_SWITCH", duration, { state: "visible", returned: true });
    }
  };

  private onBlur = (): void => {
    if (!document.hidden) {
      this.report("FOCUS_LOSS", 0, {});
    }
  };

  private onCopy = (e: ClipboardEvent): void => {
    e.preventDefault();
    this.report("COPY_ATTEMPT", 0, {});
  };

  private onCut = (e: ClipboardEvent): void => {
    e.preventDefault();
    this.report("CUT_ATTEMPT", 0, {});
  };

  private onPaste = (e: ClipboardEvent): void => {
    e.preventDefault();
    this.report("PASTE_ATTEMPT", 0, {});
  };

  private onContextMenu = (e: MouseEvent): void => {
    e.preventDefault();
    this.report("CONTEXT_MENU", 0, {});
  };

  private onPrint = (): void => {
    this.report("PRINT_ATTEMPT", 0, {});
  };

  private onMouseDown = (e: MouseEvent): void => {
    if (e.button === 2) {
      // context menu handled by onContextMenu; nothing extra needed
    }
  };

  private onKeyDown = (e: KeyboardEvent): void => {
    const key = e.key.toLowerCase();
    const ctrl = e.ctrlKey || e.metaKey;
    const shift = e.shiftKey;
    const blocked =
      e.key === "F12" ||
      (ctrl && ["p", "s", "u"].includes(key)) ||
      (ctrl && shift && ["i", "j", "c"].includes(key)) ||
      (e.key === "PrintScreen");
    if (blocked) {
      e.preventDefault();
      this.report("KEYBOARD_SHORTCUT", 0, { key: e.key, ctrl, shift });
    }
  };
}
