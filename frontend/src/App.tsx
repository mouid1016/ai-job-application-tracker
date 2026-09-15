import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { AddApplicationModal } from "./components/AddApplicationModal";
import { AuthPage } from "./components/AuthPage";
import { Icon } from "./components/Icon";
import { KanbanBoard } from "./components/KanbanBoard";
import { Sidebar } from "./components/Sidebar";
import { Stats } from "./components/Stats";
import type {
  ApplicationCreate,
  ApplicationStatus,
  DashboardStats,
  JobApplication,
  LoginCredentials,
  RegisterData,
  User,
} from "./types";

const emptyStats: DashboardStats = { total: 0, active: 0, interviews: 0, offers: 0, response_rate: 0 };

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [stats, setStats] = useState<DashboardStats>(emptyStats);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);
      const [jobs, dashboardStats] = await Promise.all([api.listApplications(), api.getStats()]);
      setApplications(jobs);
      setStats(dashboardStats);
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "Could not load your applications";
      setError(message);
      if (!api.hasToken()) setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(async () => {
      if (!api.hasToken()) {
        setAuthLoading(false);
        return;
      }
      try {
        setUser(await api.getMe());
      } catch {
        api.clearSession();
      } finally {
        setAuthLoading(false);
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!user) return;
    const timer = window.setTimeout(() => {
      setLoading(true);
      void loadData();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [user, loadData]);

  const filtered = useMemo(() => {
    const query = search.toLowerCase().trim();
    if (!query) return applications;
    return applications.filter((job) => `${job.company} ${job.role} ${job.location ?? ""}`.toLowerCase().includes(query));
  }, [applications, search]);

  async function login(credentials: LoginCredentials) {
    const authenticatedUser = await api.login(credentials);
    setUser(authenticatedUser);
    return authenticatedUser;
  }

  async function register(data: RegisterData) {
    const authenticatedUser = await api.register(data);
    setUser(authenticatedUser);
    return authenticatedUser;
  }

  function logout() {
    api.clearSession();
    setUser(null);
    setApplications([]);
    setStats(emptyStats);
    setError(null);
  }

  async function addApplication(payload: ApplicationCreate) {
    try {
      setSaving(true);
      await api.createApplication(payload);
      setModalOpen(false);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save the application");
    } finally {
      setSaving(false);
    }
  }

  async function moveApplication(id: number, status: ApplicationStatus) {
    const previous = applications;
    setApplications((current) => current.map((job) => job.id === id ? { ...job, status } : job));
    try {
      await api.updateStatus(id, status);
      setStats(await api.getStats());
    } catch (caught) {
      setApplications(previous);
      setError(caught instanceof Error ? caught.message : "Could not update the application");
    }
  }

  async function deleteApplication(id: number) {
    if (!window.confirm("Delete this application?")) return;
    try {
      await api.deleteApplication(id);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not delete the application");
    }
  }

  if (authLoading) {
    return <div className="app-loading"><span className="brand-mark"><Icon name="briefcase" size={20} /></span><span className="spinner" /></div>;
  }

  if (!user) {
    return <AuthPage onLogin={login} onRegister={register} />;
  }

  return (
    <div className="app-shell">
      <Sidebar user={user} onLogout={logout} />
      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">APPLICATION COMMAND CENTRE</span>
            <h1>Good morning, {user.name.split(" ")[0]} <span aria-hidden="true">👋</span></h1>
            <p>Here’s where your job search stands today.</p>
          </div>
          <button className="button primary" onClick={() => setModalOpen(true)}><Icon name="plus" /> Add application</button>
        </header>

        {error && <div className="alert" role="alert"><span>{error}</span><button onClick={() => setError(null)}>Dismiss</button></div>}

        {loading ? (
          <div className="loading-state"><span className="spinner" /> Loading your applications…</div>
        ) : (
          <>
            <Stats stats={stats} />
            <section className="board-section">
              <div className="section-heading">
                <div><h2>Application pipeline</h2><p>Drag cards between columns as you make progress.</p></div>
                <label className="search-box"><Icon name="search" size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search company or role" aria-label="Search applications" /></label>
              </div>
              <KanbanBoard applications={filtered} onMove={moveApplication} onDelete={deleteApplication} />
            </section>
          </>
        )}
      </main>
      <AddApplicationModal open={modalOpen} saving={saving} onClose={() => setModalOpen(false)} onSubmit={addApplication} />
    </div>
  );
}
