// frontend/src/components/ChatInput.jsx
import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from "react";

const ChatInput = forwardRef(function ChatInput({ onSubmit, loading = false, disabled = false }, ref) {
  const [query, setQuery] = useState("");
  const textareaRef = useRef(null);
  const isDisabled = loading || disabled;

  useImperativeHandle(ref, () => ({ focus: () => textareaRef.current?.focus() }));

  useEffect(() => { textareaRef.current?.focus(); }, []);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [query]);

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || isDisabled) return;
    onSubmit(trimmed);
    setQuery("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  const hasText = query.trim().length > 0;

  return (
    <div className="relative rounded-2xl border transition-all duration-200"
      style={{
        background: "#0D1520",
        borderColor: hasText && !isDisabled ? "rgba(1,196,160,0.25)" : "#182030",
        boxShadow: hasText && !isDisabled
          ? "0 0 0 1px rgba(1,196,160,0.1), 0 8px 32px rgba(0,0,0,0.4)"
          : "0 4px 24px rgba(0,0,0,0.3)",
      }}
    >
      <div className="flex items-end gap-3 px-4 py-3.5">
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything — I'll tell you what to trust…"
          disabled={isDisabled}
          rows={1}
          className="flex-1 bg-transparent text-[#C8D8E8] text-[14px] leading-relaxed
                     placeholder:text-[#2E4560] resize-none outline-none font-sans min-h-[26px]
                     disabled:opacity-40 disabled:cursor-not-allowed"
        />

        {/* Submit button */}
        <button
          onClick={handleSubmit}
          disabled={!hasText || isDisabled}
          className="flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center
                     transition-all duration-200"
          style={{
            background: hasText && !isDisabled
              ? "linear-gradient(135deg, #01C4A0, #00A882)"
              : "#182030",
            opacity: hasText && !isDisabled ? 1 : 0.4,
            boxShadow: hasText && !isDisabled ? "0 0 12px rgba(1,196,160,0.3)" : "none",
            transform: "none",
            cursor: hasText && !isDisabled ? "pointer" : "not-allowed",
          }}
        >
          {loading ? (
            <svg className="w-3.5 h-3.5 text-[#050B12] animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
          ) : (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke={hasText ? "#050B12" : "#3D5670"} strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5M5 12l7-7 7 7" />
            </svg>
          )}
        </button>
      </div>

      {/* Footer hint */}
      <div className="flex items-center justify-between px-4 pb-2.5">
        <span className="text-[10.5px] font-mono text-[#2A3E52]">
          {loading ? (
            <span className="text-[#01C4A0]/70 animate-pulse">Verifying…</span>
          ) : (
            "↵ send  ·  ⇧↵ newline  ·  / focus"
          )}
        </span>
        <span className="text-[10px] font-mono text-[#1E3048]">
          {query.length > 0 ? `${query.length} / 2000` : ""}
        </span>
      </div>
    </div>
  );
});

export default ChatInput;
