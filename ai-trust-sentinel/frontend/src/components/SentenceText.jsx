// frontend/src/components/SentenceText.jsx
import { useState } from "react";
import { getStatusConfig } from "../utils/trustHelpers";

/**
 * Renders AI answer with inline per-sentence trust badges.
 * Click on a non-neutral sentence to open the source inspect panel.
 */
export default function SentenceText({ sentences, onInspect }) {
  if (!sentences?.length) return null;

  return (
    <div className="text-[15px] leading-[1.85] text-ats-text">
      {sentences.map((sentence, idx) => (
        <SentenceSegment key={idx} sentence={sentence} index={idx} onInspect={onInspect} />
      ))}
    </div>
  );
}

function SentenceSegment({ sentence, index, onInspect }) {
  const config = getStatusConfig(sentence.status);
  const isNeutral = sentence.status === "NEUTRAL" || !sentence.status;
  const isClickable = !isNeutral && onInspect;

  return (
    <span className="relative group">
      {/* Sentence text with subtle underline highlight for non-neutral */}
      <span
        className={[
          "inline transition-all duration-150",
          !isNeutral && "cursor-pointer",
          !isNeutral && "hover:opacity-80",
        ].filter(Boolean).join(" ")}
        style={{
          borderBottom: !isNeutral ? `2px solid ${config.underlineColor}40` : "none",
          backgroundColor: !isNeutral ? `${config.dotColor}08` : "transparent",
          padding: !isNeutral ? "1px 2px" : "0",
          borderRadius: "2px",
        }}
        onClick={isClickable ? () => onInspect(sentence, index) : undefined}
        title={config.tooltip}
      >
        {sentence.text}
      </span>
      {/* Inline badge pill at the end of highlighted sentence */}
      {!isNeutral && (
        <span
          className={`${config.badgeClass} ml-1 text-[10px] py-0 px-1.5 align-middle cursor-pointer`}
          onClick={isClickable ? () => onInspect(sentence, index) : undefined}
        >
          {config.icon}
        </span>
      )}
      {" "}
    </span>
  );
}
