import { useEffect, useRef, useState, type FormEvent } from "react";
import { api } from "../api";
import type { AssistantMessage, AssistantResponse, JobApplication } from "../types";
import { Icon } from "./Icon";

const suggestions = [
  "Which applications should I prioritise?",
  "What skills am I commonly missing?",
  "Create my job-search plan for this week.",
  "Summarise my progress.",
];

interface ChatEntry extends AssistantMessage {
  id: number;
  result?: AssistantResponse;
}

interface AssistantPageProps {
  applications: JobApplication[];
  onOpenApplication: (id: number) => void;
  onOpenSettings: () => void;
}

export function AssistantPage({ applications, onOpenApplication, onOpenSettings }: AssistantPageProps) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatEntry[]>([]);
  const [aiConfigured, setAiConfigured] = useState<boolean | null>(null);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const nextId = useRef(1);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    void api.getSettings().then((settings) => setAiConfigured(settings.ai.configured)).catch(() => setAiConfigured(false));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, asking]);

  async function ask(value = question) {
    const cleaned = value.trim();
    if (!cleaned || asking) return;
    const history: AssistantMessage[] = messages.slice(-10).map(({ role, content }) => ({ role, content }));
    setMessages((current) => [...current, { id: nextId.current++, role: "user", content: cleaned }]);
    setQuestion("");
    try {
      setAsking(true);
      setError(null);
      const result = await api.askAssistant(cleaned, history);
      setMessages((current) => [...current, { id: nextId.current++, role: "assistant", content: result.answer, result }]);
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

  return (
    <div className="feature-page assistant-page">
      <header className="page-header"><div><span className="eyebrow">YOUR JOB-SEARCH COPILOT</span><h1>AI Assistant</h1><p>Have a conversation grounded in your applications and match analyses.</p></div><span className="assistant-mode"><Icon name="sparkles" size={14} /> {aiConfigured === true ? "OpenAI connected" : aiConfigured === false ? "Limited local mode" : "Checking connection…"}</span></header>

      {aiConfigured === false && <div className="assistant-connection-warning"><div><strong>Connect OpenAI for unrestricted questions</strong><p>You are currently using the limited local fallback, which can only handle a few job-search categories.</p></div><button onClick={onOpenSettings}>View setup</button></div>}

      <section className={`assistant-chat ${messages.length ? "has-messages" : ""}`}>
        {!messages.length && <div className="assistant-welcome">
          <div className="assistant-orb"><Icon name="sparkles" size={27} /></div>
          <h2>Ask about any part of your job search</h2>
          <p>The examples below are starting points, not the only questions available. Once OpenAI is connected, you can ask free-form questions and follow up naturally.</p>
          <span>Example questions</span>
          <div className="prompt-grid">{suggestions.map((suggestion) => <button key={suggestion} onClick={() => void ask(suggestion)} disabled={asking}>{suggestion}</button>)}</div>
        </div>}

        {messages.length > 0 && <div className="chat-thread">
          {messages.map((message) => {
            const related = message.result?.related_application_ids.map((id) => applications.find((item) => item.id === id)).filter((item): item is JobApplication => Boolean(item)) ?? [];
            return <article className={`chat-message ${message.role}`} key={message.id}>
              <div className="chat-avatar">{message.role === "assistant" ? <Icon name="sparkles" size={15} /> : "You"}</div>
              <div className="chat-bubble">
                <p>{message.content}</p>
                {message.result && <>
                  <div className="response-meta">{message.result.provider === "openai" ? `OpenAI · ${message.result.model}` : message.result.provider === "local_fallback" ? "OpenAI unavailable · local fallback used" : "Limited local mode"}</div>
                  <div className="assistant-columns">
                    <div><h3>What stands out</h3><ul>{message.result.highlights.map((item) => <li key={item}>{item}</li>)}</ul></div>
                    <div><h3>Recommended actions</h3><ol>{message.result.recommended_actions.map((item) => <li key={item}>{item}</li>)}</ol></div>
                  </div>
                  {related.length > 0 && <div className="related-applications"><h3>Relevant applications</h3>{related.map((item) => <button key={item.id} onClick={() => onOpenApplication(item.id)}><span>{item.company[0]}</span><div><strong>{item.role}</strong><small>{item.company} · {item.status}</small></div><b>{item.match_score === null ? "Open" : `${item.match_score}%`}</b></button>)}</div>}
                </>}
              </div>
            </article>;
          })}
          {asking && <article className="chat-message assistant"><div className="chat-avatar"><Icon name="sparkles" size={15} /></div><div className="chat-bubble typing"><span /><span /><span /></div></article>}
          <div ref={endRef} />
        </div>}

        {error && <div className="auth-error" role="alert">{error}</div>}
        <form className="chat-composer" onSubmit={submit}>
          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void ask(); } }} rows={2} maxLength={500} placeholder="Ask anything about your job search…" />
          <button type="submit" disabled={asking || !question.trim()}>{asking ? <span className="spinner" /> : <Icon name="sparkles" size={16} />}<span>{asking ? "Thinking" : "Send"}</span></button>
        </form>
        <p className="assistant-disclaimer">AI guidance can be wrong. Verify employer details and never invent experience in an application.</p>
      </section>
    </div>
  );
}
