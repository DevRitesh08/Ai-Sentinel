// frontend/src/components/TrustScoreMeter.jsx
import { useEffect, useState } from "react";
import { getTrustConfig } from "../utils/trustHelpers";

export default function TrustScoreMeter({ score, size = 120, animated = true }) {
  const [display, setDisplay] = useState(animated ? 0 : score);
  const config = getTrustConfig(score);

  useEffect(() => {
    if (!animated) { setDisplay(score); return; }
    let cur = 0;
    const steps = 40;
    const inc = score / steps;
    const id = setInterval(() => {
      cur += inc;
      if (cur >= score) { setDisplay(score); clearInterval(id); }
      else setDisplay(Math.floor(cur));
    }, 600 / steps);
    return () => clearInterval(id);
  }, [score, animated]);

  const r = (size / 2) - 8;
  const circ = 2 * Math.PI * r;
  const dash = (display / 100) * circ;
  const c = size / 2;

  return (
    <div className="flex flex-col items-center gap-1"
      style={{ animation: "scoreIn 0.6s cubic-bezier(0.34,1.56,0.64,1) both" }}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}
          className="-rotate-90" style={{ overflow: "visible" }}>
          {/* Track */}
          <circle cx={c} cy={c} r={r} fill="none"
            stroke="#141F2D" strokeWidth="5" />
          {/* Arc */}
          <circle cx={c} cy={c} r={r} fill="none"
            stroke={config.color} strokeWidth="5" strokeLinecap="round"
            strokeDasharray={`${dash} ${circ}`}
            style={{
              transition: "stroke-dasharray 0.06s linear",
              filter: `drop-shadow(0 0 5px ${config.color}50)`,
            }}
          />
        </svg>
        {/* Center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-head font-bold leading-none tabular-nums"
            style={{ fontSize: size * 0.31, color: config.color }}>
            {display}
          </span>
          <span className="font-mono" style={{ fontSize: size * 0.14, color: "#2E4560" }}>
            /100
          </span>
        </div>
      </div>
      <span className="font-mono font-semibold tracking-widest uppercase"
        style={{ fontSize: size * 0.115, color: config.color, opacity: 0.85 }}>
        {config.label}
      </span>
    </div>
  );
}
