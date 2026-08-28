import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "./hooks/useAuth";
import { Landing } from "./pages/Landing";
import { FacultyLogin } from "./pages/FacultyLogin";
import { FacultyRegister } from "./pages/FacultyRegister";
import { AdminLogin } from "./pages/AdminLogin";
import { FacultyDashboard } from "./pages/FacultyDashboard";
import { ExamStart } from "./pages/ExamStart";
import { CameraCheck } from "./pages/CameraCheck";
import { ExamPage } from "./pages/ExamPage";
import { ExamComplete } from "./pages/ExamComplete";
import { AdminLayout } from "./layouts/AdminLayout";
import { AdminDashboard } from "./pages/admin/AdminDashboard";
import { AdminFaculty } from "./pages/admin/AdminFaculty";
import { AdminFacultyDetail } from "./pages/admin/AdminFacultyDetail";
import { AdminReport } from "./pages/admin/AdminReport";
import { AdminQuestions } from "./pages/admin/AdminQuestions";
import { AdminQuestionEditor } from "./pages/admin/AdminQuestionEditor";
import { AdminSubjects } from "./pages/admin/AdminSubjects";
import { AdminDepartments } from "./pages/admin/AdminDepartments";
import { AdminConfig } from "./pages/admin/AdminConfig";
import { NotFound } from "./pages/NotFound";

function RequireRole({ role, children }: { role: "faculty" | "admin"; children: ReactNode }) {
  const { user } = useAuth();
  if (!user) return <Navigate to={role === "admin" ? "/admin/login" : "/login"} replace />;
  if (user.role !== role) {
    return <Navigate to={user.role === "admin" ? "/admin" : "/dashboard"} replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<FacultyLogin />} />
      <Route path="/register" element={<FacultyRegister />} />
      <Route path="/admin/login" element={<AdminLogin />} />

      <Route
        path="/dashboard"
        element={
          <RequireRole role="faculty">
            <FacultyDashboard />
          </RequireRole>
        }
      />
      <Route
        path="/subjects/:subjectId/start"
        element={
          <RequireRole role="faculty">
            <ExamStart />
          </RequireRole>
        }
      />
      <Route
        path="/subjects/:subjectId/verify"
        element={
          <RequireRole role="faculty">
            <CameraCheck />
          </RequireRole>
        }
      />
      <Route
        path="/exam"
        element={
          <RequireRole role="faculty">
            <ExamPage />
          </RequireRole>
        }
      />
      <Route
        path="/exam/complete"
        element={
          <RequireRole role="faculty">
            <ExamComplete />
          </RequireRole>
        }
      />

      <Route
        path="/admin"
        element={
          <RequireRole role="admin">
            <AdminLayout />
          </RequireRole>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="faculty" element={<AdminFaculty />} />
        <Route path="faculty/:id" element={<AdminFacultyDetail />} />
        <Route path="attempts/:id" element={<AdminReport />} />
        <Route path="questions" element={<AdminQuestions />} />
        <Route path="questions/new" element={<AdminQuestionEditor />} />
        <Route path="questions/:id/edit" element={<AdminQuestionEditor />} />
        <Route path="subjects" element={<AdminSubjects />} />
        <Route path="departments" element={<AdminDepartments />} />
        <Route path="config" element={<AdminConfig />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
