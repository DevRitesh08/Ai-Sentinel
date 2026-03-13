// frontend/src/utils/trustHelpers.js

/**
 * Trust score configuration — new redesign palette.
 */
export function getTrustConfig(score) {
  if (score >= 85) return {
    label:     "High Confidence",
    color:     "#01E6A8",
    bgClass:   "bg-emerald-950/40",
    textClass: "text-ats-mint",
    emoji:     "✓",
    tagline:   "Supported by external sources",
  };
  if (score >= 65) return {
    label:     "Moderate Confidence",
    color:     "#F5C156",
    bgClass:   "bg-yellow-950/30",
    textClass: "text-ats-caution",
    emoji:     "~",
    tagline:   "Partially supported — review sources",
  };
  if (score >= 45) return {
    label:     "Low Confidence",
    color:     "#FF9A3C",
    bgClass:   "bg-orange-950/30",
    textClass: "text-orange-400",
    emoji:     "!",
    tagline:   "Limited evidence — verify manually",
  };
  return {
    label:     "Unreliable",
    color:     "#FF6B6B",
    bgClass:   "bg-red-950/30",
    textClass: "text-ats-danger",
    emoji:     "✗",
    tagline:   "Contradicted by credible sources",
  };
}

/**
 * Sentence / claim status configuration — redesign palette.
 */
export function getStatusConfig(status) {
  switch (status?.toUpperCase()) {
    case "VERIFIED":
      return {
        highlightBg:   "bg-emerald-950/30",
        underlineColor: "#01E6A8",
        badgeClass:    "badge-verified",
        dotColor:      "#01E6A8",
        label:         "Verified",
        tooltip:       "Verified — supported by external sources",
        icon:          "✓",
      };
    case "UNCERTAIN":
      return {
        highlightBg:   "bg-yellow-950/25",
        underlineColor: "#F5C156",
        badgeClass:    "badge-uncertain",
        dotColor:      "#F5C156",
        label:         "Uncertain",
        tooltip:       "Uncertain — no confirming web sources found",
        icon:          "?",
      };
    case "CONTRADICTED":
      return {
        highlightBg:   "bg-red-950/30",
        underlineColor: "#FF6B6B",
        badgeClass:    "badge-contradicted",
        dotColor:      "#FF6B6B",
        label:         "Contradicted",
        tooltip:       "Contradicted by credible sources",
        icon:          "✗",
      };
    default:
      return {
        highlightBg:   "",
        underlineColor: "transparent",
        badgeClass:    "badge-neutral",
        dotColor:      "#64748B",
        label:         "Unverified",
        tooltip:       "No matching claim extracted",
        icon:          "–",
      };
  }
}

/**
 * Formats latency in ms to human-readable.
 */
export function formatLatency(ms) {
  if (!ms) return null;
  if (ms < 100)  return "instant";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

/**
 * Format a cache timestamp.
 */
export function formatCacheAge(ms) {
  if (!ms) return "just now";
  const mins = Math.floor(ms / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}
