import { useEffect, useState } from "react";
import { AlertTriangle, Gauge, Save } from "lucide-react";
import { api } from "../../services/api";
import { Card, LoadingScreen, Spinner } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import { useToast } from "../../components/Toast";
import { experienceLabel } from "../../utils/format";
import type { ExperienceConfig, ViolationPenalty } from "../../types";

export function AdminConfig() {
  const { toast } = useToast();
  const [penalties, setPenalties] = useState<ViolationPenalty[] | null>(null);
  const [bands, setBands] = useState<ExperienceConfig[] | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get<ViolationPenalty[]>("/api/admin/penalties").then(setPenalties).catch(() => {});
    api.get<ExperienceConfig[]>("/api/admin/experience-configs").then(setBands).catch(() => {});
  }, []);

  if (!penalties || !bands) return <LoadingScreen label="Loading configuration…" />;

  const updatePenalty = (p: ViolationPenalty, penalty: number, enabled: boolean) =>
    setPenalties((prev) => (prev ? prev.map((x) => (x.id === p.id ? { ...x, penalty, enabled } : x)) : prev));

  const updateBand = (b: ExperienceConfig, patch: Partial<Pick<ExperienceConfig, "hard_pct" | "very_hard_pct" | "expert_pct">>) =>
    setBands((prev) => (prev ? prev.map((x) => (x.id === b.id ? { ...x, ...patch } : x)) : prev));

  const saveAll = async () => {
    setBusy(true);
    let failed = false;
    for (const p of penalties) {
      try {
        await api.put(`/api/admin/penalties/${p.id}`, { penalty: p.penalty, description: p.description, enabled: p.enabled });
      } catch {
        failed = true;
      }
    }
    for (const b of bands) {
      const total = b.hard_pct + b.very_hard_pct + b.expert_pct;
      if (total !== 100) {
        toast(`${experienceLabel(b.band)}: percentages must sum to 100 (currently ${total}).`, "error");
        failed = true;
        continue;
      }
      try {
        await api.put(`/api/admin/experience-configs/${b.id}`, {
          hard_pct: b.hard_pct,
          very_hard_pct: b.very_hard_pct,
          expert_pct: b.expert_pct,
        });
      } catch {
        failed = true;
      }
    }
    setBusy(false);
    if (failed) toast("Some settings could not be saved.", "error");
    else toast("Configuration saved.", "success");
  };

  return (
    <div>
      <PageHeader
        title="Security & Configuration"
        subtitle="Violation penalties and per-experience difficulty distributions (applied to new exams)."
        actions={
          <button onClick={saveAll} className="btn-primary" disabled={busy}>
            {busy ? <Spinner /> : <Save className="h-4 w-4" />} Save all changes
          </button>
        }
      />

      <Card className="p-6">
        <h2 className="mb-5 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-300">
          <AlertTriangle className="h-4 w-4 text-rose-400" /> Violation Penalties
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Enabled</th>
                <th className="px-4 py-3">Penalty (marks)</th>
              </tr>
            </thead>
            <tbody>
              {penalties.map((p) => (
                <tr key={p.id} className="border-b border-white/5">
                  <td className="px-4 py-2.5">
                    <span className="font-semibold text-slate-200">{p.type.replace(/_/g, " ")}</span>
                  </td>
                  <td className="px-4 py-2.5">
                    <input
                      type="checkbox"
                      checked={p.enabled}
                      onChange={(e) => updatePenalty(p, p.penalty, e.target.checked)}
                      className="h-4 w-4 accent-brand-500"
                    />
                  </td>
                  <td className="px-4 py-2.5">
                    <input
                      type="number"
                      step={0.5}
                      max={0}
                      value={p.penalty}
                      onChange={(e) => updatePenalty(p, Number(e.target.value), p.enabled)}
                      className="input !w-24 !py-1.5 text-right"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="mt-6 p-6">
        <h2 className="mb-1 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-300">
          <Gauge className="h-4 w-4 text-brand-300" /> Experience Difficulty Distributions
        </h2>
        <p className="mb-5 text-xs text-slate-500">
          Percentage of Hard / Very Hard / Expert questions in a 40-question exam per experience band. Must sum to 100.
        </p>
        <div className="space-y-5">
          {bands.map((b) => {
            const total = b.hard_pct + b.very_hard_pct + b.expert_pct;
            return (
              <div key={b.id}>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-200">{experienceLabel(b.band)}</span>
                  <span className={`text-xs ${total === 100 ? "text-mint-400" : "text-rose-400"}`}>Σ {total}%</span>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <BandField label="Hard" value={b.hard_pct} onChange={(v) => updateBand(b, { hard_pct: v })} />
                  <BandField label="Very Hard" value={b.very_hard_pct} onChange={(v) => updateBand(b, { very_hard_pct: v })} />
                  <BandField label="Expert" value={b.expert_pct} onChange={(v) => updateBand(b, { expert_pct: v })} />
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

function BandField({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  return (
    <div>
      <label className="label !mb-1">{label}</label>
      <input
        type="number"
        min={0}
        max={100}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="input !py-1.5"
      />
    </div>
  );
}
