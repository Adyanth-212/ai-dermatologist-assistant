// frontend/src/App.js
import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import ReactMarkdown from 'react-markdown'; // Make sure this is imported

// Make sure API_BASE points to your backend
const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8001";

function useTheme() {
  const [theme, setTheme] = useState(
    document.documentElement.classList.contains("dark") ? "dark" : "light"
  );
  const apply = (t) => {
    const root = document.documentElement;
    if (t === "dark") root.classList.add("dark");
    else root.classList.remove("dark");
    localStorage.setItem("theme", t);
    setTheme(t);
  };
  const toggle = () => apply(theme === "dark" ? "light" : "dark");
  return { theme, toggle, setTheme: apply };
}

export default function App() {
  const fileRef = useRef(null);
  const [file, setFile] = useState(null);
  const [previewURL, setPreviewURL] = useState("");
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [triage, setTriage] = useState(null);
  const [view, setView] = useState("landing");
  const { theme, toggle } = useTheme();

  // --- Chat State ---
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef(null); // To auto-scroll chat

  // --- Geolocation ---
  const [geo, setGeo] = useState(null);
  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (g) => setGeo(g),
      () => {},
      { timeout: 1500 }
    );
  }, []);

  // --- Cleanup Preview URL ---
  useEffect(() => {
    return () => {
      if (previewURL) URL.revokeObjectURL(previewURL);
    };
  }, [previewURL]);

  // --- Auto-scroll chat ---
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- Suggested Prompts ---
  const suggestedPrompts = {
    eczema: [
      "What are common Eczema triggers?",
      "Suggest daily routines for Eczema",
      "Are there OTC options for Eczema?",
      "When should I see a doctor for Eczema?",
    ],
    psoriasis: [
      "What lifestyle changes help Psoriasis?",
      "Are there different types of Psoriasis?",
      "Suggest OTC options for Psoriasis",
      "When should I consult a dermatologist?",
    ],
    default: [
      "What are common skin rashes?",
      "How does sunscreen work?",
      "When should I see a dermatologist?",
    ],
  };

  // --- Event Handlers ---
  function openPicker() {
    fileRef.current?.click();
  }

  function onPick(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    setFileName(f.name);
    const url = URL.createObjectURL(f);
    setPreviewURL(url);
    setView("preview");
    setTriage(null);
    setMessages([]); // Clear chat history
  }

  async function runFastAnalysis() {
    if (!file) return;
    setLoading(true);
    setTriage(null);
    try {
      const form = new FormData();
      form.append("image", file);
      const params = geo
        ? { latitude: geo.coords.latitude, longitude: geo.coords.longitude }
        : {};

      const { data } = await axios.post(`${API_BASE}/analyze/quick`, form, {
        params,
      });
      setTriage({ condition: data.condition, confidence: data.confidence });
      setView("fast_triage");
    } catch (err) {
      alert("Analyze failed. Is your backend server (main_server.py) running on port 8001?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  function handleStartDeepSearch() {
    if (!file) return;
    const context = triage ? triage.condition : "the uploaded image";
    setMessages([
      {
        sender: "bot",
        text: `I'm ready to discuss ${context}. You can ask me about common symptoms or treatments.`,
      },
    ]);
    setView("deep_search");
  }

  async function handleSendMessage(e, directMessage = null) {
    e.preventDefault();
    const messageToSend = directMessage || currentMessage;

    if (!messageToSend.trim()) return;

    const userMessage = { sender: "user", text: messageToSend };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentMessage(""); // Clear input regardless
    setIsChatLoading(true);

    try {
      const { data } = await axios.post(`${API_BASE}/chat`, {
        message: messageToSend,
        context: triage ? triage.condition : null,
      });
      const botMessage = { sender: "bot", text: data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage = { sender: "bot", text: "Sorry, I'm having trouble connecting to the server." };
      setMessages((prev) => [...prev, errorMessage]);
      console.error(err);
    } finally {
      setIsChatLoading(false);
    }
  }

  const handleSuggestionClick = (suggestion) => {
    // We don't need to set currentMessage here as handleSendMessage takes directMessage
    const mockEvent = { preventDefault: () => {} };
    // Call handleSendMessage directly with the suggestion
    handleSendMessage(mockEvent, suggestion);
  };


  // --- Render Logic ---
  return (
    <div className="relative min-h-screen bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-50">
      {/* Background Orbs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="bg-grid absolute inset-0 opacity-20 dark:opacity-25" />
        <div className="orb orb-purple absolute left-[-8vmin] top-[-6vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatA mix-blend-multiply dark:mix-blend-screen opacity-75" />
        <div className="orb orb-green absolute right-[-12vmin] top-[10vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatB mix-blend-multiply dark:mix-blend-screen opacity-70" />
        <div className="orb orb-pink absolute left-[10vmin] bottom-[-14vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatC mix-blend-multiply dark:mix-blend-screen opacity-70" />
      </div>

      {/* Header/Nav */}
      <header className="relative z-10 flex items-center justify-between px-5 py-4 sm:px-7 sm:py-5">
        <div className="text-lg font-extrabold sm:text-xl">
          🩺 Derma
          <span className="bg-gradient-to-r from-emerald-500 via-indigo-500 to-pink-500 bg-clip-text text-transparent">
            AI
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full border px-2.5 py-1 text-[11px] sm:text-xs backdrop-blur ${
              API_BASE && API_BASE !== "http://localhost:8001"
                ? "border-emerald-500/40 text-emerald-700 dark:text-emerald-200"
                : "border-amber-500/40 text-amber-700 dark:text-amber-200"
            }`}
          >
            {API_BASE && API_BASE !== "http://localhost:8001" ? "API ok" : "API not set"}
          </span>
          <button
            onClick={toggle}
            className="inline-flex items-center gap-1.5 rounded-full border border-slate-300 bg-white/70 px-2.5 py-1.5 text-[11px] font-semibold text-slate-800 backdrop-blur hover:bg-white/90 dark:border-white/20 dark:bg-white/10 dark:text-slate-100 dark:hover:bg-white/15"
            title="Toggle theme"
            aria-label="Toggle theme"
          >
            <span className="text-base">{theme === "dark" ? "🌞" : "🌙"}</span>
            <span className="hidden sm:inline">
              {theme === "dark" ? "Light" : "Dark"}
            </span>
          </button>
        </div>
      </header>

      {/* Hero Title */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center pt-10 md:pt-14">
        <h1 className="mt-1 text-4xl font-black leading-[1.1] sm:mt-2 sm:text-6xl">
          AI{" "}
          <span className="bg-gradient-to-r from-indigo-500 via-emerald-400 to-pink-400 bg-clip-text text-transparent">
            Dermatologist
          </span>{" "}
          Assistant
        </h1>
        <p className="mx-auto mt-2 max-w-2xl text-slate-600 dark:text-slate-300">
          Instant, privacy-first skin insights with a visual explanation.
          <br />
          <b>Not medical advice.</b>
        </p>
      </div>

      {/* Action Buttons */}
      <div className="relative z-10 mt-4 flex flex-wrap items-center justify-center gap-3 px-6">
        {view === "landing" && (
          <button
            onClick={openPicker}
            className="rounded-xl bg-gradient-to-r from-indigo-400 to-emerald-400 px-5 py-2.5 font-bold text-slate-900 shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01]"
          >
            Start analysis
          </button>
        )}
        {view === "preview" && (
          <>
            <button
              onClick={openPicker}
              className="rounded-xl border border-slate-300 bg-white/60 px-5 py-2.5 font-semibold backdrop-blur transition hover:bg-white/80 dark:border-white/20 dark:bg-white/10 dark:hover:bg-white/15"
            >
              Change Image
            </button>
            <button
              onClick={runFastAnalysis}
              disabled={loading}
              className="rounded-xl bg-gradient-to-r from-indigo-400 to-emerald-400 px-5 py-2.5 font-bold text-slate-900 shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Analyzing…" : "Run Fast Analysis"}
            </button>
            <button
              onClick={handleStartDeepSearch}
              disabled={loading}
              className="rounded-xl bg-gradient-to-r from-purple-400 to-pink-500 px-5 py-2.5 font-bold text-white shadow-lg shadow-purple-500/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
            >
              Start Deep Search
            </button>
          </>
        )}
        {(view === "fast_triage" || view === "deep_search") && (
          <>
            <button
              onClick={openPicker}
              className="rounded-xl border border-slate-300 bg-white/60 px-5 py-2.5 font-semibold backdrop-blur transition hover:bg-white/80 dark:border-white/20 dark:bg-white/10 dark:hover:bg-white/15"
            >
              Change Image
            </button>
          </>
        )}
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          onChange={onPick}
          className="hidden"
        />
      </div>

      {/* Preview/Triage/Chat Panel */}
      <div className="relative z-10 mx-auto mt-6 max-w-5xl px-6">
        {/* Image Preview */}
        {view !== "landing" && (
          <div className="mb-6"> {/* Added margin-bottom */}
            <h2 className="mb-3 text-center text-lg font-semibold text-slate-700 dark:text-slate-300">
              Image Preview
            </h2>
            <div className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-300 bg-white/50 p-3 shadow-2xl backdrop-blur dark:border-white/10 dark:bg-white/5">
              <div className="overflow-hidden rounded-xl border border-slate-300 bg-slate-200/50 dark:border-white/10 dark:bg-black/80">
                {previewURL ? (
                  <img
                    src={previewURL}
                    alt={fileName || "uploaded"}
                    className="mx-auto block max-h-[56vh] w-auto object-contain"
                  />
                ) : (
                  <div className="flex h-64 items-center justify-center text-slate-500 dark:text-slate-400">
                    No image selected.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Triage Results */}
        {view === "fast_triage" && triage && (
          <div className="mx-auto mt-6 w-full max-w-3xl rounded-2xl border border-slate-300 bg-white/50 p-4 text-center backdrop-blur dark:border-white/10 dark:bg-white/5">
            <div className="text-sm uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Quick Triage
            </div>
            <div className="mt-1 text-2xl font-semibold text-slate-800 dark:text-white">
              {triage.condition}{" "}
              <span className="text-slate-500 dark:text-slate-400">
                ({Math.round(triage.confidence * 100)}%)
              </span>
            </div>
            <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={handleStartDeepSearch}
                className="rounded-xl bg-gradient-to-r from-purple-400 to-pink-500 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-purple-500/30 transition hover:scale-[1.01]"
              >
                Start Deep Search on {triage.condition}
              </button>
              <button
                onClick={runFastAnalysis}
                disabled={loading}
                className="rounded-xl border border-slate-300 bg-white/60 px-4 py-2 text-sm font-semibold backdrop-blur transition hover:bg-white/80 dark:border-white/20 dark:bg-white/10 dark:hover:bg-white/15 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Run Fast Analysis Again"}
              </button>
            </div>
          </div>
        )}

        {/* Chatbot Interface */}
        {view === "deep_search" && (
          <div className="mx-auto mt-6 w-full max-w-3xl rounded-2xl border border-slate-300 bg-white/50 p-4 text-left backdrop-blur dark:border-white/10 dark:bg-white/5">
            <div className="mb-2 text-center text-sm uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Deep Search (Chat)
            </div>

            {/* Message List */}
            <div className="h-80 overflow-y-auto rounded-lg border border-slate-300 bg-slate-100/50 p-4 space-y-4 dark:border-slate-700/50 dark:bg-slate-900/50">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 text-sm shadow ${
                      msg.sender === "user"
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200 prose prose-sm max-w-none prose-headings:mt-3 prose-p:mb-2 dark:prose-invert"
                    }`}
                  >
                    {msg.sender === 'bot' ? <ReactMarkdown>{msg.text}</ReactMarkdown> : msg.text}
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="justify-start flex">
                  <div className="bg-slate-200 text-slate-500 text-sm px-4 py-2 rounded-lg dark:bg-slate-700 dark:text-slate-400">
                    Typing...
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Suggested Prompts */}
            <div className="mt-3 mb-2 flex flex-wrap items-center justify-center gap-2">
              {(suggestedPrompts[triage?.condition?.toLowerCase()] || suggestedPrompts.default).map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(prompt)}
                  className="rounded-full border border-slate-400/50 bg-slate-200/60 px-3 py-1 text-xs text-slate-700 backdrop-blur transition hover:bg-slate-300/80 hover:border-slate-500 dark:border-slate-600/50 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:bg-slate-700/80 dark:hover:border-slate-500"
                  disabled={isChatLoading}
                >
                  {prompt}
                </button>
              ))}
            </div>

            {/* Message Input Form */}
            <form onSubmit={handleSendMessage} className="mt-4 flex gap-2">
               <div className="flex-1 rounded-lg bg-gradient-to-r from-indigo-500 to-emerald-500 p-[2px]">
                 <input
                   type="text"
                   value={currentMessage}
                   onChange={(e) => setCurrentMessage(e.target.value)} // Ensure this is e.target.value
                   placeholder="Ask about symptoms, treatments, etc..."
                   className="w-full rounded-[7px] border-none bg-white px-4 py-2 text-slate-800 placeholder-slate-500 focus:outline-none focus:ring-0 dark:bg-slate-800/80 dark:text-slate-200"
                   disabled={isChatLoading}
                 />
               </div>
              <button
                type="submit"
                className="rounded-lg bg-gradient-to-r from-indigo-500 to-emerald-500 px-5 py-2 font-semibold text-white transition hover:from-indigo-600 hover:to-emerald-600 disabled:opacity-50"
                disabled={isChatLoading}
              >
                Send
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Bottom Cards */}
      <section className="relative z-10 mx-auto mt-10 max-w-5xl px-6 pb-16 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <article className="rounded-2xl border border-slate-300 bg-white/50 p-4 text-left backdrop-blur dark:border-slate-900/10 dark:bg-slate-900/[.03] dark:dark:border-white/15 dark:dark:bg-white/5">
          <div className="mb-1 text-xl">🖼️</div>
          <h3 className="font-semibold text-slate-800 dark:text-white">1. Upload</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Clear, well-lit skin photo. No faces/PII.
          </p>
        </article>
        <article className="rounded-2xl border border-slate-300 bg-white/50 p-4 text-left backdrop-blur dark:border-slate-900/10 dark:bg-slate-900/[.03] dark:dark:border-white/15 dark:dark:bg-white/5">
          <div className="mb-1 text-xl">⚙️</div>
          <h3 className="font-semibold text-slate-800 dark:text-white">2. Analyze</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Quick triage now, detailed Grad-CAM report on demand.
          </p>
        </article>
        <article className="rounded-2xl border border-slate-300 bg-white/50 p-4 text-left backdrop-blur dark:border-slate-900/10 dark:bg-slate-900/[.03] dark:dark:border-white/15 dark:dark:bg-white/5">
          <div className="mb-1 text-xl">✨</div>
          <h3 className="font-semibold text-slate-800 dark:text-white">3. Dual Analysis</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Get a quick answer from our fast model, or launch an AI chat to
            analyze the disease in-depth.
          </p>
        </article>
      </section>
    </div>
  );
}