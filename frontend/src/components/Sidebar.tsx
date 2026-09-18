import { Icon } from "./Icon";
import type { User } from "../types";

interface SidebarProps {
  user: User;
  onLogout: () => void;
  currentPage: "applications" | "analytics" | "assistant" | "settings";
  onNavigate: (page: "applications" | "analytics" | "assistant" | "settings") => void;
}

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

export function Sidebar({ user, onLogout, currentPage, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark"><Icon name="briefcase" size={20} /></span>
        <span>ApplyFlow</span>
      </div>

      <nav className="nav" aria-label="Main navigation">
        <button className={`nav-item ${currentPage === "applications" ? "active" : ""}`} onClick={() => onNavigate("applications")}><Icon name="grid" /> Applications</button>
        <button className={`nav-item ${currentPage === "analytics" ? "active" : ""}`} onClick={() => onNavigate("analytics")}><Icon name="chart" /> Analytics</button>
        <button className={`nav-item ${currentPage === "assistant" ? "active" : ""}`} onClick={() => onNavigate("assistant")}><Icon name="sparkles" /> AI Assistant</button>
      </nav>

      <div className="sidebar-bottom">
        <button className={`nav-item ${currentPage === "settings" ? "active" : ""}`} onClick={() => onNavigate("settings")}><Icon name="settings" /> Settings</button>
        <button className="profile" onClick={onLogout} title="Sign out">
          <span className="avatar">{initials(user.name)}</span>
          <span><strong>{user.name}</strong><small>Sign out</small></span>
        </button>
      </div>
    </aside>
  );
}
