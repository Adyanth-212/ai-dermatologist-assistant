import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "";  // CRA env

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
  const [view, setView] = useState("landing"); // landing | preview | triage
  const { theme, toggle } = useTheme();

  // optional geolocation
  const [geo, setGeo] = useState(null);
  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (g) => setGeo(g),
      () => {},
      { timeout: 1500 }
    );
  }, []);

  // cleanup preview URL
  useEffect(() => {
    return () => {
      if (previewURL) URL.revokeObjectURL(previewURL);
    };
  }, [previewURL]);

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
  }

  async function confirmAndAnalyze() {
    if (!file) return;
    setLoading(true);
    try {
      if (API_BASE) {
        const form = new FormData();
        form.append("image", file);
        const params = geo
          ? { latitude: geo.coords.latitude, longitude: geo.coords.longitude }
          : {};
        const { data } = await axios.post(`${API_BASE}/analyze/quick`, form, {
          params,
        });
        setTriage({ condition: data.condition, confidence: data.confidence });
      } else {
        // MOCK if API not configured
        await new Promise((r) => setTimeout(r, 900));
        setTriage({ condition: "Eczema", confidence: 0.71 });
      }
      setView("triage");
    } catch (err) {
      alert("Analyze failed. Check REACT_APP_API_BASE / backend logs.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-50">
      {/* background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="bg-grid absolute inset-0 opacity-20 dark:opacity-25" />
        {/* make orbs pop in both themes */}
        <div className="orb orb-purple absolute left-[-8vmin] top-[-6vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatA mix-blend-multiply dark:mix-blend-screen opacity-75" />
        <div className="orb orb-green absolute right-[-12vmin] top-[10vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatB mix-blend-multiply dark:mix-blend-screen opacity-70" />
        <div className="orb orb-pink absolute left-[10vmin] bottom-[-14vmin] h-[46vmin] w-[46vmin] rounded-full animate-floatC mix-blend-multiply dark:mix-blend-screen opacity-70" />
      </div>

      {/* nav */}
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
              API_BASE
                ? "border-emerald-500/40 text-emerald-700 dark:text-emerald-200"
                : "border-amber-500/40 text-amber-700 dark:text-amber-200"
            }`}
          >
            {API_BASE ? "API ok" : "API not set"}
          </span>
          <button
            onClick={toggle}
            className="inline-flex items-center gap-1.5 rounded-full border border-slate-300 bg-white/70 px-2.5 py-1.5 text-[11px] font-semibold text-slate-800 backdrop-blur hover:bg-white/90 dark:border-white/20 dark:bg-white/10 dark:text-slate-100 dark:hover:bg-white/15"
            title="Toggle theme"
            aria-label="Toggle theme"
          >
            <span className="text-base">{theme === "dark" ? "🌞" : "🌙"}</span>
            <span className="hidden sm:inline">{theme === "dark" ? "Light" : "Dark"}</span>
          </button>
        </div>
      </header>

      {/* hero title */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
        <h1 className="mt-1 text-4xl font-black leading-tight sm:mt-2 sm:text-6xl">
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

      {/* action row */}
      <div className="relative z-10 mt-4 flex flex-wrap items-center justify-center gap-3 px-6">
        {view === "landing" && (
          <>
            <button
              onClick={() => fileRef.current?.click()}
              className="rounded-xl bg-gradient-to-r from-indigo-400 to-emerald-400 px-5 py-2.5 font-bold text-slate-900 shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01]"
            >
              Start analysis
            </button>
            <button
              onClick={() => window.open("https://polygon.technology", "_blank")}
              className="rounded-xl border border-slate-300 bg-white/60 px-5 py-2.5 font-semibold backdrop-blur transition hover:bg-white/80 dark:border-white/20 dark:bg-white/10 dark:hover:bg-white/15"
            >
              See how we verify
            </button>
          </>
        )}

        {view !== "landing" && (
          <>
            <button
              onClick={() => fileRef.current?.click()}
              className="rounded-xl border border-slate-300 bg-white/60 px-5 py-2.5 font-semibold backdrop-blur transition hover:bg-white/80 dark:border-white/20 dark:bg-white/10 dark:hover:bg-white/15"
            >
              Change Image
            </button>
            <button
              onClick={confirmAndAnalyze}
              disabled={loading}
              className="rounded-xl bg-gradient-to-r from-indigo-400 to-emerald-400 px-5 py-2.5 font-bold text-slate-900 shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Analyzing…" : "Confirm & Analyze"}
            </button>
            <button
              onClick={() => window.open("https://polygon.technology", "_blank")}
              className="rounded-xl border border-slate-300 bg-white/60 px-5 py-2.5 font-semibold backdrop-blur transition hover:bg-white/80 dark:border-white/20 dark:bg-white/10 dark:hover:bg-white/15"
            >
              See how we verify
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

      {/* preview / triage panel */}
      <div className="relative z-10 mx-auto mt-6 max-w-5xl px-6 pb-16">
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

            {view === "triage" && triage && (
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
                <div className="mt-3 text-xs text-slate-400">
                  Tip: click “Confirm & Analyze” again to re-run; “Change Image” to select a different photo.
                </div>
              </div>
            )}
          </>
        )}

        {/* bottom cards (how it works) */}
        <section className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
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
            <div className="mb-1 text-xl">🔗</div>
            <h3 className="font-semibold">3. Verify</h3>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Hash anchored on Polygon testnet to prove integrity.
            </p>
          </article>
        </section>
      </div>
    </div>
  );
}
