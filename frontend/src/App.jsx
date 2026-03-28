// frontend/src/App.jsx
import { useState, useRef } from "react";
import { useVerify } from "./hooks/useVerify";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import ChatInput    from "./components/ChatInput";
import ChatMessage  from "./components/ChatMessage";
import LoadingState from "./components/LoadingState";
import ErrorState   from "./components/ErrorState";
import HistoryEntry from "./components/HistoryEntry";

const SUGGESTED_QUERIES = [
  "Was Einstein really bad at math in school?",
  "Is the Great Wall of China visible from space?",
  "Did Napoleon have an unusually short stature?",
  "Was the Eiffel Tower supposed to be permanent?",
  "Do humans only use 10% of their brain?",
  "Can you survive any fall into water?",
];

export default function App() {
  const { verify, data, loading, error, reset } = useVerify();
  const [currentQuery, setCurrentQuery] = useState("");
  const [history, setHistory] = useState([]);
  const inputRef = useRef(null);

  useKeyboardShortcuts({
    onFocusInput:  () => inputRef.current?.focus(),
    onClearResult: () => { reset(); inputRef.current?.focus(); },
  });

  const handleSubmit = async (query) => {
    setCurrentQuery(query);
    const result = await verify(query);
    if (result) {
      setHistory(prev => [{ query, data: result }, ...prev]);
    }
  };

  const showHero = !data && !loading && !error && history.length === 0;

  return (
    <div className="min-h-screen flex flex-col bg-[#080E16]">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b border-[#182030]/60 bg-[#080E16]/90 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative w-7 h-7">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#01C4A0] to-[#4BA8E8] opacity-90" />
              <div className="absolute inset-0 rounded-xl flex items-center justify-center">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M8 2L14 5.5V10.5L8 14L2 10.5V5.5L8 2Z" stroke="#050B12" strokeWidth="1.5" strokeLinejoin="round"/>
                  <path d="M8 6L10 7.5V10L8 11.5L6 10V7.5L8 6Z" fill="#050B12"/>
                </svg>
              </div>
            </div>
            <div className="flex flex-col leading-none">
              <span className="font-head text-[13px] font-bold text-white tracking-tight">Trust Sentinel</span>
              <span className="text-[10px] text-[#3D5670] font-mono tracking-wide">AI Fact Verifier</span>
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-[#182030] bg-[#0D1520]">
              <div className="w-1.5 h-1.5 rounded-full bg-[#01C4A0]"
                style={{ animation: "pulseGlow 2.5s ease-in-out infinite", boxShadow: "0 0 6px rgba(1,196,160,0.6)" }} />
              <span className="text-[11px] font-mono text-[#3D5670]">live</span>
            </div>
            {(data || history.length > 0) && (
              <button onClick={() => { reset(); setHistory([]); }}
                className="btn-ghost text-[11px] rounded-full px-3 py-1">
                Clear
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 flex flex-col">
        <div className="w-full space-y-4 flex-1">

          {/* Hero */}
          {showHero && (
            <div className="flex flex-col items-center justify-center py-16 sm:py-24"
              style={{ animation: "fadeUp 0.5s ease both" }}>

              {/* Icon */}
              <div className="relative mb-8">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#01C4A0]/20 to-[#4BA8E8]/10 blur-xl scale-150" />
                <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-br from-[#01C4A0] to-[#4BA8E8] flex items-center justify-center shadow-lg">
                  <svg width="28" height="28" viewBox="0 0 16 16" fill="none">
                    <path d="M8 2L14 5.5V10.5L8 14L2 10.5V5.5L8 2Z" stroke="#050B12" strokeWidth="1.5" strokeLinejoin="round"/>
                    <path d="M8 6L10 7.5V10L8 11.5L6 10V7.5L8 6Z" fill="#050B12"/>
                  </svg>
                </div>
              </div>

              <h1 className="font-head text-[28px] sm:text-4xl font-bold text-center leading-[1.15] mb-3 tracking-tight">
                <span className="text-white">Ask anything.</span>
                <br />
                <span className="text-gradient-teal">Know what to trust.</span>
              </h1>

              <p className="text-[#3D5670] text-[13px] text-center max-w-sm leading-relaxed mb-10 font-mono">
                Dual-LLM · Web fact-check · Sentence-level trust · 0–100 score
              </p>

              {/* Chips */}
              <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                {SUGGESTED_QUERIES.map((q, i) => (
                  <button key={i} onClick={() => handleSubmit(q)}
                    className="text-[12px] px-3.5 py-1.5 rounded-full border border-[#1A2840]
                               text-[#4A6880] hover:text-[#01C4A0] hover:border-[#01C4A0]/30
                               hover:bg-[#01C4A0]/5 transition-all duration-200 active:scale-95"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Active states */}
          {loading && <LoadingState />}
          {error && !loading && <ErrorState message={error} onRetry={() => reset()} type={error.includes("timed out") ? "timeout" : "generic"} />}
          {data && !loading && <ChatMessage query={currentQuery} data={data} />}

          {/* History */}
          {history.length > 1 && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-3">
                <div className="flex-1 h-px" style={{ background: "linear-gradient(to right, transparent, #182030, transparent)" }} />
                <span className="text-[10px] font-mono text-[#2E4560] uppercase tracking-widest">Previous</span>
                <div className="flex-1 h-px" style={{ background: "linear-gradient(to right, #182030, transparent)" }} />
              </div>
              {history.slice(1).map((item, i) => (
                <HistoryEntry key={i} query={item.query} data={item.data} />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Sticky input */}
      <div className="sticky bottom-0 z-20 w-full">
        <div className="h-8 bg-gradient-to-t from-[#080E16] to-transparent pointer-events-none" />
        <div className="bg-[#080E16] pb-4 px-4 sm:px-0">
          <div className="max-w-3xl mx-auto sm:px-6">
            <ChatInput ref={inputRef} onSubmit={handleSubmit} loading={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}
