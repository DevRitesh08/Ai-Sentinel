// frontend/src/components/ErrorState.jsx
export default function ErrorState({ message, onRetry, type = "generic" }) {
  const configs = {
    timeout: {
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F0B43C" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
      ),
      title: "Pipeline Timed Out",
      hint: "The pipeline took too long. This can happen during peak load — try again.",
      color: "#F0B43C",
    },
    network: {
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F5505A" strokeWidth="2">
          <line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0119 12.55M5 12.55a10.94 10.94 0 015.17-2.39M10.71 5.05A16 16 0 0122.56 9M1.42 9a15.91 15.91 0 014.7-2.88M8.53 16.11a6 6 0 016.95 0M12 20h.01"/>
        </svg>
      ),
      title: "Connection Failed",
      hint: "Cannot reach the backend. Check if the server is running on port 8000.",
      color: "#F5505A",
    },
    generic: {
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F5505A" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      ),
      title: "Pipeline Error",
      hint: message ?? "Something went wrong. Please try again.",
      color: "#F5505A",
    },
  };

  const cfg = configs[type] ?? configs.generic;

  return (
    <div className="card p-5 space-y-4" style={{ borderColor: `${cfg.color}22`, animation: "fadeUp 0.3s ease both" }}>
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ background: `${cfg.color}12` }}>
          {cfg.icon}
        </div>
        <div className="flex-1 pt-0.5">
          <p className="font-mono text-[11px] font-bold tracking-widest uppercase mb-1.5" style={{ color: cfg.color }}>
            {cfg.title}
          </p>
          <p className="text-[13.5px] text-[#8BA5BE] leading-relaxed">{cfg.hint}</p>
        </div>
      </div>
      {onRetry && (
        <button onClick={onRetry}
          className="flex items-center gap-2 text-[12px] font-medium px-4 py-2 rounded-xl transition-all duration-200"
          style={{ background: `${cfg.color}12`, color: cfg.color, border: `1px solid ${cfg.color}25` }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/>
          </svg>
          Try again
        </button>
      )}
    </div>
  );
}
