export const STATUSES = [
  "saved",
  "applied",
  "assessment",
  "interview",
  "offer",
  "rejected",
] as const;

export type ApplicationStatus = (typeof STATUSES)[number];

export interface JobApplication {
  id: number;
  company: string;
  role: string;
  location: string | null;
  status: ApplicationStatus;
  salary: string | null;
  job_url: string | null;
  deadline: string | null;
  notes: string | null;
  job_description: string | null;
  match_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  company: string;
  role: string;
  location?: string;
  status: ApplicationStatus;
  salary?: string;
  job_url?: string;
  deadline?: string;
  notes?: string;
}

export interface ApplicationUpdate {
  company?: string;
  role?: string;
  location?: string | null;
  status?: ApplicationStatus;
  salary?: string | null;
  job_url?: string | null;
  deadline?: string | null;
  notes?: string | null;
  job_description?: string | null;
  match_score?: number | null;
}

export interface Activity {
  id: number;
  application_id: number;
  event_type: "created" | "status_changed" | "details_updated" | string;
  description: string;
  old_value: string | null;
  new_value: string | null;
  created_at: string;
}

export interface CvDocument {
  id: number;
  application_id: number;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  extracted_characters: number;
  extraction_status: "complete" | string;
  uploaded_at: string;
}

export interface AIAnalysis {
  id: number;
  application_id: number;
  match_score: number;
  skill_coverage: number;
  matching_skills: string[];
  missing_skills: string[];
  cv_skills: string[];
  job_skills: string[];
  strengths: string[];
  recommendations: string[];
  summary: string;
  provider: "openai" | "local" | "local_fallback" | string;
  model: string | null;
  is_stale: boolean;
  created_at: string;
  updated_at: string;
}

export interface InterviewQuestion {
  question: string;
  why_asked: string;
  answer_framework: string;
  talking_points: string[];
}

export interface ApplicationKit {
  id: number;
  application_id: number;
  cover_letter: string;
  elevator_pitch: string;
  interview_questions: InterviewQuestion[];
  questions_to_ask: string[];
  provider: "openai" | "local" | "local_fallback" | string;
  model: string | null;
  is_stale: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total: number;
  active: number;
  interviews: number;
  offers: number;
  response_rate: number;
}

export interface AnalyticsApplication {
  id: number;
  company: string;
  role: string;
  status: ApplicationStatus;
  deadline: string | null;
  match_score: number | null;
}

export interface AnalyticsPoint {
  label: string;
  value: number;
}

export interface AnalyticsData {
  total: number;
  active: number;
  response_rate: number;
  interview_rate: number;
  offer_rate: number;
  average_match_score: number | null;
  analysed_applications: number;
  status_counts: Record<ApplicationStatus, number>;
  monthly_applications: AnalyticsPoint[];
  upcoming_deadlines: AnalyticsApplication[];
  top_matches: AnalyticsApplication[];
}

export interface AssistantResponse {
  answer: string;
  highlights: string[];
  recommended_actions: string[];
  related_application_ids: number[];
  provider: "openai" | "local" | "local_fallback" | string;
  model: string | null;
}

export interface AssistantMessage {
  role: "user" | "assistant";
  content: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface SettingsData {
  user: User;
  ai: {
    configured: boolean;
    model: string;
  };
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  name: string;
}
