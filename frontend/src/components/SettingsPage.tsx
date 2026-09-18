import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api";
import type { SettingsData, User } from "../types";
import { Icon } from "./Icon";

interface SettingsPageProps {
  user: User;
  onUserUpdated: (user: User) => void;
  onAccountDeleted: () => void;
}

export function SettingsPage({ user, onUserUpdated, onAccountDeleted }: SettingsPageProps) {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [name, setName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteConfirmation, setDeleteConfirmation] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { void api.getSettings().then(setSettings).catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load settings")); }, []);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    try { setBusy("profile"); setError(null); const updated = await api.updateProfile({ name, email }); onUserUpdated(updated); setMessage("Profile updated"); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not update your profile"); }
    finally { setBusy(null); }
  }

  async function savePassword(event: FormEvent) {
    event.preventDefault();
    try { setBusy("password"); setError(null); await api.updatePassword({ current_password: currentPassword, new_password: newPassword }); setCurrentPassword(""); setNewPassword(""); setMessage("Password changed"); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not change your password"); }
    finally { setBusy(null); }
  }

  async function exportData() {
    try { setBusy("export"); const data = await api.exportData(); const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })); const link = document.createElement("a"); link.href = url; link.download = `applyflow-export-${new Date().toISOString().slice(0, 10)}.json`; link.click(); URL.revokeObjectURL(url); setMessage("Export downloaded"); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not export your data"); }
    finally { setBusy(null); }
  }

  async function deleteAccount(event: FormEvent) {
    event.preventDefault();
    if (deleteConfirmation !== "DELETE") return;
    if (!window.confirm("Permanently delete your account and every application? This cannot be undone.")) return;
    try { setBusy("delete"); setError(null); await api.deleteAccount(deletePassword); api.clearSession(); onAccountDeleted(); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not delete your account"); setBusy(null); }
  }

  return (
    <div className="feature-page settings-page">
      <header className="page-header"><div><span className="eyebrow">ACCOUNT & PRIVACY</span><h1>Settings</h1><p>Manage your profile, security, AI configuration, and account data.</p></div></header>
      {message && <div className="settings-success">✓ {message}<button onClick={() => setMessage(null)}>×</button></div>}
      {error && <div className="auth-error" role="alert">{error}</div>}

      <div className="settings-grid">
        <section className="settings-card"><div className="settings-card-title"><span><Icon name="settings" /></span><div><h2>Profile</h2><p>Your account identity</p></div></div><form onSubmit={saveProfile}><label>Name<input value={name} onChange={(event) => setName(event.target.value)} minLength={2} required /></label><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><button className="button primary" disabled={busy === "profile"}>{busy === "profile" ? "Saving…" : "Save profile"}</button></form></section>

        <section className="settings-card"><div className="settings-card-title"><span><Icon name="settings" /></span><div><h2>Password</h2><p>Use at least eight characters</p></div></div><form onSubmit={savePassword}><label>Current password<input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required /></label><label>New password<input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} minLength={8} required /></label><button className="button secondary" disabled={busy === "password"}>{busy === "password" ? "Changing…" : "Change password"}</button></form></section>

        <section className="settings-card"><div className="settings-card-title"><span><Icon name="sparkles" /></span><div><h2>AI configuration</h2><p>Server-side connection status</p></div></div>{settings ? <div className="ai-status"><span className={settings.ai.configured ? "connected" : "local"}>{settings.ai.configured ? "Connected" : "Local mode"}</span><strong>{settings.ai.configured ? settings.ai.model : "No OpenAI API key configured"}</strong><p>{settings.ai.configured ? "AI requests use the server key; it is never sent to your browser." : "Matching, toolkits, and assistant guidance use deterministic local fallbacks."}</p></div> : <div className="settings-loading"><span className="spinner" /></div>}</section>

        <section className="settings-card"><div className="settings-card-title"><span><Icon name="download" /></span><div><h2>Export data</h2><p>Download a portable JSON backup</p></div></div><p className="settings-copy">Includes your profile, applications, saved analyses, cover letters, and interview toolkits.</p><button className="button secondary" onClick={() => void exportData()} disabled={busy === "export"}>{busy === "export" ? "Preparing…" : "Download my data"}</button></section>

        <section className="settings-card danger-zone"><div className="settings-card-title"><span><Icon name="trash" /></span><div><h2>Delete account</h2><p>Permanently remove all data</p></div></div><form onSubmit={deleteAccount}><label>Current password<input type="password" value={deletePassword} onChange={(event) => setDeletePassword(event.target.value)} required /></label><label>Type DELETE to confirm<input value={deleteConfirmation} onChange={(event) => setDeleteConfirmation(event.target.value)} required /></label><button className="danger-button" disabled={busy === "delete" || deleteConfirmation !== "DELETE"}>{busy === "delete" ? "Deleting…" : "Delete account permanently"}</button></form></section>
      </div>
    </div>
  );
}
