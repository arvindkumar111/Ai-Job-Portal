import { useState } from "react";
import { sendChatMessage } from "../api/client";

function FormattedAnswer({ content }) {
  const blocks = content.split(/\n\s*\n/).filter(Boolean);

  return blocks.map((block, index) => {
    const lines = block.split("\n").filter(Boolean);
    const isList = lines.every((line) => /^\s*[-*•]\s+/.test(line) || /^\s*\d+[.)]\s+/.test(line));
    const isHeading = lines.length === 1 && /^\s*#{1,3}\s+/.test(lines[0]);

    if (isList) {
      const ordered = /^\s*\d+[.)]\s+/.test(lines[0]);
      const List = ordered ? "ol" : "ul";
      return <List key={index}>{lines.map((line, itemIndex) => <li key={itemIndex}>{line.replace(/^\s*(?:[-*•]|\d+[.)])\s+/, "")}</li>)}</List>;
    }
    if (isHeading) {
      return <h3 key={index}>{lines[0].replace(/^\s*#{1,3}\s+/, "")}</h3>;
    }
    return <p key={index}>{lines.join(" ")}</p>;
  });
}

function ChatWidget({ jobId, resumeText, title = "Ask about this job" }) {
  const [apiKey, setApiKey] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const askQuestion = async (event) => {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!apiKey.trim() || !trimmedQuestion || loading) return;

    const history = messages.map(({ role, content }) => ({ role, content }));
    const userMessage = { role: "user", content: trimmedQuestion };
    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setLoading(true);
    setError(null);

    try {
      const result = await sendChatMessage({
        gemini_api_key: apiKey.trim(),
        question: trimmedQuestion,
        job_id: jobId,
        resume_text: resumeText,
        conversation_history: history,
      });
      setMessages((current) => [...current, {
        role: "assistant",
        content: result.answer,
        status: result.status || "success",
      }]);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not get an answer. Check that the backend and API key are valid.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="chat-widget career-chat">
      <header className="career-chat-header">
        <span className="career-chat-icon">✦</span>
        <div><p>AI CAREER ASSISTANT</p><h2>{title}</h2></div>
        <span className="online-status"><i /> Ready</span>
      </header>
      <div className="api-key-row">
        <label htmlFor={`gemini-api-key-${jobId || "resume"}`}>Gemini API key</label>
        <input id={`gemini-api-key-${jobId || "resume"}`} type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder="Paste key to begin" autoComplete="off" />
      </div>
      <div className="chat-messages" aria-live="polite">
        {messages.length === 0 && <div className="chat-welcome"><span>✧</span><p>{resumeText ? "Ask about your skills, role fit, or the best next step in your search." : "Ask anything about this opportunity, from required skills to how to tailor your application."}</p></div>}
        {messages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-message ${message.role} ${message.status || ""}`}><span className="message-label">{message.role === "assistant" ? "CAREER ASSISTANT" : "YOU"}</span>{message.status === "fallback" && <span className="chat-status-note">Answered with a backup AI model</span>}{message.status === "unavailable" && <span className="chat-status-note">AI temporarily unavailable — you can still explore these database roles while the assistant is offline.</span>}<div className="answer-content"><FormattedAnswer content={message.content} /></div></div>)}
      </div>
      <form className="chat-input" onSubmit={askQuestion}>
        <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={resumeText ? "Ask about your skills or best matches" : "Ask a question about this job"} disabled={loading} />
        <button type="submit" disabled={loading || !apiKey.trim() || !question.trim()}>{loading ? "Thinking..." : "Send ↗"}</button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  );
}

export default ChatWidget;
