// frontend/src/components/InspectPanel.jsx
import { useEffect, useRef } from "react";
import { getStatusConfig } from "../utils/trustHelpers";

/**
 * Deep-inspect slide-over — opens when user clicks a highlighted sentence.
 * Shows extracted claim, evidence, source link, and model agreement info.
 */
export default function InspectPanel({ sentence, isOpen, onClose }) {
  const panelRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen) panelRef.current?.focus();
  }, [isOpen]);

  if (!isOpen || !sentence) return null;

  const config = getStatusConfig(sentence.status);
  const hasSource = !!sentence.source_url;

  return (
    <>
      <div className="overlay animate-fade-in" onClick={onClose} />

      <div ref={panelRef} tabIndex={-1}
        className="drawer w-full max-w-sm p-6 animate-slide-right outline-none"
        role="dialog" aria-label="Claim inspection">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-head text-base font-bold text-white">Inspect Claim</h2>
          <button onClick={onClose}
            className="btn-ghost rounded-full w-8 h-8 flex items-center justify-center text-lg"
            aria-label="Close">✕</button>
        </div>

        {/* Status badge */}
        <div className="mb-5">
          <span className={`${config.badgeClass} text-sm px-3 py-1.5`}>
            {config.icon} {config.label}
          </span>
        </div>

        {/* Sentence text */}
        <div className="mb-5">
          <p className="text-xs font-mono text-ats-dim uppercase tracking-wider mb-2">Sentence</p>
          <p className="text-sm text-ats-text leading-relaxed p-3 rounded-xl bg-ats-elevated border border-ats-border">
            "{sentence.text}"
          </p>
        </div>

        {/* Matched claim */}
        {sentence.claim_ref && (
          <div className="mb-5">
            <p className="text-xs font-mono text-ats-dim uppercase tracking-wider mb-2">Extracted Claim</p>
            <p className="text-sm text-ats-muted leading-relaxed p-3 rounded-xl bg-ats-bg border border-ats-border">
              {sentence.claim_ref}
            </p>
          </div>
        )}

        {/* Evidence / source */}
        <div className="mb-5">
          <p className="text-xs font-mono text-ats-dim uppercase tracking-wider mb-2">Source Evidence</p>
          {hasSource ? (
            <a href={sentence.source_url} target="_blank" rel="noopener noreferrer"
              className="flex items-start gap-3 p-3 rounded-xl bg-ats-elevated border border-ats-border
                         hover:border-ats-blue/40 transition-colors group">
              <div className="w-8 h-8 rounded-lg bg-ats-blue/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-ats-blue text-xs">↗</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-ats-text group-hover:text-ats-blue transition-colors truncate">
                  {new URL(sentence.source_url).hostname.replace("www.", "")}
                </p>
                <p className="text-xs text-ats-dim font-mono mt-0.5 truncate">{sentence.source_url}</p>
              </div>
            </a>
          ) : (
            <div className="p-3 rounded-xl bg-ats-bg border border-ats-border">
              <p className="text-sm text-ats-dim">No source URL available for this claim.</p>
            </div>
          )}
        </div>

        {/* Confidence visualization placeholder */}
        <div className="pt-4 border-t border-ats-border">
          <p className="text-xs font-mono text-ats-dim uppercase tracking-wider mb-3">Trust Signal</p>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-2 bg-ats-border rounded-full overflow-hidden">
              <div className="h-full rounded-full transition-all duration-500"
                style={{
                  width: sentence.status === "VERIFIED" ? "90%" :
                         sentence.status === "UNCERTAIN" ? "50%" :
                         sentence.status === "CONTRADICTED" ? "15%" : "30%",
                  background: config.dotColor,
                  boxShadow: `0 0 8px ${config.dotColor}40`,
                }} />
            </div>
            <span className="text-xs font-mono" style={{ color: config.dotColor }}>
              {config.label}
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
