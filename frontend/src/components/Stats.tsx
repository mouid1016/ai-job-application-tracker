import type { DashboardStats } from "../types";

interface StatsProps {
  stats: DashboardStats;
}

export function Stats({ stats }: StatsProps) {
  const cards = [
    { label: "Total applications", value: stats.total, detail: `${stats.active} currently active`, tone: "violet" },
    { label: "Interviews", value: stats.interviews, detail: "Keep preparing", tone: "blue" },
    { label: "Offers", value: stats.offers, detail: stats.offers ? "Great progress" : "Your next milestone", tone: "green" },
    { label: "Response rate", value: `${stats.response_rate}%`, detail: "Across all applications", tone: "orange" },
  ];

  return (
    <section className="stats-grid" aria-label="Application summary">
      {cards.map((card) => (
        <article className={`stat-card ${card.tone}`} key={card.label}>
          <div className="stat-label">{card.label}</div>
          <div className="stat-value">{card.value}</div>
          <div className="stat-detail"><span className="trend-dot" /> {card.detail}</div>
        </article>
      ))}
    </section>
  );
}

