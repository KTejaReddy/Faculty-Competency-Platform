import { CheckCircle2, AlertTriangle, Info, XCircle } from "lucide-react";
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

type Tone = "success" | "error" | "warning" | "info";

interface ToastItem {
  id: number;
  message: string;
  tone: Tone;
}

interface ToastContextValue {
  toast: (message: string, tone?: Tone) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const icons: Record<Tone, ReactNode> = {
  success: <CheckCircle2 className="h-4.5 w-4.5 text-mint-400" />,
  error: <XCircle className="h-4.5 w-4.5 text-rose-400" />,
  warning: <AlertTriangle className="h-4.5 w-4.5 text-amber-400" />,
  info: <Info className="h-4.5 w-4.5 text-brand-300" />,
};

const toneBar: Record<Tone, string> = {
  success: "bg-mint-500",
  error: "bg-rose-500",
  warning: "bg-amber-400",
  info: "bg-brand-500",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const counter = useRef(0);

  const toast = useCallback((message: string, tone: Tone = "info") => {
    const id = ++counter.current;
    setItems((prev) => [...prev, { id, message, tone }]);
    setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 4500);
  }, []);

  const value = useMemo(() => ({ toast }), [toast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-[70] flex w-80 flex-col gap-2">
        {items.map((t) => (
          <div
            key={t.id}
            className="card pointer-events-auto flex items-start gap-3 overflow-hidden bg-ink-850/95 px-4 py-3 shadow-xl"
            style={{ animation: "slideIn 0.18s ease-out" }}
          >
            <span className={`mt-0.5 shrink-0 w-1 self-stretch rounded-full ${toneBar[t.tone]}`} />
            {icons[t.tone]}
            <p className="text-sm text-slate-200">{t.message}</p>
          </div>
        ))}
      </div>
      <style>{`@keyframes slideIn { from { transform: translateX(24px); opacity: 0 } to { transform: translateX(0); opacity: 1 } }`}</style>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx;
}
