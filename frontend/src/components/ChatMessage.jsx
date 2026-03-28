import { useState } from "react";
import InspectPanel from "./InspectPanel";
import SentenceText from "./SentenceText";
import SourceChainDrawer from "./SourceChainDrawer";
import TrustScoreMeter from "./TrustScoreMeter";
import { formatLatency, getTrustConfig } from "../utils/trustHelpers";

function isResolvedQueryDifferent(rawQuery, resolvedQuery) {
  if (!rawQuery || !resolvedQuery) return false;
  const normalize = (value) => value.trim().toLowerCase().replace(/\s+/g, " ");
  return normalize(rawQuery) !== normalize(resolvedQuery);
}

export default function ChatMessage({ query, data }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [inspectSentence, setInspectSentence] = useState(null);
  const [copied, setCopied] = useState(false);

  if (!data) return null;

  const verifiedCount = data.claims?.filter((claim) => claim.status === "VERIFIED").length || 0;
  const totalClaims = data.claims?.length || 0;
  const trustConfig = getTrustConfig(data.trust_score);
  const showResolvedQuery = data.used_context && isResolvedQueryDifferent(query, data.resolved_query);

  const handleCopy = () => {
    navigator.clipboard.writeText(data.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <>
      <div className="space-y-3" style={{ animation: "fadeUp 0.35s ease both" }}>
        <div className="flex justify-end">
          <div
            className="max-w-[82%] sm:max-w-lg px-4 py-2.5 rounded-2xl rounded-br-md text-[13.5px] text-[#C8D8E8]"
            style={{ background: "#111E2C", border: "1px solid #1A2D40" }}
          >
            {query}
          </div>
        </div>

        {showResolvedQuery && (
          <div className="flex justify-start">
            <div
              className="max-w-[92%] px-4 py-2.5 rounded-2xl rounded-bl-md text-[12.5px]"
              style={{ background: "#0D1520", border: "1px solid #182030" }}
            >
              <span className="block text-[10px] font-mono uppercase tracking-wider text-[#4A6880] mb-1">
                Verified as
              </span>
              <span className="text-[#C8D8E8]">{data.resolved_query}</span>
            </div>
          </div>
        )}

        <div className="card overflow-hidden" style={{ borderColor: "#182030" }}>
          <div className="flex items-center gap-4 px-5 py-4 border-b border-[#182030]" style={{ background: "rgba(8,14,22,0.5)" }}>
            <TrustScoreMeter score={data.trust_score} size={52} />

            <div className="flex-1 min-w-0 space-y-1.5">
              <div className="flex items-center flex-wrap gap-1.5">
                <span className="text-[12px] font-medium" style={{ color: trustConfig.color }}>
                  {trustConfig.label}
                </span>
                {data.verifier_used && (
                  <span className="badge-dual text-[10px]">
                    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M9 9h.01M15 9h.01M8 14s1.5 2 4 2 4-2 4-2" />
                    </svg>
                    dual-LLM
                  </span>
                )}
                {data.used_context && (
                  <span className="badge-info text-[10px]">
                    follow-up {data.context_turns_used > 0 ? `${data.context_turns_used} turn${data.context_turns_used !== 1 ? "s" : ""}` : ""}
                  </span>
                )}
                {data.from_cache && <span className="badge-info text-[10px]">cached</span>}
                {data.bias_score != null && data.bias_score > 25 && (
                  <span className="badge-uncertain text-[10px]">bias {data.bias_score}</span>
                )}
                {data.intent_aligned === false && (
                  <span className="badge-contradicted text-[10px]">intent drift</span>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[11px] font-mono text-[#3D5670]">Trust Sentinel</span>
                {data.latency_ms > 0 && (
                  <span className="text-[11px] font-mono text-[#2E4560]">{formatLatency(data.latency_ms)}</span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-1 flex-shrink-0">
              {totalClaims > 0 && (
                <button
                  onClick={() => setDrawerOpen(true)}
                  className="btn-ghost text-[11px] rounded-xl px-2.5 py-1.5 gap-1.5"
                >
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
                  </svg>
                  <span className="hidden sm:inline">
                    {verifiedCount}/{totalClaims}
                  </span>
                  <span className="sm:hidden">{totalClaims}</span>
                </button>
              )}
            </div>
          </div>

          <div className="px-5 py-5">
            <SentenceText
              sentences={data.sentences}
              onInspect={(sentence) => setInspectSentence(sentence)}
            />
          </div>

          <div className="flex items-center justify-between px-5 py-3 border-t border-[#182030]/60">
            {totalClaims > 0 ? (
              <button
                onClick={() => setDrawerOpen(true)}
                className="flex items-center gap-2 text-[11.5px] text-[#3D5670] hover:text-[#4BA8E8] transition-colors"
              >
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: trustConfig.color }} />
                {totalClaims} claim{totalClaims !== 1 ? "s" : ""} verified · view sources
              </button>
            ) : (
              <span />
            )}

            <button onClick={handleCopy} className="btn-ghost text-[11px] rounded-lg px-2.5 py-1 gap-1.5">
              {copied ? (
                <>
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#01C4A0" strokeWidth="2.5">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  <span className="text-[#01C4A0]">Copied</span>
                </>
              ) : (
                <>
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" />
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                  </svg>
                  Copy
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <SourceChainDrawer claims={data.claims} isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
      <InspectPanel sentence={inspectSentence} isOpen={!!inspectSentence} onClose={() => setInspectSentence(null)} />
    </>
  );
}
