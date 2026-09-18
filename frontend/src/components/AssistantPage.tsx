import { useState, type FormEvent } from "react";
import { api } from "../api";
import type { AssistantResponse, JobApplication } from "../types";
import { Icon } from "./Icon";

const suggestions = [
  "Which applications should I prioritise?",
  "What skills am I commonly missing?",
  "Create my job-search plan for this week.",
  "Summarise my progress.",
];

interface AssistantPageProps {
  applications: JobApplication[];
  onOpenApplication: (id: number) => void;
}

export function AssistantPage({ applications, onOpenApplication }: AssistantPageProps) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AssistantResponse | null>(null);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(value = question) {
    if (!value.trim()) return;
    try {
      setQuestion(value);
      setAsking(true);
      setError(null);
      setResult(await api.askAssistant(value));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The assistant could not answer");
    } finally {
      setAsking(false);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask();
  }

  const related = result?.related_application_ids.map((id) => applications.find((item) => item.id === id)).filter((item): item is JobApplication => Boolean(item)) ?? [];

  return (
    <div className="feature-page assistant-page">
      <header className="page-header"><div><span className="eyebrow">YOUR JOB-SEARCH COPILOT</span><h1>AI Assistant</h1><p>Ask questions across your tracked applications and saved match analyses.</p></div><span className="assistant-mode"><Icon name="sparkles" size={14} /> Grounded in your data</span></header>

      <section className="assistant-hero">
        <div className="assistant-orb"><Icon name="sparkles" size={27} /></div>
        <h2>What should we work on?</h2>
        <p>I can prioritise roles, identify repeated skill gaps, review your progress, and create a focused weekly plan.</p>
        <form onSubmit={submit}><textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} maxLength={500} placeholder="Ask about your applications…" /><button type="submit" disabled={asking || !question.trim()}>{asking ? <><span className="spinner" /> Thinking…</> : <><Icon name="sparkles" size={15} /> Ask assistant</>}</button></form>
        <div className="prompt-grid">{suggestions.map((suggestion) => <button key={suggestion} onClick={() => void ask(suggestion)} disabled={asking}>{suggestion}</button>)}</div>
      </section>

      {error && <div className="auth-error" role="alert">{error}</div>}
      {result && <section className="assistant-response">
        <div className="response-heading"><div><span className="assistant-orb small"><Icon name="sparkles" size={16} /></span><div><h2>ApplyFlow’s recommendation</h2><p>{result.provider === "openai" ? "OpenAI analysis" : result.provider === "local_fallback" ? "Local fallback" : "Local career coach"}</p></div></div></div>
        <p className="assistant-answer">{result.answer}</p>
        <div className="assistant-columns">
          <div><h3>What stands out</h3><ul>{result.highlights.map((item) => <li key={item}>{item}</li>)}</ul></div>
          <div><h3>Recommended actions</h3><ol>{result.recommended_actions.map((item) => <li key={item}>{item}</li>)}</ol></div>
        </div>
        {related.length > 0 && <div className="related-applications"><h3>Relevant applications</h3>{related.map((item) => <button key={item.id} onClick={() => onOpenApplication(item.id)}><span>{item.company[0]}</span><div><strong>{item.role}</strong><small>{item.company} · {item.status}</small></div><b>{item.match_score === null ? "Open" : `${item.match_score}%`}</b></button>)}</div>}
      </section>}
    </div>
  );
}
