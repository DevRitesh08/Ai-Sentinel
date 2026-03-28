// frontend/src/hooks/useKeyboardShortcuts.js
import { useEffect } from "react";

/**
 * Global keyboard shortcuts for the app.
 *
 * Shortcuts:
 *   /         → Focus the query input
 *   Escape    → Clear current result and focus input
 *   Ctrl+K    → Focus input (VSCode style)
 */
export function useKeyboardShortcuts({ onFocusInput, onClearResult }) {
  useEffect(() => {
    const handler = (e) => {
      // Don't intercept when user is already typing
      const tag = document.activeElement?.tagName;
      const inInput = tag === "INPUT" || tag === "TEXTAREA";

      if (!inInput && e.key === "/") {
        e.preventDefault();
        onFocusInput?.();
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        onFocusInput?.();
        return;
      }

      if (e.key === "Escape") {
        onClearResult?.();
        onFocusInput?.();
        return;
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onFocusInput, onClearResult]);
}
