/**
 * Centralized session-loss handling (401, OOD idle logout, HTML login pages, etc.).
 * Sets isSessionExpired so polling stops; shows at most one toast per page load.
 */

import { ref, watch } from 'vue';

type ToastInstance = {
  clear: () => void;
  error: (msg: string, options?: { timeout?: number }) => void;
};

let toastInstance: ToastInstance | null = null;

const SESSION_EXPIRED_MESSAGE =
  'Session expired. Please log in to OOD again.';

/** When true, session has ended. Components should stop polling / fetching. */
export const isSessionExpired = ref(false);

/** Only the first detection shows a toast (avoids N racks × N intervals). */
let sessionExpiredToastShown = false;

/** Console once per page load when UI state flips (same moment as top banner). */
let sessionExpiredUiLogged = false;

watch(
  isSessionExpired,
  (expired) => {
    if (!expired || sessionExpiredUiLogged) return;
    sessionExpiredUiLogged = true;
    console.warn(
      '[rack-app] Session expired — UI updated (banner + toast). Polling/fetch hooks stop.',
      SESSION_EXPIRED_MESSAGE
    );
  },
  { flush: 'sync' }
);

export function initConnectionStatus(toast: ToastInstance) {
  toastInstance = toast;
}

export function handleSessionExpired() {
  isSessionExpired.value = true;
  if (!toastInstance) return;
  if (sessionExpiredToastShown) return;
  sessionExpiredToastShown = true;

  toastInstance.clear();
  // Longer than default 4000ms so the message is not missed before a manual refresh
  toastInstance.error(SESSION_EXPIRED_MESSAGE, { timeout: 60_000 });
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

/** Fetch/EventSource failures common when session expires or browser blocks connection */
export function fetchFailureLikelySessionRelated(e: unknown): boolean {
  if (e instanceof TypeError) return true;
  const m = String(e instanceof Error ? e.message : e).toLowerCase();
  return (
    m.includes('failed to fetch') ||
    m.includes('networkerror') ||
    m.includes('load failed') ||
    m.includes("can't establish") ||
    m.includes('network request failed')
  );
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
    const st = response.status;
    // OOD/proxy often returns 5xx when session is gone or upstream is unreachable
    if (st === 502 || st === 503 || st === 504) {
      return { kind: 'session_lost' };
    }
    return { kind: 'error' };
  }

  try {
    const data = JSON.parse(text) as unknown;
    return { kind: 'ok', data };
  } catch {
    return { kind: 'session_lost' };
  }
}
