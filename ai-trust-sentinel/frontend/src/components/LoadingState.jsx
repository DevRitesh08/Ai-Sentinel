// frontend/src/components/LoadingState.jsx
import { useEffect, useState } from "react";

const PIPELINE_STAGES = [
  {
    id:    "cache",
    icon:  "⚡",
    label: "Checking query cache",
    sub:   "Looking for cached result to save API costs",
    color: "text-ats-blue",
    delay: 0,
  },
  {
    id:    "primary_llm",
    icon:  "🧠",
    label: "Primary LLM analysis",
    sub:   "GPT-4o-mini generating answer + confidence score",
    color: "text-ats-purple",
    delay: 300,
  },
  {
    id:    "gate",
    icon:  "🔀",
    label: "Confidence gate evaluation",
    sub:   "Deciding whether second model verification is needed",
    color: "text-ats-caution",
    delay: 1000,
  },
  {
    id:    "claims",
    icon:  "🔍",
    label: "Extracting factual claims",
    sub:   "Isolating the 3–5 key assertions for fact-checking",
    color: "text-ats-blue",
    delay: 1400,
  },
  {
    id:    "factcheck",
    icon:  "🌐",
    label: "Verifying against web sources",
    sub:   "Searching live sources for each extracted claim",
    color: "text-ats-mint",
    delay: 2000,
  },
  {
    id:    "score",
    icon:  "📊",
    label: "Computing Trust Score",
    sub:   "Aggregating all signals into 0–100 confidence rating",
    color: "text-ats-mint",
    delay: 2800,
  },
];

export default function LoadingState({ startTime }) {
  const [activeStage, setActiveStage] = useState(0);
  const [elapsedMs, setElapsedMs] = useState(0);

  // Animate through stages sequentially
  useEffect(() => {
    const timers = PIPELINE_STAGES.map((stage, i) =>
      setTimeout(() => setActiveStage(i), stage.delay)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  // Live elapsed time counter
  useEffect(() => {
    const start = startTime ?? Date.now();
    const ticker = setInterval(() => setElapsedMs(Date.now() - start), 100);
    return () => clearInterval(ticker);
  }, [startTime]);

  return (
    <div className="card p-5 sm:p-6 space-y-5 animate-fade-up">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-2.5 h-2.5 rounded-full bg-ats-mint" />
            <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-ats-mint animate-ping opacity-40" />
          </div>
          <span className="font-mono text-xs font-bold tracking-widest text-ats-mint uppercase">
            Pipeline Running
          </span>
        </div>
        <span className="font-mono text-xs text-ats-muted">
          {(elapsedMs / 1000).toFixed(1)}s elapsed
        </span>
      </div>

      {/* Stage list */}
      <div className="space-y-2.5">
        {PIPELINE_STAGES.map((stage, i) => {
          const isDone = i < activeStage;
          const isActive = i === activeStage;
          const isPending = i > activeStage;

          return (
            <div key={stage.id}
              className={`flex items-start gap-3 transition-all duration-300 ${isPending ? "opacity-25" : "opacity-100"}`}>
              {/* Icon / status indicator */}
              <div className={[
                "w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-sm transition-all duration-300",
                isDone && "bg-emerald-950/50 border border-ats-mint/40",
                isActive && "bg-ats-elevated border border-ats-blue/50",
                isPending && "bg-ats-elevated border border-ats-border",
              ].filter(Boolean).join(" ")}>
                {isDone
                  ? <span className="text-ats-mint text-xs font-bold">✓</span>
                  : isActive
                    ? <span className="text-sm animate-pulse">{stage.icon}</span>
                    : <span className="text-ats-dim text-[10px]">{i + 1}</span>
                }
              </div>

              {/* Stage text */}
              <div className="flex-1 pt-0.5">
                <div className={[
                  "text-xs font-mono font-semibold",
                  isDone && "text-ats-mint",
                  isActive && stage.color,
                  isPending && "text-ats-dim",
                ].filter(Boolean).join(" ")}>
                  {stage.label}
                  {isActive && <span className="animate-pulse ml-1">...</span>}
                </div>
                {(isActive || isDone) && (
                  <div className="text-[11px] text-ats-muted mt-0.5">
                    {stage.sub}
                  </div>
                )}
              </div>

              {/* Done indicator */}
              {isDone && (
                <span className="text-[10px] font-mono text-ats-dim pt-1">done</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Shimmer skeleton */}
      <div className="space-y-2 pt-3 border-t border-ats-border/50">
        <div className="text-[11px] text-ats-dim mb-2">Preparing response...</div>
        {[85, 95, 70, 90, 55].map((w, i) => (
          <div key={i} className="h-3 rounded-md"
            style={{
              width: `${w}%`,
              background: "linear-gradient(90deg, #1E2A3A 25%, #243040 50%, #1E2A3A 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.8s ease infinite",
              animationDelay: `${i * 120}ms`,
            }} />
        ))}
      </div>
    </div>
  );
}
