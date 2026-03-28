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

export function getResponseStatusConfig(data) {
  const reason = data?.degraded_reason;
  const source = data?.answer_source;
  const status = data?.status ?? "ok";

  if (status === "ok" && source === "primary") {
    return null;
  }

  if (reason === "quota_exceeded") {
    return {
      label: "Provider limit reached",
      message: source === "offline_demo"
        ? "Primary provider quota was exhausted, so a matching demo response is being shown instead."
        : source === "ollama_fallback"
          ? "Primary provider quota was exhausted, so this answer came from a local fallback model and may have limited verification."
          : "Primary provider quota was exhausted. Retry in a bit for a live verified answer.",
      color: "#F0B43C",
    };
  }

  if (source === "offline_demo" || reason === "offline_demo") {
    return {
      label: "Demo response",
      message: "This answer came from a precomputed demo response rather than a live provider call.",
      color: "#4BA8E8",
    };
  }

  if (source === "ollama_fallback") {
    return {
      label: "Local fallback answer",
      message: "The primary provider was unavailable, so this answer came from a local fallback model and may have limited verification.",
      color: "#4BA8E8",
    };
  }

  if (reason === "timeout") {
    return {
      label: "Provider timed out",
      message: "The upstream model took too long to respond. Retry for a fully verified answer.",
      color: "#F0B43C",
    };
  }

  if (reason === "malformed_response") {
    return {
      label: "Provider response issue",
      message: "The upstream model returned an unreadable response. The answer below is a degraded fallback.",
      color: "#F0B43C",
    };
  }

  if (status === "error") {
    return {
      label: "Provider unavailable",
      message: "No fallback answer source was available, so the result below is an outage message rather than a verified answer.",
      color: "#F5505A",
    };
  }

  return {
    label: "Degraded response",
    message: "This result was generated in a degraded mode. Treat it as lower-confidence than a normal verified answer.",
    color: "#F0B43C",
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
