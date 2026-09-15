import type { JobApplication } from "../types";
import { Icon } from "./Icon";

interface JobCardProps {
  application: JobApplication;
  onDelete: (id: number) => void;
  onDragStart: (id: number) => void;
}

const companyColors = ["#6c5ce7", "#0984e3", "#00a884", "#e17055", "#2d3436", "#d63031"];

function companyColor(company: string) {
  const value = [...company].reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return companyColors[value % companyColors.length];
}

function initials(company: string) {
  return company.split(/\s+/).slice(0, 2).map((word) => word[0]).join("").toUpperCase();
}

function formatDeadline(deadline: string | null) {
  if (!deadline) return "No deadline";
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short" }).format(new Date(`${deadline}T00:00:00`));
}

export function JobCard({ application, onDelete, onDragStart }: JobCardProps) {
  return (
    <article
      className="job-card"
      draggable
      onDragStart={() => onDragStart(application.id)}
      tabIndex={0}
    >
      <div className="card-top">
        <span className="company-logo" style={{ background: companyColor(application.company) }}>
          {initials(application.company)}
        </span>
        <button className="icon-button delete-button" onClick={() => onDelete(application.id)} aria-label={`Delete ${application.company} application`}>
          <Icon name="trash" size={16} />
        </button>
      </div>

      <h3>{application.role}</h3>
      <p className="company-name">{application.company}</p>

      <div className="meta-row"><Icon name="pin" size={14} /> {application.location || "Location not set"}</div>
      <div className="card-footer">
        <span className="meta-row"><Icon name="calendar" size={14} /> {formatDeadline(application.deadline)}</span>
        {application.match_score !== null && <span className="match-score">{application.match_score}% match</span>}
      </div>
    </article>
  );
}

