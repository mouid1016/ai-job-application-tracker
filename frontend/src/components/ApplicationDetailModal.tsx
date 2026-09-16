import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api } from "../api";
import type { Activity, ApplicationStatus, ApplicationUpdate, JobApplication } from "../types";
import { Icon } from "./Icon";

interface ApplicationDetailModalProps {
  application: JobApplication;
  onClose: () => void;
  onSaved: (application: JobApplication) => void;
}

interface DetailForm {
  company: string;
  role: string;
  location: string;
  status: ApplicationStatus;
  salary: string;
  job_url: string;
  deadline: string;
  notes: string;
  job_description: string;
}

function initialForm(application: JobApplication): DetailForm {
  return {
    company: application.company,
    role: application.role,
    location: application.location ?? "",
    status: application.status,
    salary: application.salary ?? "",
    job_url: application.job_url ?? "",
    deadline: application.deadline ?? "",
    notes: application.notes ?? "",
    job_description: application.job_description ?? "",
  };
}

function formatActivityDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function ApplicationDetailModal({ application, onClose, onSaved }: ApplicationDetailModalProps) {
  const [form, setForm] = useState<DetailForm>(() => initialForm(application));
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadActivities = useCallback(async () => {
    try {
      setActivities(await api.listActivities(application.id));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load activity history");
    } finally {
      setLoadingHistory(false);
    }
  }, [application.id]);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", closeOnEscape);
    const timer = window.setTimeout(() => void loadActivities(), 0);
    return () => {
      window.removeEventListener("keydown", closeOnEscape);
      window.clearTimeout(timer);
    };
  }, [loadActivities, onClose]);

  function update<K extends keyof DetailForm>(field: K, value: DetailForm[K]) {
    setSaved(false);
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    const payload: ApplicationUpdate = {
      company: form.company,
      role: form.role,
      location: form.location || null,
      status: form.status,
      salary: form.salary || null,
      job_url: form.job_url || null,
      deadline: form.deadline || null,
      notes: form.notes || null,
      job_description: form.job_description || null,
    };
    try {
      setSaving(true);
      setError(null);
      const updated = await api.updateApplication(application.id, payload);
      onSaved(updated);
      setSaved(true);
      setLoadingHistory(true);
      await loadActivities();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save this application");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="detail-backdrop" role="presentation">
      <section className="detail-modal" role="dialog" aria-modal="true" aria-labelledby="detail-title">
        <header className="detail-header">
          <div>
            <span className="eyebrow">APPLICATION WORKSPACE</span>
            <h2 id="detail-title">{application.role}</h2>
            <p>{application.company}{application.location ? ` · ${application.location}` : ""}</p>
          </div>
          <button className="close-button" onClick={onClose} aria-label="Close application details">×</button>
        </header>

        <div className="detail-layout">
          <form className="detail-form" onSubmit={save}>
            <div className="detail-section-heading"><h3>Application details</h3><span className={`detail-status ${form.status}`}>{form.status}</span></div>
            <div className="form-grid detail-fields">
              <label>Company<input required value={form.company} onChange={(event) => update("company", event.target.value)} /></label>
              <label>Role<input required value={form.role} onChange={(event) => update("role", event.target.value)} /></label>
              <label>Location<input value={form.location} onChange={(event) => update("location", event.target.value)} placeholder="Remote or city" /></label>
              <label>Status
                <select value={form.status} onChange={(event) => update("status", event.target.value as ApplicationStatus)}>
                  <option value="saved">Saved</option><option value="applied">Applied</option><option value="assessment">Assessment</option><option value="interview">Interview</option><option value="offer">Offer</option><option value="rejected">Rejected</option>
                </select>
              </label>
              <label>Salary<input value={form.salary} onChange={(event) => update("salary", event.target.value)} placeholder="e.g. £35k–£45k" /></label>
              <label>Deadline<input type="date" value={form.deadline} onChange={(event) => update("deadline", event.target.value)} /></label>
              <label className="wide">Job URL<input type="url" value={form.job_url} onChange={(event) => update("job_url", event.target.value)} placeholder="https://…" /></label>
            </div>

            <label className="detail-textarea-label">Personal notes<textarea rows={4} value={form.notes} onChange={(event) => update("notes", event.target.value)} placeholder="Recruiter details, interview preparation and reminders…" /></label>
            <label className="detail-textarea-label">Job description<textarea rows={9} value={form.job_description} onChange={(event) => update("job_description", event.target.value)} placeholder="Paste the full job description here. This will power AI matching in the next milestone." /></label>

            {error && <div className="auth-error" role="alert">{error}</div>}
            <div className="detail-actions">
              {saved && <span className="saved-confirmation">✓ Changes saved</span>}
              <button className="button secondary" type="button" onClick={onClose}>Close</button>
              <button className="button primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
            </div>
          </form>

          <aside className="activity-panel">
            <div className="detail-section-heading"><h3>Activity</h3><span>{activities.length}</span></div>
            <p className="activity-intro">A record of progress and important changes.</p>
            {loadingHistory ? (
              <div className="activity-loading"><span className="spinner" /></div>
            ) : activities.length ? (
              <ol className="activity-list">
                {activities.map((activity) => (
                  <li key={activity.id} className={activity.event_type}>
                    <span className="activity-icon"><Icon name={activity.event_type === "status_changed" ? "chart" : activity.event_type === "created" ? "plus" : "briefcase"} size={14} /></span>
                    <div><strong>{activity.description}</strong><time>{formatActivityDate(activity.created_at)}</time></div>
                  </li>
                ))}
              </ol>
            ) : (
              <div className="empty-activity">Changes to this application will appear here.</div>
            )}
          </aside>
        </div>
      </section>
    </div>
  );
}
