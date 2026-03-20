/**
 * Centralized session-loss handling (401, OOD idle logout, HTML login pages, etc.).
 * Sets isSessionExpired so polling stops; shows at most one toast per page load.
 */

import { ref } from 'vue';

type ToastInstance = { clear: () => void; error: (msg: string) => void };

let toastInstance: ToastInstance | null = null;

const SESSION_EXPIRED_MESSAGE =
  'Session expired. Please log in to OOD again.';

/** When true, session has ended. Components should stop polling / fetching. */
export const isSessionExpired = ref(false);

/** Only the first detection shows a toast (avoids N racks × N intervals). */
let sessionExpiredToastShown = false;

export function initConnectionStatus(toast: ToastInstance) {
  toastInstance = toast;
}

export function handleSessionExpired() {
  isSessionExpired.value = true;
  if (!toastInstance) return;
  if (sessionExpiredToastShown) return;
  sessionExpiredToastShown = true;

  toastInstance.clear();
  toastInstance.error(SESSION_EXPIRED_MESSAGE);
}

/** @deprecated Use handleSessionExpired; kept for axios interceptors and existing imports */
export function handle401Disconnect() {
  handleSessionExpired();
}

/** Auth failure or HTML (e.g. redirect to login) before reading the body */
export function responseIndicatesSessionLost(response: Response): boolean {
  const status = response.status;
  if (status === 401 || status === 403) return true;
  const ct = (response.headers.get('content-type') || '').toLowerCase();
  if (ct.includes('text/html')) return true;
  return false;
}

/** Sniff OOD/login HTML returned with misleading status or content-type */
export function bodyLooksLikeLoginHtml(text: string): boolean {
  const t = text.trimStart().slice(0, 800).toLowerCase();
  if (t.startsWith('<!doctype') || t.startsWith('<html')) return true;
  if (t.startsWith('<') && (t.includes('login') || t.includes('sign in') || t.includes('session')))
    return true;
  return false;
}

export function messageIndicatesSessionLost(raw: unknown): boolean {
  const s = String(raw ?? '').toLowerCase();
  return (
    s.includes('401') ||
    s.includes('403') ||
    s.includes('unauthorized') ||
    s.includes('forbidden') ||
    (s.includes('session') &&
      (s.includes('expir') || s.includes('invalid'))) ||
    s.includes('login required') ||
    s.includes('not authenticated')
  );
}

export type ParsedAppJsonResult =
  | { kind: 'session_lost' }
  | { kind: 'ok'; data: unknown }
  | { kind: 'error' };

/**
 * Read a JSON API response; treat auth/HTML/login wall / parse failure on OK as session lost.
 */
export async function readJsonApiResponse(
  response: Response
): Promise<ParsedAppJsonResult> {
  if (responseIndicatesSessionLost(response)) {
    return { kind: 'session_lost' };
  }

  const text = await response.text();
  if (bodyLooksLikeLoginHtml(text)) {
    return { kind: 'session_lost' };
  }

  if (!response.ok) {
    return { kind: 'error' };
  }

  try {
    const data = JSON.parse(text) as unknown;
    return { kind: 'ok', data };
  } catch {
    return { kind: 'session_lost' };
  }
}
