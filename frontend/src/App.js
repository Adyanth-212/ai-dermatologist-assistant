import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import ReactMarkdown from 'react-markdown';

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
  const [triage, setTriage] = useState(null); // {condition, confidence}
  const [view, setView] = useState("landing"); // landing | preview | fast_triage | deep_search
  const { theme, toggle } = useTheme();

  // --- NEW: Chat State ---
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef(null); // To auto-scroll chat
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
  atopic_dermatitis: [
    "What causes Atopic Dermatitis?",
    "How can I manage Atopic Dermatitis at home?",
    "Are there foods that worsen Atopic Dermatitis?",
    "When should I visit a dermatologist for Atopic Dermatitis?",
  ],
  melanoma: [
    "What are the early warning signs of Melanoma?",
    "How can I differentiate Melanoma from normal moles?",
    "What are the main causes and risk factors for Melanoma?",
    "What treatments are available for Melanoma?",
  ],
  bcc: [
    "What are common symptoms of Basal Cell Carcinoma (BCC)?",
    "Is BCC dangerous or slow-growing?",
    "What treatments are available for BCC?",
    "How can I prevent Basal Cell Carcinoma recurrence?",
  ],
  melanocytic_nevi: [
    "What are Melanocytic Nevi (moles)?",
    "How can I tell if a mole is harmless or needs checking?",
    "Do Melanocytic Nevi ever become cancerous?",
    "How should I care for skin with many moles?",
  ],
  bkl: [
    "What are Benign Keratosis-like Lesions (BKL)?",
    "Are BKLs caused by sun exposure?",
    "When should I get BKLs checked by a doctor?",
    "Are there home treatments for Benign Keratosis?",
  ],
  seborrheic_keratoses: [
    "What are Seborrheic Keratoses and how do they form?",
    "Can Seborrheic Keratoses turn into skin cancer?",
    "Are there safe removal options for Seborrheic Keratoses?",
    "How can I tell Seborrheic Keratoses from other growths?",
  ],
  fungal_infections: [
    "What causes Tinea, Ringworm, or Candidiasis?",
    "What are the symptoms of common fungal skin infections?",
    "Which antifungal creams or medications are most effective?",
    "How can I prevent fungal skin infections from recurring?",
  ],
  viral_infections: [
    "What are common viral skin infections like Warts and Molluscum?",
    "How are viral skin infections transmitted?",
    "What are home remedies and medical treatments for Warts?",
    "When should I see a doctor for viral skin lesions?",
  ],
  lichen_planus: [
    "What is Lichen Planus and how is it related to Psoriasis?",
    "What are common triggers for Lichen Planus?",
    "Is Lichen Planus contagious?",
    "What are the best treatments for Lichen Planus?",
  ],
  default: [
    "What are common skin rashes?",
    "How does sunscreen work?",
    "When should I see a dermatologist?",
  ],
};

  // --- (Geolocation and Cleanup Effects are unchanged) ---
  const [geo, setGeo] = useState(null);
  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (g) => setGeo(g),
      () => {},
      { timeout: 1500 }
    );
  }, []);

  useEffect(() => {
    return () => {
      if (previewURL) URL.revokeObjectURL(previewURL);
    };
  }, [previewURL]);

  // --- Auto-scroll chat ---
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


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
      
      // Use API_BASE, which points to your M4 server
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

  // MODIFIED: This now sets up the chat
  function handleStartDeepSearch() {
    if (!file) return;
    
    // Get context from triage if it exists
    const context = triage ? triage.condition : "the uploaded image";
    
    // Pre-populate chat with a welcome message
    setMessages([
      {
        sender: "bot",
        text: `I'm ready to discuss ${context}. You can ask me about common symptoms or treatments.`,
      },
    ]);
    setView("deep_search");
  }

  // NEW: This function calls your /chat endpoint
  async function handleSendMessage(e) {
    e.preventDefault(); // Prevent form from reloading page
    if (!currentMessage.trim()) return;

    const userMessage = { sender: "user", text: currentMessage };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentMessage("");
    setIsChatLoading(true);

    try {
      const { data } = await axios.post(`${API_BASE}/chat`, {
        message: currentMessage,
        context: triage ? triage.condition : null, // Send context
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

  return (
    <div className="relative min-h-screen bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-50">
      {/* ... (background and nav are unchanged) ... */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="bg-grid absolute inset-0 opacity-20 dark:opacity-25" />
        <div className="orb orb-purple absolute left-[-8vmin] top-[-6vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatA mix-blend-multiply dark:mix-blend-screen opacity-75" />
        <div className="orb orb-green absolute right-[-12vmin] top-[10vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatB mix-blend-multiply dark:mix-blend-screen opacity-70" />
        <div className="orb orb-pink absolute left-[10vmin] bottom-[-14vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatC mix-blend-multiply dark:mix-blend-screen opacity-70" />
      </div>
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
      
      {/* ... (hero title and action row are unchanged) ... */}
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

      {/* --- (Preview Panel is unchanged) --- */}
      <div className="relative z-10 mx-auto mt-6 max-w-5xl px-6">
        {view !== "landing" && (
          <>
            <h2 className="mb-3 text-center text-lg font-semibold text-slate-300">
              Image Preview
            </h2>
            <div className="mx-auto w-full max-w-3xl rounded-2xl border border-white/10 bg-white/5 p-3 shadow-2xl backdrop-blur dark:border-white/10">
              <div className="overflow-hidden rounded-xl border border-white/10 bg-black/80">
                {previewURL ? (
                  <img
                    src={previewURL}
                    alt={fileName || "uploaded"}
                    className="mx-auto block max-h-[56vh] w-auto object-contain"
                  />
                ) : (
                  <div className="flex h-64 items-center justify-center text-slate-400">
                    No image selected.
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* --- (Triage Panel is unchanged) --- */}
        {view === "fast_triage" && triage && (
          <div className="mx-auto mt-6 w-full max-w-3xl rounded-2xl border border-white/10 bg-white/5 p-4 text-center backdrop-blur">
            <div className="text-sm uppercase tracking-wide text-slate-400">
              Quick Triage
            </div>
            <div className="mt-1 text-2xl font-semibold">
              {triage.condition}{" "}
              <span className="text-slate-400">
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

        {/* --- MODIFIED: Deep Search Panel is now a real Chatbot --- */}
        {view === "deep_search" && (
          <div className="mx-auto mt-6 w-full max-w-3xl rounded-2xl border border-white/10 bg-white/5 p-4 text-left backdrop-blur">
            <div className="mb-2 text-center text-sm uppercase tracking-wide text-slate-400">
              Deep Search (Chat)
            </div>
            
            {/* Message List */}
            <div className="h-80 overflow-y-auto rounded-lg border border-slate-700/50 bg-slate-900/50 p-4 space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                  msg.sender === "user"
                    ? "bg-indigo-600 text-white"
                    // Add prose class + spacing modifiers
                    : "bg-slate-700 text-slate-200 prose prose-invert prose-sm max-w-none prose-headings:mt-3 prose-p:mb-2"
                }`}
                >
                {/* Wrap bot messages in ReactMarkdown */}
                {msg.sender === 'bot' ? <ReactMarkdown>{msg.text}</ReactMarkdown> : msg.text}
                  </div>    
                </div>
              ))}
              {isChatLoading && (
                <div className="justify-start flex">
                  <div className="bg-slate-700 text-slate-400 text-sm px-4 py-2 rounded-lg">
                    Typing...
                  </div>
                </div>
              )}
              {/* Empty div to auto-scroll to */}
              <div ref={chatEndRef} />
            </div>

            {/* Message Input Form */}
            <form onSubmit={handleSendMessage} className="mt-4 flex gap-2">
              {/* Wrap the input in a div with the gradient and padding */}
<div className="flex-1 rounded-lg bg-gradient-to-r from-indigo-500 to-emerald-500 p-[2px]">
  <input
    type="text"
    value={currentMessage}
    onChange={(e) => setCurrentMessage(e.target.value)}
    placeholder="Ask about symptoms, treatments, etc..."
    // Removed border, added bg color, slightly smaller rounding
    className="w-full rounded-[7px] bg-slate-800/80 px-4 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-0" 
    disabled={isChatLoading}
  />
</div>

{/* The Send button remains the same */}
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

      {/* --- (Bottom Cards are unchanged) --- */}
      <section className="relative z-10 mx-auto mt-10 max-w-5xl px-6 pb-16 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <article className="rounded-2xl border border-slate-900/10 bg-slate-900/[.03] p-4 text-left backdrop-blur dark:border-white/15 dark:bg-white/5">
          <div className="mb-1 text-xl">🖼️</div>
          <h3 className="font-semibold">1. Upload</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Clear, well-lit skin photo. No faces/PII.
          </p>
        </article>
        <article className="rounded-2xl border border-slate-900/10 bg-slate-900/[.03] p-4 text-left backdrop-blur dark:border-white/15 dark:bg-white/5">
          <div className="mb-1 text-xl">⚙️</div>
          <h3 className="font-semibold">2. Analyze</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Quick triage now, detailed Grad-CAM report on demand.
          </p>
        </article>
        <article className="rounded-2xl border border-slate-900/10 bg-slate-900/[.03] p-4 text-left backdrop-blur dark:border-white/15 dark:bg-white/5">
          <div className="mb-1 text-xl">✨</div>
          <h3 className="font-semibold">3. Dual Analysis</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Get a quick answer from our fast model, or launch an AI chat to
            analyze the disease in-depth.
          </p>
        </article>
      </section>
    </div>
  );
}