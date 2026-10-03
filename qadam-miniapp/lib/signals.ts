import data from "./signal-labels.json";

/**
 * Signal labels — verbatim copy of the backend source (qadam/backend/data/signals_v1.json).
 * Parity with the backend is enforced by qadam/tests/test_signal_labels.py.
 */
export const SIGNAL_LABELS: Readonly<Record<string, string>> = data.labels;

export function signalLabel(key: string): string {
  return SIGNAL_LABELS[key] ?? key;
}
