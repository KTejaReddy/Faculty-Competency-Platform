import { useEffect, useState, type FormEvent } from "react";
import { Building2, Plus } from "lucide-react";
import { api } from "../../services/api";
import { Card, EmptyState, LoadingScreen, Modal, Spinner } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import { useToast } from "../../components/Toast";
import type { Department } from "../../types";

export function AdminDepartments() {
  const [departments, setDepartments] = useState<Department[] | null>(null);
  const [open, setOpen] = useState(false);

  const load = () => api.get<Department[]>("/api/admin/departments").then(setDepartments).catch(() => {});

  useEffect(() => {
    void load();
  }, []);

  if (!departments) return <LoadingScreen label="Loading departments…" />;

  return (
    <div>
      <PageHeader
        title="Departments"
        subtitle="Departments available to faculty during registration."
        actions={
          <button onClick={() => setOpen(true)} className="btn-primary">
            <Plus className="h-4 w-4" /> Add Department
          </button>
        }
      />
      {departments.length === 0 ? (
        <EmptyState icon={<Building2 className="h-6 w-6" />} title="No departments" />
      ) : (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3.5">Department</th>
                <th className="px-5 py-3.5">Code</th>
              </tr>
            </thead>
            <tbody>
              {departments.map((d) => (
                <tr key={d.id} className="border-b border-white/5">
                  <td className="px-5 py-3.5 font-semibold text-slate-100">{d.name}</td>
                  <td className="px-5 py-3.5">
                    <span className="chip text-brand-300">{d.code}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {open && <CreateDepartmentModal onClose={() => setOpen(false)} onCreated={() => { setOpen(false); load(); }} />}
    </div>
  );
}

function CreateDepartmentModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const { toast } = useToast();

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post("/api/admin/departments", { name: name.trim().toUpperCase(), code: code.trim().toUpperCase() });
      toast("Department added.", "success");
      onCreated();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Create failed.", "error");
      setBusy(false);
    }
  };

  return (
    <Modal open onClose={onClose} title="Add Department">
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="label">Department Name</label>
          <input className="input uppercase" value={name} onChange={(e) => setName(e.target.value)} placeholder="BIOTECHNOLOGY" />
        </div>
        <div>
          <label className="label">Code</label>
          <input className="input uppercase" value={code} onChange={(e) => setCode(e.target.value)} placeholder="BT" />
        </div>
        <div className="flex justify-end gap-3">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" disabled={busy}>
            {busy ? <Spinner /> : <Plus className="h-4 w-4" />} Create
          </button>
        </div>
      </form>
    </Modal>
  );
}
