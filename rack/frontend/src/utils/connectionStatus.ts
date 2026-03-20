/**
 * Centralized 401 (session terminated) handling.
 * When OOD login expires, clear errors and show a single actionable message.
 * Stops repeated toasts and exposes a flag so polling can be paused.
 */

import { ref } from 'vue';

type ToastInstance = { clear: () => void; error: (msg: string) => void };

let toastInstance: ToastInstance | null = null;

/** Debounce: only show 401 toast once per this many ms */
const TOAST_DEBOUNCE_MS = 5 * 60 * 1000; // 5 minutes
let last401ToastAt = 0;

/** When true, session has expired (401). Components should stop polling. */
export const isSessionExpired = ref(false);

export function initConnectionStatus(toast: ToastInstance) {
  toastInstance = toast;
}

/**
 * Call when a 401 response is received. Clears existing error toasts and shows
 * a single message. Debounced to avoid repeated toasts from polling.
 */
export function handle401Disconnect() {
  isSessionExpired.value = true;
  if (!toastInstance) return;

  toastInstance.clear();

  const now = Date.now();
  if (now - last401ToastAt < TOAST_DEBOUNCE_MS) {
    return; // Already showed recently, avoid spam
  }
  last401ToastAt = now;

  toastInstance.error(
    'Session expired (401). Please log in to OOD again.'
  );
}
