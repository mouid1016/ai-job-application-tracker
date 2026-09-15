import { useEffect, useState, type FormEvent } from "react";
import type { ApplicationCreate, ApplicationStatus } from "../types";

interface AddApplicationModalProps {
  open: boolean;
  saving: boolean;
  onClose: () => void;
  onSubmit: (application: ApplicationCreate) => Promise<void>;
}

const initialForm: ApplicationCreate = {
  company: "",
  role: "",
  location: "",
  status: "saved",
  salary: "",
  job_url: "",
  deadline: "",
  notes: "",
};

export function AddApplicationModal({ open, saving, onClose, onSubmit }: AddApplicationModalProps) {
  const [form, setForm] = useState<ApplicationCreate>(initialForm);

  useEffect(() => {
    if (!open) return;
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [open, onClose]);

  if (!open) return null;

  function update<K extends keyof ApplicationCreate>(field: K, value: ApplicationCreate[K]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    await onSubmit(form);
    setForm(initialForm);
  }

  return (
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className="modal-header">
          <div><span className="eyebrow">New opportunity</span><h2 id="modal-title">Add an application</h2></div>
          <button className="close-button" onClick={onClose} aria-label="Close">×</button>
        </div>
        <form onSubmit={submit}>
          <div className="form-grid">
            <label>Company<input required autoFocus value={form.company} onChange={(event) => update("company", event.target.value)} placeholder="e.g. OpenAI" /></label>
            <label>Role<input required value={form.role} onChange={(event) => update("role", event.target.value)} placeholder="e.g. Software Engineer" /></label>
            <label>Location<input value={form.location} onChange={(event) => update("location", event.target.value)} placeholder="Remote or city" /></label>
            <label>Status
              <select value={form.status} onChange={(event) => update("status", event.target.value as ApplicationStatus)}>
                <option value="saved">Saved</option><option value="applied">Applied</option><option value="assessment">Assessment</option><option value="interview">Interview</option><option value="offer">Offer</option><option value="rejected">Rejected</option>
              </select>
            </label>
            <label>Deadline<input type="date" value={form.deadline} onChange={(event) => update("deadline", event.target.value)} /></label>
            <label>Salary<input value={form.salary} onChange={(event) => update("salary", event.target.value)} placeholder="e.g. £35k–£45k" /></label>
            <label className="wide">Job URL<input type="url" value={form.job_url} onChange={(event) => update("job_url", event.target.value)} placeholder="https://…" /></label>
            <label className="wide">Notes<textarea rows={3} value={form.notes} onChange={(event) => update("notes", event.target.value)} placeholder="Recruiter details, interview prep, reminders…" /></label>
          </div>
          <div className="modal-actions">
            <button className="button secondary" type="button" onClick={onClose}>Cancel</button>
            <button className="button primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Add application"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

