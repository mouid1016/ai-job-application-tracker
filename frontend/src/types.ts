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

export interface DashboardStats {
  total: number;
  active: number;
  interviews: number;
  offers: number;
  response_rate: number;
}

