import type { ApplicationCreate, ApplicationStatus, DashboardStats, JobApplication } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  listApplications: () => request<JobApplication[]>("/applications"),
  getStats: () => request<DashboardStats>("/stats"),
  createApplication: (payload: ApplicationCreate) =>
    request<JobApplication>("/applications", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateStatus: (id: number, status: ApplicationStatus) =>
    request<JobApplication>(`/applications/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  deleteApplication: (id: number) =>
    request<void>(`/applications/${id}`, { method: "DELETE" }),
};

