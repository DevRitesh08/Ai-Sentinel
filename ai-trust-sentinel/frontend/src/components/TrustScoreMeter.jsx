// frontend/src/components/TrustScoreMeter.jsx
import { useEffect, useState } from "react";
import { getTrustConfig } from "../utils/trustHelpers";

/**
 * Trust Score ribbon / card — designed as a compact trust-forward widget.
 * Shows animated score, color-coded ring, label, and tagline.
 */
export default function TrustScoreMeter({ score, size = 120, animated = true }) {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);
  const config = getTrustConfig(score);

  useEffect(() => {
    if (!animated) { setDisplayScore(score); return; }

    let current = 0;
    const target = score;
    const steps = 50;
    const increment = target / steps;
    const interval = 700 / steps;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setDisplayScore(target);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(current));
      }
    }, interval);

    return () => clearInterval(timer);
  }, [score, animated]);

  const radius = (size / 2) - 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDash = (displayScore / 100) * circumference;
  const center = size / 2;

  return (
    <div className="flex flex-col items-center gap-2 animate-score-in" title={`Trust Score (0–100): ${config.tagline}`}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
          {/* Background ring */}
          <circle cx={center} cy={center} r={radius} fill="none"
            stroke="#1E2A3A" strokeWidth="6" />
          {/* Score arc */}
          <circle cx={center} cy={center} r={radius} fill="none"
            stroke={config.color} strokeWidth="6" strokeLinecap="round"
            strokeDasharray={`${strokeDash} ${circumference}`}
            style={{
              transition: "stroke-dasharray 0.08s linear",
              filter: `drop-shadow(0 0 6px ${config.color}50)`,
            }}
          />
        </svg>
        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-head font-bold leading-none"
            style={{ fontSize: size * 0.32, color: config.color, textShadow: `0 0 16px ${config.color}30` }}>
            {displayScore}
          </span>
          <span className="text-ats-dim font-mono" style={{ fontSize: size * 0.085 }}>/100</span>
        </div>
      </div>
      {/* Trust label */}
      <span className={`font-mono text-[10px] font-semibold tracking-widest uppercase ${config.textClass}`}>
        {config.label}
      </span>
    </div>
  );
}
