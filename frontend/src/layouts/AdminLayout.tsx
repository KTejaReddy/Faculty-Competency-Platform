import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BookOpenCheck,
  FileQuestion,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Settings2,
  ShieldCheck,
  Users,
  Building2,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";

const NAV = [
  { to: "/admin", label: "Dashboard", icon: <LayoutDashboard className="h-4.5 w-4.5" />, end: true },
  { to: "/admin/faculty", label: "Faculty", icon: <Users className="h-4.5 w-4.5" />, end: false },
  { to: "/admin/questions", label: "Question Bank", icon: <FileQuestion className="h-4.5 w-4.5" />, end: false },
  { to: "/admin/subjects", label: "Subjects", icon: <BookOpenCheck className="h-4.5 w-4.5" />, end: false },
  { to: "/admin/departments", label: "Departments", icon: <Building2 className="h-4.5 w-4.5" />, end: false },
  { to: "/admin/config", label: "Security & Config", icon: <Settings2 className="h-4.5 w-4.5" />, end: false },
];

export function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-white/5 bg-ink-900/60 backdrop-blur-xl">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-ink-700 to-ink-800 ring-1 ring-white/15">
            <ShieldCheck className="h-5 w-5 text-brand-300" />
          </div>
          <div>
            <p className="text-xs font-bold tracking-wide text-slate-100">ADMIN</p>
            <p className="text-[10px] text-slate-500">Control Panel</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-2">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-500/15 text-brand-200 ring-1 ring-brand-500/25"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                }`
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/5 px-5 py-4">
          <p className="truncate text-xs font-semibold text-slate-200">{user?.full_name}</p>
          <button
            onClick={() => {
              logout();
              navigate("/admin/login");
            }}
            className="mt-2 flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300"
          >
            <LogOut className="h-3.5 w-3.5" /> Sign out
          </button>
        </div>
      </aside>

      <main className="ml-60 flex-1 px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: React.ReactNode }) {
  return (
    <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="flex items-center gap-2.5 text-2xl font-extrabold tracking-tight text-slate-50">
          <GraduationCap className="h-6 w-6 text-brand-300" />
          {title}
        </h1>
        {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
      </div>
      {actions}
    </div>
  );
}
