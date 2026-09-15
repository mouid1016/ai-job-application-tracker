import { Icon } from "./Icon";
import type { User } from "../types";

interface SidebarProps {
  user: User;
  onLogout: () => void;
}

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

export function Sidebar({ user, onLogout }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark"><Icon name="briefcase" size={20} /></span>
        <span>ApplyFlow</span>
      </div>

      <nav className="nav" aria-label="Main navigation">
        <a className="nav-item active" href="#board"><Icon name="grid" /> Applications</a>
        <a className="nav-item" href="#insights"><Icon name="chart" /> Analytics</a>
        <a className="nav-item" href="#ai"><Icon name="sparkles" /> AI Assistant <span className="soon">Soon</span></a>
      </nav>

      <div className="sidebar-bottom">
        <a className="nav-item" href="#settings"><Icon name="settings" /> Settings</a>
        <button className="profile" onClick={onLogout} title="Sign out">
          <span className="avatar">{initials(user.name)}</span>
          <span><strong>{user.name}</strong><small>Sign out</small></span>
        </button>
      </div>
    </aside>
  );
}
