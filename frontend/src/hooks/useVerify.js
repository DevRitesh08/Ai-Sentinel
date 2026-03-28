import { useState, useCallback, useRef } from "react";
import { verifyQuery } from "../api/client";

const INITIAL_STATE = {
  data: null,
  loading: false,
  error: null,
  fromCache: false,
};

export function useVerify() {
  const [state, setState] = useState(INITIAL_STATE);
  const abortRef = useRef(null);

  const verify = useCallback(async (query, options = {}) => {
    if (abortRef.current) {
      abortRef.current.abort();
    }

    setState({ data: null, loading: true, error: null, fromCache: false });

    try {
      const result = await verifyQuery(query, options.history ?? []);

      setState({
        data: result,
        loading: false,
        error: null,
        fromCache: result.from_cache ?? false,
      });

      return result;
    } catch (err) {
      let errorMessage = "Something went wrong. Please try again.";

      if (err.isTimeout) {
        errorMessage = "The request timed out. The pipeline may be busy - try again.";
      } else if (err.isNetwork) {
        errorMessage = "Cannot reach the server. Is the backend running on port 8000?";
      } else if (err.isClient) {
        errorMessage = err.message ?? "Invalid request.";
      } else if (err.isServer) {
        errorMessage = "Server error. Check the backend logs.";
      }

      setState({
        data: null,
        loading: false,
        error: errorMessage,
        fromCache: false,
      });

      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState(INITIAL_STATE);
  }, []);

  return {
    ...state,
    verify,
    reset,
    hasResult: !!state.data && !state.loading,
    isLoading: state.loading,
    hasError: !!state.error && !state.loading,
  };
}
