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
  "Did Napoleon Bonaparte have a short stature?",
  "Was the Eiffel Tower supposed to be permanent?",
  "Can you survive a fall from any height into water?",
  "Do humans only use 10% of their brain?",
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
    <div className="min-h-screen flex flex-col">
      {/* Sticky header */}
      <header className="border-b border-ats-border/50 bg-ats-surface/80 backdrop-blur-md sticky top-0 z-30">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-3 sm:py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {/* Logo mark */}
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-ats-mint to-ats-blue
                            flex items-center justify-center shadow-glow-mint">
              <span className="text-ats-bg font-head font-bold text-xs">AT</span>
            </div>
            <span className="font-head text-sm font-bold text-white tracking-tight">
              Trust Sentinel
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:block text-[11px] text-ats-dim">
              The trust layer AI never gave you.
            </span>
            <span className="sm:hidden font-mono text-[10px] text-ats-dim">
              Trust · Verify · Source
            </span>
            <div className="w-1.5 h-1.5 rounded-full bg-ats-mint animate-pulse-dot ml-2 sm:ml-2" />
          </div>
        </div>
      </header>

      {/* Main content area */}
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 space-y-4 sm:space-y-5 flex flex-col items-center">
        <div className="w-full max-w-3xl space-y-5">
          {/* Hero / Landing state */}
          {showHero && (
            <div className="flex flex-col items-center justify-center py-10 sm:py-24 animate-fade-up">
              {/* Logo mark large */}
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-ats-mint to-ats-blue
                              flex items-center justify-center mb-6 sm:mb-8 shadow-glow-mint hover:animate-glow transition-all">
                <span className="text-ats-bg font-head font-bold text-xl">AT</span>
              </div>

              <h1 className="font-head text-3xl sm:text-4xl font-bold text-center leading-tight mb-3">
                <span className="text-white">Ask anything.</span>
                <br />
                <span className="text-gradient-mint">Know what to trust.</span>
              </h1>

              <p className="text-ats-muted text-xs sm:text-sm text-center max-w-sm leading-relaxed mb-8 font-mono">
                Dual-LLM cross-verification · Real-time fact-checking · Sentence-level trust scoring
              </p>

              {/* Suggested queries */}
              <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                {SUGGESTED_QUERIES.map((q, i) => (
                  <button key={i} onClick={() => handleSubmit(q)}
                    className="text-[11px] sm:text-xs px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-xl border border-ats-border
                               text-ats-muted hover:text-ats-mint hover:border-ats-mint/40
                               transition-all duration-200 hover:bg-ats-mint/5 active:scale-95 text-left sm:text-center">
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
            <div className="space-y-3 sm:space-y-4 pt-2">
              <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-ats-border/50" />
                <span className="text-[10px] sm:text-[11px] font-mono text-ats-dim uppercase tracking-wider">Previous queries</span>
                <div className="flex-1 h-px bg-ats-border/50" />
              </div>
              {history.slice(1).map((item, i) => (
                <HistoryEntry key={i} query={item.query} data={item.data} />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Sticky input */}
      <div className="sticky bottom-0 bg-ats-bg/90 sm:bg-gradient-to-t from-ats-bg via-ats-bg to-transparent backdrop-blur-md sm:backdrop-blur-none border-t border-ats-border sm:border-t-0 p-3 pb-safe sm:p-0 sm:pt-6 sm:pb-5 z-20 w-full">
        <div className="max-w-3xl mx-auto px-1 sm:px-5">
          <ChatInput ref={inputRef} onSubmit={handleSubmit} loading={loading} />
        </div>
      </div>
    </div>
  );
}
