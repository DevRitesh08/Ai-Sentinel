// frontend/src/components/HistoryEntry.jsx
import { useState } from "react";
import TrustScoreMeter from "./TrustScoreMeter";
import { getTrustConfig, formatLatency } from "../utils/trustHelpers";

/**
 * A collapsed history entry that expands on click.
 */
export default function HistoryEntry({ query, data }) {
  const [expanded, setExpanded] = useState(false);
  const config = getTrustConfig(data.trust_score);

  return (
    <div className="card transition-all duration-200 overflow-hidden">
      {/* Collapsed header — always visible */}
      <button
        className="w-full flex items-center gap-3 sm:gap-4 p-3 sm:p-4 text-left hover:bg-ats-hover/30 transition-colors"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        {/* Score pill */}
        <span className={`font-mono font-bold text-lg w-10 flex-shrink-0 ${config.textClass}`}>
          {data.trust_score}
        </span>

        {/* Query text (truncated) */}
        <span className="flex-1 text-sm text-ats-text truncate">{query}</span>

        {/* Meta */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {data.from_cache && (
            <span className="text-xs text-ats-mint">⚡</span>
          )}
          <span className="text-[11px] font-mono text-ats-dim">
            {formatLatency(data.latency_ms)}
          </span>
          <span className={`text-ats-dim transition-transform duration-200 text-xs ${expanded ? "rotate-180" : ""}`}>
            ▾
          </span>
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-ats-border p-4 animate-fade-up">
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
            <div className="flex-1 space-y-1">
              {data.sentences?.map((s, i) => (
                <span key={i}
                  className={`text-sm leading-relaxed mr-1 ${
                    s.status === "VERIFIED"     ? "text-ats-mint" :
                    s.status === "CONTRADICTED" ? "text-ats-danger" :
                    s.status === "UNCERTAIN"    ? "text-ats-caution" :
                    "text-ats-text"
                  }`}
                >
                  {s.text}{" "}
                </span>
              ))}
            </div>
            <div className="flex-shrink-0">
              <TrustScoreMeter score={data.trust_score} size={80} animated={false} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
