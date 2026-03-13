// frontend/src/components/ErrorState.jsx

export default function ErrorState({ message, onRetry, type = "generic" }) {
  const configs = {
    timeout: {
      icon: "⏱",
      title: "Pipeline Timed Out",
      hint: "The pipeline took too long. This sometimes happens during peak load.",
      action: "Try again",
    },
    network: {
      icon: "📡",
      title: "Connection Failed",
      hint: "Cannot reach the backend API. Check if the server is running.",
      action: "Retry",
    },
    rate_limit: {
      icon: "🔄",
      title: "Rate Limited",
      hint: "Too many requests. Wait a moment before trying again.",
      action: "Wait and retry",
    },
    generic: {
      icon: "⚠",
      title: "Pipeline Error",
      hint: message ?? "Something went wrong. The team has been notified.",
      action: "Try again",
    },
  };

  const config = configs[type] ?? configs.generic;

  return (
    <div className="card p-5 border-ats-danger/30 bg-red-950/10 animate-fade-up space-y-3">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-red-950/50 flex items-center justify-center flex-shrink-0">
          <span className="text-base">{config.icon}</span>
        </div>
        <div className="flex-1">
          <p className="font-mono text-xs text-ats-danger font-bold tracking-wider uppercase mb-1">
            {config.title}
          </p>
          <p className="text-sm text-ats-text leading-relaxed">
            {config.hint}
          </p>
        </div>
      </div>

      {onRetry && (
        <button onClick={onRetry}
          className="btn-primary text-xs px-4 py-2">
          ↻ {config.action}
        </button>
      )}
    </div>
  );
}
