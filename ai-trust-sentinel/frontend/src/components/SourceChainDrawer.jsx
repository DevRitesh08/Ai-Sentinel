// frontend/src/components/SourceChainDrawer.jsx
import { useEffect, useRef } from "react";
import { getStatusConfig } from "../utils/trustHelpers";

/**
 * Source Chain — slide-over drawer from the right.
 * Shows all extracted claims, status badges, evidence snippets, and source links.
 */
export default function SourceChainDrawer({ claims, isOpen, onClose }) {
  const drawerRef = useRef(null);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  // Focus trap — focus drawer on open
  useEffect(() => {
    if (isOpen) drawerRef.current?.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  const verifiedCount = claims?.filter(c => c.status === "VERIFIED").length || 0;
  const uncertainCount = claims?.filter(c => c.status === "UNCERTAIN").length || 0;
  const contradictedCount = claims?.filter(c => c.status === "CONTRADICTED").length || 0;

  return (
    <>
      {/* Backdrop */}
      <div className="overlay animate-fade-in" onClick={onClose} />

      {/* Drawer */}
      <div ref={drawerRef} tabIndex={-1}
        className="drawer w-full max-w-md p-6 animate-slide-right outline-none"
        role="dialog" aria-label="Source Chain">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-head text-lg font-bold text-white">Source Chain</h2>
            <p className="text-ats-muted text-xs mt-0.5">
              {claims?.length || 0} claim{claims?.length !== 1 ? "s" : ""} extracted &amp; verified
            </p>
          </div>
          <button onClick={onClose}
            className="btn-ghost rounded-full w-8 h-8 flex items-center justify-center text-lg"
            aria-label="Close source chain">
            ✕
          </button>
        </div>

        {/* Summary strip */}
        <div className="flex items-center gap-2 mb-5 flex-wrap">
          {verifiedCount > 0 && <span className="badge-verified">{verifiedCount} verified</span>}
          {uncertainCount > 0 && <span className="badge-uncertain">{uncertainCount} uncertain</span>}
          {contradictedCount > 0 && <span className="badge-contradicted">{contradictedCount} contradicted</span>}
        </div>

        {/* Claim list */}
        <div className="space-y-3">
          {claims?.map((claim, idx) => (
            <ClaimCard key={idx} claim={claim} index={idx} />
          ))}
        </div>

        {!claims?.length && (
          <p className="text-ats-muted text-sm text-center py-8">No claims extracted.</p>
        )}
      </div>
    </>
  );
}

function ClaimCard({ claim, index }) {
  const config = getStatusConfig(claim.status);
  const hasSource = !!claim.source_url;

  return (
    <div className="rounded-xl border border-ats-border bg-ats-elevated/60 p-4 transition-all duration-150
                    hover:border-ats-hover animate-slide-up"
         style={{ animationDelay: `${index * 60}ms` }}>

      {/* Top row: number + status */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-start gap-2.5 flex-1">
          <span className="font-mono text-xs text-ats-dim mt-0.5 w-5 flex-shrink-0">{index + 1}.</span>
          <div className="w-2 h-2 rounded-full flex-shrink-0 mt-1.5" style={{ background: config.dotColor }} />
          <p className="text-sm text-ats-text leading-relaxed">{claim.text}</p>
        </div>
        <span className={`${config.badgeClass} flex-shrink-0 text-[10px]`}>
          {config.icon} {config.label}
        </span>
      </div>

      {/* Source info */}
      {hasSource ? (
        <div className="ml-8 mt-2 space-y-1">
          {claim.source_title && (
            <p className="text-xs text-ats-muted truncate">{claim.source_title}</p>
          )}
          <a href={claim.source_url} target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-ats-blue hover:underline font-mono break-all"
            onClick={(e) => e.stopPropagation()}>
            <span className="text-[10px]">↗</span>
            <span className="truncate max-w-[280px]">{claim.source_url}</span>
          </a>
        </div>
      ) : (
        <p className="ml-8 mt-2 text-xs text-ats-dim font-mono">No web source found</p>
      )}
    </div>
  );
}
