// frontend/src/utils/trustHelpers.js

export function getTrustConfig(score) {
  if (score >= 85) return {
    label:     "High Confidence",
    color:     "#01C4A0",
    textClass: "text-[#01C4A0]",
    tagline:   "Supported by external sources",
  };
  if (score >= 65) return {
    label:     "Moderate Confidence",
    color:     "#F0B43C",
    textClass: "text-[#F0B43C]",
    tagline:   "Partially supported — review sources",
  };
  if (score >= 45) return {
    label:     "Low Confidence",
    color:     "#E87830",
    textClass: "text-[#E87830]",
    tagline:   "Limited evidence — verify manually",
  };
  return {
    label:     "Unreliable",
    color:     "#F5505A",
    textClass: "text-[#F5505A]",
    tagline:   "Contradicted by credible sources",
  };
}

export function getStatusConfig(status) {
  switch (status?.toUpperCase()) {
    case "VERIFIED":
      return {
        underlineColor: "#01C4A0",
        badgeClass:    "badge-verified",
        dotColor:      "#01C4A0",
        label:         "Verified",
        tooltip:       "Supported by external sources",
        icon:          "✓",
      };
    case "UNCERTAIN":
      return {
        underlineColor: "#F0B43C",
        badgeClass:    "badge-uncertain",
        dotColor:      "#F0B43C",
        label:         "Uncertain",
        tooltip:       "No confirming sources found",
        icon:          "?",
      };
    case "CONTRADICTED":
      return {
        underlineColor: "#F5505A",
        badgeClass:    "badge-contradicted",
        dotColor:      "#F5505A",
        label:         "Contradicted",
        tooltip:       "Contradicted by credible sources",
        icon:          "✗",
      };
    default:
      return {
        underlineColor: "transparent",
        badgeClass:    "badge-neutral",
        dotColor:      "#3D5670",
        label:         "Unverified",
        tooltip:       "No matching claim extracted",
        icon:          "–",
      };
  }
}

export function formatLatency(ms) {
  if (!ms) return null;
  if (ms < 100)  return "instant";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function formatCacheAge(ms) {
  if (!ms) return "just now";
  const mins = Math.floor(ms / 60000);
  if (mins < 1)  return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}
