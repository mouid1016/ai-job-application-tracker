import type {
  Activity,
  ApplicationCreate,
  ApplicationStatus,
  ApplicationUpdate,
  AuthResponse,
  CvDocument,
  DashboardStats,
  JobApplication,
  LoginCredentials,
  RegisterData,
  User,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "applyflow_access_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const isFormData = options?.body instanceof FormData;
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(!isFormData ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    if (response.status === 401 && path !== "/auth/login") {
      localStorage.removeItem(TOKEN_KEY);
    }
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function download(path: string): Promise<Blob> {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Download failed with status ${response.status}`);
  }
  return response.blob();
}

function storeSession(response: AuthResponse) {
  localStorage.setItem(TOKEN_KEY, response.access_token);
  return response.user;
}

export const api = {
  hasToken: () => Boolean(getToken()),
  clearSession: () => localStorage.removeItem(TOKEN_KEY),
  login: async (credentials: LoginCredentials) =>
    storeSession(
      await request<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
      }),
    ),
  register: async (payload: RegisterData) =>
    storeSession(
      await request<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    ),
  getMe: () => request<User>("/auth/me"),
  listApplications: () => request<JobApplication[]>("/applications"),
  getApplication: (id: number) => request<JobApplication>(`/applications/${id}`),
  listActivities: (id: number) => request<Activity[]>(`/applications/${id}/activities`),
  getCv: (id: number) => request<CvDocument | null>(`/applications/${id}/documents/cv`),
  uploadCv: (id: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<CvDocument>(`/applications/${id}/documents/cv`, {
      method: "POST",
      body: form,
    });
  },
  downloadCv: (id: number) => download(`/applications/${id}/documents/cv/download`),
  deleteCv: (id: number) => request<void>(`/applications/${id}/documents/cv`, { method: "DELETE" }),
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
  updateApplication: (id: number, payload: ApplicationUpdate) =>
    request<JobApplication>(`/applications/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteApplication: (id: number) =>
    request<void>(`/applications/${id}`, { method: "DELETE" }),
};
