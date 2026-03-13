// frontend/src/components/ChatMessage.jsx
import { useState } from "react";
import TrustScoreMeter from "./TrustScoreMeter";
import SentenceText from "./SentenceText";
import SourceChainDrawer from "./SourceChainDrawer";
import InspectPanel from "./InspectPanel";
import { getTrustConfig, formatLatency } from "../utils/trustHelpers";

/**
 * Full response container — trust-forward layout.
 * Trust Score ribbon at top, answer with inline sentence badges,
 * quick actions, bias/intent indicators, and triggers for drawers.
 */
export default function ChatMessage({ query, data }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [inspectSentence, setInspectSentence] = useState(null);

  if (!data) return null;

  const verifiedCount = data.claims?.filter(c => c.status === "VERIFIED").length || 0;
  const totalClaims = data.claims?.length || 0;
  const trustConfig = getTrustConfig(data.trust_score);

  return (
    <>
      <div className="space-y-3 sm:space-y-4 animate-fade-up">
        {/* User query */}
        <div className="flex justify-end">
          <div className="card px-3 py-2 sm:px-4 sm:py-3 max-w-[85%] sm:max-w-lg bg-ats-elevated border-ats-blue/20">
            <p className="text-sm text-ats-text">{query}</p>
          </div>
        </div>

        {/* Response card */}
        <div className="card p-0 overflow-hidden">
          {/* Trust Score ribbon at top */}
          <div className="flex items-center justify-between px-4 sm:px-5 py-3 border-b border-ats-border bg-ats-bg/50">
            <div className="flex items-center gap-3 sm:gap-4">
              {/* Compact score */}
              <TrustScoreMeter score={data.trust_score} size={48} />

              {/* Meta */}
              <div className="space-y-0.5">
                <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                  <span className="text-[11px] text-ats-muted">AI Trust Sentinel</span>
                  {data.verifier_used && (
                    <span className="badge-verified text-[10px]">dual-LLM</span>
                  )}
                  {data.from_cache && (
                    <span className="badge-info text-[10px]">⚡ cached</span>
                  )}
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {data.latency_ms > 0 && (
                    <span className="text-[11px] font-mono text-ats-dim">
                      {formatLatency(data.latency_ms)}
                    </span>
                  )}
                  {data.bias_score != null && data.bias_score > 25 && (
                    <span className="badge-uncertain text-[10px]">⚠ bias {data.bias_score}</span>
                  )}
                  {data.intent_aligned === false && (
                    <span className="badge-contradicted text-[10px]">✗ intent drift</span>
                  )}
                </div>
              </div>
            </div>

            {/* Quick actions */}
            <div className="flex items-center gap-1">
              {totalClaims > 0 && (
                <button onClick={() => setDrawerOpen(true)}
                  className="btn-ghost text-xs rounded-lg px-2 sm:px-3 py-1.5 text-ats-blue">
                  <span className="hidden sm:inline">{verifiedCount}/{totalClaims} sources</span>
                  <span className="sm:hidden">{totalClaims} ↗</span>
                </button>
              )}
            </div>
          </div>

          {/* Answer body with sentence highlighting */}
          <div className="px-4 sm:px-5 py-4 sm:py-5">
            <SentenceText
              sentences={data.sentences}
              onInspect={(sentence) => setInspectSentence(sentence)}
            />
          </div>

          {/* Bottom bar */}
          {totalClaims > 0 && (
            <div className="px-4 sm:px-5 py-2.5 border-t border-ats-border/50 flex items-center justify-between">
              <button onClick={() => setDrawerOpen(true)}
                className="flex items-center gap-2 text-xs text-ats-muted hover:text-ats-blue transition-colors">
                <span className="w-1.5 h-1.5 rounded-full bg-ats-mint" />
                View Source Chain · {totalClaims} claim{totalClaims !== 1 ? "s" : ""}
              </button>
              <button className="btn-ghost text-xs rounded-lg px-2.5 py-1"
                onClick={() => navigator.clipboard.writeText(data.answer)}>
                Copy
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Source Chain drawer */}
      <SourceChainDrawer
        claims={data.claims}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />

      {/* Deep-inspect panel */}
      <InspectPanel
        sentence={inspectSentence}
        isOpen={!!inspectSentence}
        onClose={() => setInspectSentence(null)}
      />
    </>
  );
}
