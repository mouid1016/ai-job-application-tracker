import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { STATUSES, type AnalyticsData, type ApplicationStatus } from "../types";
import { Icon } from "./Icon";

const labels: Record<ApplicationStatus, string> = {
  saved: "Saved",
  applied: "Applied",
  assessment: "Assessment",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
};

function formatDeadline(value: string) {
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`));
}

export function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void api.getAnalytics().then(setData).catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load analytics"));
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const maximumMonth = useMemo(() => Math.max(1, ...(data?.monthly_applications.map((point) => point.value) ?? [1])), [data]);

  if (error) return <div className="page-state"><div className="auth-error">{error}</div></div>;
  if (!data) return <div className="page-state"><span className="spinner" /> Loading analytics…</div>;

  return (
    <div className="feature-page">
      <header className="page-header">
        <div><span className="eyebrow">JOB SEARCH PERFORMANCE</span><h1>Analytics</h1><p>Understand your pipeline and decide where to focus next.</p></div>
      </header>

      <section className="analytics-metrics">
        <article><span>Response rate</span><strong>{data.response_rate}%</strong><small>{data.total} total applications</small></article>
        <article><span>Interview rate</span><strong>{data.interview_rate}%</strong><small>Including applications that became offers</small></article>
        <article><span>Offer rate</span><strong>{data.offer_rate}%</strong><small>{data.status_counts.offer} offer{data.status_counts.offer === 1 ? "" : "s"}</small></article>
        <article><span>Average match</span><strong>{data.average_match_score === null ? "—" : `${data.average_match_score}%`}</strong><small>{data.analysed_applications} analysed</small></article>
      </section>

      <div className="analytics-grid">
        <section className="analytics-panel">
          <div className="panel-heading"><div><h2>Application funnel</h2><p>Current applications at each stage</p></div><Icon name="chart" /></div>
          <div className="funnel-list">
            {STATUSES.map((status) => {
              const count = data.status_counts[status];
              const width = data.total ? Math.max(count ? 8 : 0, count / data.total * 100) : 0;
              return <div className="funnel-row" key={status}><span>{labels[status]}</span><div><i className={status} style={{ width: `${width}%` }} /></div><strong>{count}</strong></div>;
            })}
          </div>
        </section>

        <section className="analytics-panel">
          <div className="panel-heading"><div><h2>Applications over time</h2><p>New applications during the last six months</p></div><Icon name="calendar" /></div>
          <div className="month-chart">
            {data.monthly_applications.map((point) => <div key={point.label}><strong>{point.value}</strong><i style={{ height: `${Math.max(point.value ? 12 : 2, point.value / maximumMonth * 100)}%` }} /><span>{point.label.split(" ")[0]}</span></div>)}
          </div>
        </section>

        <section className="analytics-panel">
          <div className="panel-heading"><div><h2>Upcoming deadlines</h2><p>Your next time-sensitive applications</p></div><Icon name="calendar" /></div>
          {data.upcoming_deadlines.length ? <div className="ranked-list">{data.upcoming_deadlines.map((item) => <article key={item.id}><span className="rank-logo">{item.company[0]}</span><div><strong>{item.role}</strong><small>{item.company}</small></div><time>{formatDeadline(item.deadline!)}</time></article>)}</div> : <div className="panel-empty">No upcoming deadlines.</div>}
        </section>

        <section className="analytics-panel">
          <div className="panel-heading"><div><h2>Strongest matches</h2><p>Roles with your highest current CV match</p></div><Icon name="sparkles" /></div>
          {data.top_matches.length ? <div className="ranked-list">{data.top_matches.map((item) => <article key={item.id}><span className="rank-logo">{item.company[0]}</span><div><strong>{item.role}</strong><small>{item.company} · {labels[item.status]}</small></div><b>{item.match_score}%</b></article>)}</div> : <div className="panel-empty">Run a CV match analysis to populate this list.</div>}
        </section>
      </div>
    </div>
  );
}
