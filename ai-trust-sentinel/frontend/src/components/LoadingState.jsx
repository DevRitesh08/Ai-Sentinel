// frontend/src/components/LoadingState.jsx
import { useEffect, useState, useRef } from "react";

const THOUGHTS = [
  { delay: 0,    text: "Checking query cache for prior results…" },
  { delay: 600,  text: "Calling primary LLM — generating answer with confidence score…" },
  { delay: 1400, text: "Evaluating confidence gate — is a second opinion needed?" },
  { delay: 2100, text: "Extracting 3–5 independently verifiable factual claims…" },
  { delay: 2900, text: "Cross-referencing claims against live web sources via Tavily…" },
  { delay: 3700, text: "Running bias scan and intent alignment check in parallel…" },
  { delay: 4500, text: "Aggregating all signals into a composite Trust Score (0–100)…" },
];

function TypewriterLine({ text, active }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const idx = useRef(0);

  useEffect(() => {
    if (!active) return;
    idx.current = 0;
    setDisplayed("");
    setDone(false);

    const interval = setInterval(() => {
      idx.current++;
      setDisplayed(text.slice(0, idx.current));
      if (idx.current >= text.length) {
        clearInterval(interval);
        setDone(true);
      }
    }, 18);
    return () => clearInterval(interval);
  }, [active, text]);

  if (!active && displayed === "") return null;

  return (
    <span>
      {displayed}
      {active && !done && (
        <span className="inline-block w-0.5 h-3.5 bg-current ml-px align-middle animate-[caretBlink_0.8s_ease_infinite]" />
      )}
    </span>
  );
}

export default function LoadingState() {
  const [visibleThoughts, setVisibleThoughts] = useState([]);
  const [activeIdx, setActiveIdx] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [expanded, setExpanded] = useState(true);
  const startRef = useRef(Date.now());
  const bottomRef = useRef(null);

  useEffect(() => {
    const timers = THOUGHTS.map((t, i) =>
      setTimeout(() => {
        setVisibleThoughts(prev => [...prev, { ...t, id: i }]);
        setActiveIdx(i);
      }, t.delay)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  useEffect(() => {
    const tick = setInterval(() => setElapsed(Date.now() - startRef.current), 100);
    return () => clearInterval(tick);
  }, []);

  useEffect(() => {
    if (expanded) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [visibleThoughts, expanded]);

  return (
    <div className="space-y-3 animate-[fadeUp_0.3s_ease_both]">
      {/* Thinking block — Claude-style */}
      <div className="rounded-2xl border border-[#1E2E40] bg-[#0D1520] overflow-hidden">
        {/* Header bar */}
        <button
          onClick={() => setExpanded(e => !e)}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/[0.02] transition-colors group"
        >
          <div className="flex items-center gap-2.5">
            {/* Animated orb */}
            <div className="relative flex items-center justify-center w-5 h-5">
              <div className="absolute w-5 h-5 rounded-full bg-[#01C4A0]/20 animate-[ping_1.5s_ease_infinite]" />
              <div className="relative w-2.5 h-2.5 rounded-full bg-[#01C4A0]" />
            </div>
            <span className="text-[13px] font-medium text-[#8BA5BE] tracking-wide">
              Thinking
            </span>
            <span className="flex gap-0.5 items-end h-3 ml-0.5">
              {[0,1,2].map(i => (
                <span key={i}
                  className="w-0.5 rounded-full bg-[#01C4A0]/70"
                  style={{
                    height: "100%",
                    animation: `thinkDot 1.2s ease-in-out infinite`,
                    animationDelay: `${i * 0.2}s`,
                  }}
                />
              ))}
            </span>
            <span className="text-[11px] font-mono text-[#3D5670] ml-1">
              {(elapsed / 1000).toFixed(1)}s
            </span>
          </div>

          <svg
            className={`w-3.5 h-3.5 text-[#3D5670] transition-transform duration-200 ${expanded ? "" : "-rotate-90"}`}
            viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>

        {/* Thought stream */}
        {expanded && (
          <div className="px-4 pb-4 space-y-2 max-h-52 overflow-y-auto scrollbar-thin">
            <div className="w-full h-px bg-[#1A2840] mb-3" />
            {visibleThoughts.map((thought, i) => {
              const isActive = i === activeIdx && i === visibleThoughts.length - 1;
              const isDone = !isActive;
              return (
                <div key={thought.id}
                  className="flex items-start gap-2.5"
                  style={{ animation: "fadeUp 0.25s ease both" }}
                >
                  <div className="flex-shrink-0 mt-1">
                    {isDone ? (
                      <svg className="w-3 h-3 text-[#01C4A0]/60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    ) : (
                      <div className="w-1.5 h-1.5 rounded-full bg-[#01C4A0] mt-0.5 animate-pulse" />
                    )}
                  </div>
                  <p className={`text-[12.5px] leading-relaxed font-mono ${isDone ? "text-[#3D5670]" : "text-[#7BA0B8]"}`}>
                    <TypewriterLine text={thought.text} active={isActive} />
                    {isDone && thought.text}
                  </p>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Skeleton answer preview */}
      <div className="rounded-2xl border border-[#1A2535] bg-[#0F1A25]/80 p-5 space-y-3">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1.5 h-1.5 rounded-full bg-[#01C4A0]/40 animate-pulse" />
          <span className="text-[11px] font-mono text-[#2E4560] uppercase tracking-widest">Generating response</span>
        </div>
        {[92, 100, 78, 88, 60].map((w, i) => (
          <div key={i}
            className="h-[13px] rounded-lg overflow-hidden"
            style={{ width: `${w}%` }}
          >
            <div
              className="w-full h-full"
              style={{
                background: "linear-gradient(90deg, #111E2C 0%, #1A2D3E 45%, #111E2C 100%)",
                backgroundSize: "300% 100%",
                animation: `shimmer 2s ease infinite`,
                animationDelay: `${i * 150}ms`,
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
