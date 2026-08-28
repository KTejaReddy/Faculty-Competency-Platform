export interface User {
  id: number;
  full_name: string;
  department: string;
  role: "faculty" | "admin";
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Department {
  id: number;
  name: string;
  code: string;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  description: string;
  difficulty_label: string;
  active: boolean;
}

export type SubjectStatus = "AVAILABLE" | "IN_PROGRESS" | "COMPLETED" | "LOCKED";

export interface SubjectStatusItem {
  subject: Subject;
  status: SubjectStatus;
  attempt_id: number | null;
  total_questions: number;
  duration_minutes: number;
  question_count: number;
}

export type QuestionType =
  | "single"
  | "multiple"
  | "assertion_reason"
  | "scenario"
  | "code"
  | "numerical"
  | "debugging";

export type Difficulty = "hard" | "very_hard" | "expert";

export interface ExamQuestion {
  position: number;
  question_type: QuestionType;
  question_text: string;
  options: string[];
  marks: number;
}

export interface StartExamResponse {
  attempt_id: number;
  subject_id: number;
  subject_name: string;
  experience_band: string;
  deadline: string;
  server_time: string;
  duration_minutes: number;
  num_questions: number;
  questions: ExamQuestion[];
  resuming: boolean;
}

export interface AttemptStatus {
  attempt_id: number;
  subject_id: number;
  subject_name: string;
  experience_band: string;
  status: string;
  started_at: string;
  deadline: string;
  server_time: string;
  duration_minutes: number;
  num_questions: number;
  last_position: number;
  answered_positions: number[];
  answers: Record<string, number[]>;
  violation_count: number;
  penalty_total: number;
  questions: ExamQuestion[] | null;
}

export interface ViolationSummaryItem {
  type: string;
  count: number;
  penalty_per: number;
  total_penalty: number;
}

export interface SubmitResponse {
  attempt_id: number;
  status: string;
  subject_id: number;
  num_questions: number;
  answered: number;
  violations: ViolationSummaryItem[];
  total_penalty: number;
  time_used_seconds: number;
  score_hidden: boolean;
  subject_locked: boolean;
}

export interface ResultResponse {
  attempt_id: number;
  subject_name: string;
  status: string;
  num_questions: number;
  answered: number;
  violations: ViolationSummaryItem[];
  total_penalty: number;
  time_used_seconds: number;
  score_hidden: boolean;
  subject_locked: boolean;
}

// ---- Admin ----

export interface AdminStats {
  total_faculty: number;
  exams_completed: number;
  exams_pending: number;
  total_subjects: number;
  total_questions: number;
  total_violations: number;
}

export interface Analytics {
  subject_performance: { subject: string; avg_score: number; attempts: number }[];
  violation_distribution: { type: string; count: number }[];
  completion_rate: number;
  average_score: number;
}

export interface FacultyListItem {
  id: number;
  full_name: string;
  department: string;
  subjects_completed: number;
  average_score: number;
  total_violations: number;
  created_at: string;
}

export interface AttemptListItem {
  id: number;
  faculty_name: string;
  department: string;
  subject_name: string;
  experience_band: string;
  status: string;
  started_at: string;
  submitted_at: string | null;
  time_used_seconds: number | null;
  raw_score: number | null;
  penalty_total: number;
  final_score: number | null;
  violation_count: number;
}

export interface AdminQuestion {
  id: number;
  subject_id: number;
  topic_id: number;
  difficulty: Difficulty;
  experience_min: number;
  question_type: QuestionType;
  question_text: string;
  options: string[];
  correct_answer: number[];
  explanation: string;
  active: boolean;
  subject_name: string;
  topic_name: string;
}

export interface QuestionListResponse {
  items: AdminQuestion[];
  total: number;
}

export interface AdminQuestionInput {
  subject_id: number;
  topic_id: number;
  difficulty: string;
  experience_min: number;
  question_type: string;
  question_text: string;
  options: string[];
  correct_answer: number[];
  explanation: string;
}

export interface Topic {
  id: number;
  subject_id: number;
  name: string;
}

export interface ExamConfig {
  id: number;
  subject_id: number;
  num_questions: number;
  duration_minutes: number;
  active: boolean;
}

export interface ExperienceConfig {
  id: number;
  band: string;
  hard_pct: number;
  very_hard_pct: number;
  expert_pct: number;
}

export interface ViolationPenalty {
  id: number;
  type: string;
  label: string;
  penalty: number;
  description: string;
  enabled: boolean;
}

export interface ReportQuestion {
  position: number;
  question_type: string;
  question_text: string;
  difficulty: string;
  topic: string;
  options: string[];
  correct_options: number[];
  chosen_options: number[];
  is_correct: boolean;
  marks_awarded: number;
  explanation: string;
}

export interface ReportViolation {
  id: number;
  type: string;
  timestamp: string;
  duration_seconds: number;
  penalty: number;
  details: Record<string, unknown> | null;
}

export interface AdminExamReport {
  attempt_id: number;
  faculty_name: string;
  department: string;
  subject_name: string;
  experience_band: string;
  status: string;
  started_at: string;
  submitted_at: string | null;
  time_used_seconds: number | null;
  duration_minutes: number;
  num_questions: number;
  answered: number;
  unanswered: number;
  correct: number;
  incorrect: number;
  raw_score: number;
  penalty_total: number;
  final_score: number;
  questions: ReportQuestion[];
  violations: ReportViolation[];
  violation_summary: ViolationSummaryItem[];
  recording: {
    attempt_id: number;
    status: string;
    mime_type: string;
    segment_count: number;
    duration_seconds: number;
    started_at: string | null;
    ended_at: string | null;
    url: string;
  } | null;
}

export interface PlaylistResponse {
  mode: "single" | "segments";
  mime_type: string;
  duration: number;
  url?: string;
  segments?: { index: number; duration: number; url: string }[];
}
