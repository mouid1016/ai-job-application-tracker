import { useState, type FormEvent } from "react";
import type { LoginCredentials, RegisterData, User } from "../types";
import { Icon } from "./Icon";

interface AuthPageProps {
  onLogin: (credentials: LoginCredentials) => Promise<User>;
  onRegister: (data: RegisterData) => Promise<User>;
}

type Mode = "login" | "register";

export function AuthPage({ onLogin, onRegister }: AuthPageProps) {
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "register") {
        await onRegister({ name, email, password });
      } else {
        await onLogin({ email, password });
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  async function useDemoAccount() {
    setLoading(true);
    setError(null);
    try {
      await onLogin({ email: "demo@applyflow.dev", password: "demo1234" });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not open the demo account");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-story">
        <div className="auth-brand"><span className="brand-mark"><Icon name="briefcase" size={20} /></span> ApplyFlow</div>
        <div className="auth-message">
          <span className="auth-kicker">YOUR SEARCH, ORGANISED</span>
          <h1>Turn applications into <em>opportunities.</em></h1>
          <p>Track every role, stay ready for interviews and understand where your job search is going.</p>
          <div className="auth-proof">
            <span><strong>One clear view</strong><small>From saved role to accepted offer</small></span>
            <span><strong>Private by design</strong><small>Your applications belong only to you</small></span>
          </div>
        </div>
        <p className="auth-caption">Built as a full-stack portfolio project.</p>
      </section>

      <section className="auth-panel">
        <div className="auth-card">
          <span className="eyebrow">WELCOME TO APPLYFLOW</span>
          <h2>{mode === "login" ? "Sign in to your account" : "Create your account"}</h2>
          <p>{mode === "login" ? "Continue managing your application pipeline." : "Start organising your job search today."}</p>

          <div className="auth-tabs" role="tablist">
            <button className={mode === "login" ? "active" : ""} onClick={() => { setMode("login"); setError(null); }} type="button">Sign in</button>
            <button className={mode === "register" ? "active" : ""} onClick={() => { setMode("register"); setError(null); }} type="button">Register</button>
          </div>

          <form className="auth-form" onSubmit={submit}>
            {mode === "register" && (
              <label>Full name<input value={name} onChange={(event) => setName(event.target.value)} minLength={2} required autoComplete="name" placeholder="Your name" /></label>
            )}
            <label>Email address<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" placeholder="you@example.com" /></label>
            <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={mode === "register" ? 8 : 1} required autoComplete={mode === "login" ? "current-password" : "new-password"} placeholder={mode === "register" ? "At least 8 characters" : "Your password"} /></label>
            {error && <div className="auth-error" role="alert">{error}</div>}
            <button className="button primary auth-submit" disabled={loading} type="submit">{loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}</button>
          </form>

          <div className="auth-divider"><span>or explore first</span></div>
          <button className="demo-button" disabled={loading} onClick={useDemoAccount} type="button">Open demo account <span>→</span></button>
          <p className="demo-hint">Demo login: demo@applyflow.dev · demo1234</p>
        </div>
      </section>
    </main>
  );
}
