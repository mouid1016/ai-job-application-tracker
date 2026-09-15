import { Icon } from "./Icon";

export function Sidebar() {
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
        <div className="profile">
          <span className="avatar">JD</span>
          <span><strong>Job seeker</strong><small>Portfolio mode</small></span>
        </div>
      </div>
    </aside>
  );
}

