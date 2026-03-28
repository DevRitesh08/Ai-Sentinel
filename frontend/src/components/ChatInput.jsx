import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";

const ChatInput = forwardRef(function ChatInput(
  {
    onSubmit,
    loading = false,
    disabled = false,
    useContext = true,
    contextTurns = 0,
    onToggleContext,
    onClearContext,
  },
  ref
) {
  const [query, setQuery] = useState("");
  const textareaRef = useRef(null);
  const isDisabled = loading || disabled;

  useImperativeHandle(ref, () => ({ focus: () => textareaRef.current?.focus() }));

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  useEffect(() => {
    const element = textareaRef.current;
    if (!element) return;
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, 200)}px`;
  }, [query]);

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || isDisabled) return;
    onSubmit(trimmed);
    setQuery("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  const hasText = query.trim().length > 0;

  return (
    <div
      className="relative rounded-2xl border transition-all duration-200"
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
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything - I will tell you what to trust..."
          disabled={isDisabled}
          rows={1}
          className="flex-1 bg-transparent text-[#C8D8E8] text-[14px] leading-relaxed
                     placeholder:text-[#2E4560] resize-none outline-none font-sans min-h-[26px]
                     disabled:opacity-40 disabled:cursor-not-allowed"
        />

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!hasText || isDisabled}
          className="flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-200"
          style={{
            background: hasText && !isDisabled ? "linear-gradient(135deg, #01C4A0, #00A882)" : "#182030",
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

      <div className="flex items-center justify-between gap-3 px-4 pb-2.5 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={() => onToggleContext?.(!useContext)}
            className="text-[10.5px] font-mono px-2 py-1 rounded-full border transition-colors"
            style={{
              color: useContext ? "#01C4A0" : "#3D5670",
              borderColor: useContext ? "rgba(1,196,160,0.28)" : "#182030",
              background: useContext ? "rgba(1,196,160,0.08)" : "#0B1119",
            }}
          >
            Context {useContext ? "on" : "off"}
          </button>
          {useContext && contextTurns > 0 && (
            <>
              <span className="text-[10.5px] font-mono text-[#2A3E52]">
                {contextTurns} turn{contextTurns !== 1 ? "s" : ""} queued
              </span>
              <button
                type="button"
                onClick={() => onClearContext?.()}
                disabled={loading}
                className="text-[10.5px] font-mono text-[#4A6880] hover:text-[#4BA8E8] transition-colors disabled:opacity-40"
              >
                Clear context
              </button>
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10.5px] font-mono text-[#2A3E52]">
            {loading ? <span className="text-[#01C4A0]/70 animate-pulse">Verifying...</span> : "Enter send · Shift+Enter newline · / focus"}
          </span>
          <span className="text-[10px] font-mono text-[#1E3048]">
            {query.length > 0 ? `${query.length} / 2000` : ""}
          </span>
        </div>
      </div>
    </div>
  );
});

export default ChatInput;
