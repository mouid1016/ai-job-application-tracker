import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api } from "../api";
import type { Activity, ApplicationStatus, ApplicationUpdate, CvDocument, JobApplication } from "../types";
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

function formatFileSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ApplicationDetailModal({ application, onClose, onSaved }: ApplicationDetailModalProps) {
  const [form, setForm] = useState<DetailForm>(() => initialForm(application));
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [cv, setCv] = useState<CvDocument | null>(null);
  const [loadingCv, setLoadingCv] = useState(true);
  const [uploadingCv, setUploadingCv] = useState(false);
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

  const loadCv = useCallback(async () => {
    try {
      setCv(await api.getCv(application.id));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load the CV");
    } finally {
      setLoadingCv(false);
    }
  }, [application.id]);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", closeOnEscape);
    const timer = window.setTimeout(() => {
      void loadActivities();
      void loadCv();
    }, 0);
    return () => {
      window.removeEventListener("keydown", closeOnEscape);
      window.clearTimeout(timer);
    };
  }, [loadActivities, loadCv, onClose]);

  async function uploadCv(file: File | undefined) {
    if (!file) return;
    if (!/\.(pdf|docx)$/i.test(file.name)) {
      setError("Choose a PDF or DOCX file");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("CV files must be 5 MB or smaller");
      return;
    }
    try {
      setUploadingCv(true);
      setError(null);
      setCv(await api.uploadCv(application.id, file));
      setLoadingHistory(true);
      await loadActivities();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not upload the CV");
    } finally {
      setUploadingCv(false);
    }
  }

  async function downloadCv() {
    if (!cv) return;
    try {
      setError(null);
      const blob = await api.downloadCv(application.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = cv.original_filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not download the CV");
    }
  }

  async function deleteCv() {
    if (!cv || !window.confirm(`Remove ${cv.original_filename}?`)) return;
    try {
      setUploadingCv(true);
      setError(null);
      await api.deleteCv(application.id);
      setCv(null);
      setLoadingHistory(true);
      await loadActivities();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not remove the CV");
    } finally {
      setUploadingCv(false);
    }
  }

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

            <section className="cv-section" aria-labelledby="cv-heading">
              <div className="detail-section-heading">
                <div><h3 id="cv-heading">CV document</h3><p>PDF or DOCX, up to 5 MB</p></div>
                {cv && <span className="extraction-badge">Text extracted</span>}
              </div>
              {loadingCv ? (
                <div className="cv-loading"><span className="spinner" /></div>
              ) : cv ? (
                <div className="cv-file">
                  <span className="cv-file-icon"><Icon name="document" size={22} /></span>
                  <div className="cv-file-copy">
                    <strong>{cv.original_filename}</strong>
                    <span>{formatFileSize(cv.size_bytes)} · {cv.extracted_characters.toLocaleString()} readable characters</span>
                  </div>
                  <button className="cv-icon-button" type="button" onClick={() => void downloadCv()} aria-label="Download CV"><Icon name="download" size={17} /></button>
                  <button className="cv-icon-button danger" type="button" onClick={() => void deleteCv()} disabled={uploadingCv} aria-label="Remove CV"><Icon name="trash" size={16} /></button>
                </div>
              ) : (
                <div className="cv-empty">
                  <span className="cv-file-icon"><Icon name="document" size={22} /></span>
                  <div><strong>No CV attached</strong><p>Upload the version you plan to use for this application.</p></div>
                </div>
              )}
              <label className={`cv-upload-button ${uploadingCv ? "disabled" : ""}`}>
                <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" disabled={uploadingCv} onChange={(event) => { void uploadCv(event.target.files?.[0]); event.currentTarget.value = ""; }} />
                {uploadingCv ? <><span className="spinner" /> Processing document…</> : <><Icon name="plus" size={15} /> {cv ? "Replace CV" : "Upload CV"}</>}
              </label>
            </section>

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
                    <span className="activity-icon"><Icon name={activity.event_type.startsWith("cv_") ? "document" : activity.event_type === "status_changed" ? "chart" : activity.event_type === "created" ? "plus" : "briefcase"} size={14} /></span>
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
