import { useState } from "react";
import { STATUSES, type ApplicationStatus, type JobApplication } from "../types";
import { JobCard } from "./JobCard";

interface KanbanBoardProps {
  applications: JobApplication[];
  onMove: (id: number, status: ApplicationStatus) => void;
  onDelete: (id: number) => void;
}

const labels: Record<ApplicationStatus, string> = {
  saved: "Saved",
  applied: "Applied",
  assessment: "Assessment",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
};

export function KanbanBoard({ applications, onMove, onDelete }: KanbanBoardProps) {
  const [draggedId, setDraggedId] = useState<number | null>(null);
  const [dragOver, setDragOver] = useState<ApplicationStatus | null>(null);

  function drop(status: ApplicationStatus) {
    if (draggedId !== null) onMove(draggedId, status);
    setDraggedId(null);
    setDragOver(null);
  }

  return (
    <section className="board" id="board">
      {STATUSES.map((status) => {
        const jobs = applications.filter((application) => application.status === status);
        return (
          <div
            className={`column ${dragOver === status ? "drag-over" : ""}`}
            key={status}
            onDragOver={(event) => { event.preventDefault(); setDragOver(status); }}
            onDragLeave={() => setDragOver(null)}
            onDrop={() => drop(status)}
          >
            <div className="column-header">
              <span className={`status-dot ${status}`} />
              <h2>{labels[status]}</h2>
              <span className="count">{jobs.length}</span>
            </div>
            <div className="column-body">
              {jobs.map((application) => (
                <JobCard
                  key={application.id}
                  application={application}
                  onDelete={onDelete}
                  onDragStart={setDraggedId}
                />
              ))}
              {jobs.length === 0 && <div className="empty-column">Drop an application here</div>}
            </div>
          </div>
        );
      })}
    </section>
  );
}

