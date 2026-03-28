import { useState } from "react";
import TrustScoreMeter from "./TrustScoreMeter";
import { formatLatency, getTrustConfig } from "../utils/trustHelpers";

function isResolvedQueryDifferent(rawQuery, resolvedQuery) {
  if (!rawQuery || !resolvedQuery) return false;
  const normalize = (value) => value.trim().toLowerCase().replace(/\s+/g, " ");
  return normalize(rawQuery) !== normalize(resolvedQuery);
}

export default function HistoryEntry({ query, data }) {
  const [expanded, setExpanded] = useState(false);
  const config = getTrustConfig(data.trust_score);
  const showResolvedQuery = data.used_context && isResolvedQueryDifferent(query, data.resolved_query);

  return (
    <div className="card transition-all duration-200 overflow-hidden">
      <button
        className="w-full flex items-center gap-3 sm:gap-4 p-3 sm:p-4 text-left hover:bg-ats-hover/30 transition-colors"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <span className={`font-mono font-bold text-lg w-10 flex-shrink-0 ${config.textClass}`}>
          {data.trust_score}
        </span>

        <span className="flex-1 text-sm text-ats-text truncate">{query}</span>

        <div className="flex items-center gap-2 flex-shrink-0">
          {data.used_context && <span className="text-xs text-ats-blue">ctx</span>}
          {data.from_cache && <span className="text-xs text-ats-mint">⚡</span>}
          <span className="text-[11px] font-mono text-ats-dim">{formatLatency(data.latency_ms)}</span>
          <span className={`text-ats-dim transition-transform duration-200 text-xs ${expanded ? "rotate-180" : ""}`}>
            ▾
          </span>
        </div>
      </button>

      {expanded && (
        <div className="border-t border-ats-border p-4 animate-fade-up">
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
            <div className="flex-1 space-y-3">
              {showResolvedQuery && (
                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-ats-dim">Verified as</span>
                  <p className="text-sm text-ats-muted leading-relaxed">{data.resolved_query}</p>
                </div>
              )}
              <div>
                {data.sentences?.map((sentence, index) => (
                  <span
                    key={index}
                    className={`text-sm leading-relaxed mr-1 ${
                      sentence.status === "VERIFIED"
                        ? "text-ats-mint"
                        : sentence.status === "CONTRADICTED"
                          ? "text-ats-danger"
                          : sentence.status === "UNCERTAIN"
                            ? "text-ats-caution"
                            : "text-ats-text"
                    }`}
                  >
                    {sentence.text}{" "}
                  </span>
                ))}
              </div>
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
