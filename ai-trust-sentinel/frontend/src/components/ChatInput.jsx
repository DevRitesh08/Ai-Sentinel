// frontend/src/components/ChatInput.jsx
import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from "react";

/**
 * Query input — large, centered, haloed textarea.
 * Auto-resizing, Enter to submit, Shift+Enter for newline.
 * Supports forwardRef for keyboard shortcut focus.
 */
const ChatInput = forwardRef(function ChatInput({ onSubmit, loading = false, disabled = false }, ref) {
  const [query, setQuery] = useState("");
  const textareaRef = useRef(null);
  const isDisabled = loading || disabled;

  // Expose focus to parent via ref
  useImperativeHandle(ref, () => ({
    focus: () => textareaRef.current?.focus(),
  }));

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 180) + "px";
  }, [query]);

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || isDisabled) return;
    onSubmit(trimmed);
    setQuery("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="card p-3 sm:p-4 shadow-lg shadow-black/20">
      <textarea
        ref={textareaRef}
        id="query-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything — I'll tell you what to trust."
        disabled={isDisabled}
        rows={1}
        className={[
          "w-full bg-transparent text-ats-text text-[15px]",
          "placeholder:text-ats-dim resize-none outline-none",
          "leading-relaxed min-h-[44px] font-sans",
          isDisabled && "opacity-40 cursor-not-allowed",
        ].filter(Boolean).join(" ")}
      />

      <div className="flex items-center justify-between mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-ats-border/50">
        <div className="flex items-center gap-2 sm:gap-3">
          <span className="text-[10px] sm:text-[11px] text-ats-dim">
            ↵ Send · ⇧↵ New line · / Focus
          </span>
          {loading && (
            <span className="text-[11px] text-ats-mint font-mono animate-pulse">
              ● Verifying...
            </span>
          )}
        </div>

        <button
          id="submit-button"
          onClick={handleSubmit}
          disabled={!query.trim() || isDisabled}
          className={[
            "px-4 sm:px-5 py-2 rounded-xl text-sm font-semibold transition-all duration-200",
            query.trim() && !isDisabled
              ? "bg-ats-mint text-ats-bg hover:shadow-glow-mint active:scale-[0.97] cursor-pointer"
              : "bg-ats-border text-ats-dim cursor-not-allowed opacity-40",
          ].filter(Boolean).join(" ")}
        >
          {loading ? "Verifying..." : "Verify →"}
        </button>
      </div>
    </div>
  );
});

export default ChatInput;
