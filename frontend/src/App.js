import React, { useRef, useState } from "react";

const API_BASE = process.env.REACT_APP_API_BASE || "";

export default function App() {
  const fileRef = useRef(null);
  const [fileName, setFileName] = useState("");

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-50">
      {/* Animated background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="bg-grid absolute inset-0 opacity-25" />
        <div className="orb orb-purple absolute left-[-8vmin] top-[-6vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatA" />
        <div className="orb orb-green absolute right-[-12vmin] top-[10vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatB" />
        <div className="orb orb-pink absolute left-[10vmin] bottom-[-14vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatC" />
      </div>

      {/* Nav */}
      <header className="relative z-10 flex items-center justify-between px-7 py-5">
        <div className="text-xl font-extrabold">
          🩺 Derma<span className="bg-gradient-to-r from-emerald-400 via-indigo-400 to-pink-400 bg-clip-text text-transparent">AI</span>
        </div>
        <div className={`rounded-full border px-3 py-1 text-xs backdrop-blur ${API_BASE ? "border-emerald-500/50 text-emerald-200" : "border-amber-500/50 text-amber-200"}`}>
          {API_BASE ? "API configured" : "API not set"}
        </div>
      </header>

      {/* Hero */}
      <main className="relative z-10 mx-auto max-w-5xl px-6 pb-16 text-center">
        <h1 className="mx-auto mt-2 text-4xl font-black leading-tight sm:text-6xl">
          AI <span className="bg-gradient-to-r from-indigo-400 via-emerald-400 to-pink-400 bg-clip-text text-transparent">Dermatologist</span> Assistant
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-slate-300">
          Instant, privacy-first skin insights with a visual explanation.
          <br /><b>Not medical advice.</b>
        </p>

        <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => fileRef.current?.click()}
            className="rounded-xl bg-gradient-to-r from-indigo-400 to-emerald-400 px-5 py-2.5 font-bold text-slate-900 shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01]"
          >
            Start analysis
          </button>
          <button
            onClick={() => window.open('https://polygon.technology', '_blank')}
            className="rounded-xl border border-white/20 bg-white/5 px-5 py-2.5 font-semibold backdrop-blur transition hover:bg-white/10"
          >
            See how we verify
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            onChange={(e)=> setFileName(e.target.files?.[0]?.name ?? "")}
            className="hidden"
          />
        </div>

        {fileName && (
          <div className="mt-2 text-sm text-slate-300">
            Selected: <span className="font-semibold text-slate-100">{fileName}</span> (hook to upload next)
          </div>
        )}

        {/* How it works */}
        <section className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <article className="rounded-2xl border border-white/15 bg-white/5 p-4 text-left backdrop-blur">
            <div className="mb-1 text-xl">🖼️</div>
            <h3 className="font-semibold">1. Upload</h3>
            <p className="text-sm text-slate-300">Clear, well-lit skin photo. No faces or personal info.</p>
          </article>
          <article className="rounded-2xl border border-white/15 bg-white/5 p-4 text-left backdrop-blur">
            <div className="mb-1 text-xl">⚙️</div>
            <h3 className="font-semibold">2. Analyze</h3>
            <p className="text-sm text-slate-300">Quick triage now, detailed Grad-CAM report on demand.</p>
          </article>
          <article className="rounded-2xl border border-white/15 bg-white/5 p-4 text-left backdrop-blur">
            <div className="mb-1 text-xl">🔗</div>
            <h3 className="font-semibold">3. Verify</h3>
            <p className="text-sm text-slate-300">Hash anchored on Polygon testnet to prove integrity.</p>
          </article>
        </section>
      </main>

      <footer className="relative z-10 flex justify-center gap-2 pb-10 text-sm text-slate-400">
        <span>© {new Date().getFullYear()} DermaAI • For education only.</span>
        <span>•</span>
        <a className="underline decoration-dotted hover:text-slate-200" href="https://openuv.io" target="_blank" rel="noreferrer">UV data</a>
      </footer>
    </div>
  );
}
