import { isPerformCommandFailureMessage } from '@/utils/performCommandResponse';

/**
 * Parse API/drag text into a single UI power state.
 * Only ON / OFF / RESET (exact token or whole-word match) count; anything else -> OFF
 * so LEDs and rack power button do not treat ambiguous text as powered on.
 */
export type PowerStateUi = 'ON' | 'OFF' | 'RESET';

export function parsePowerStateFromMessage(text: unknown): PowerStateUi {
  const s = String(text ?? '').trim();
  if (s && isPerformCommandFailureMessage(s)) return 'OFF';
  const u = s.toUpperCase();
  if (!u) return 'OFF';
  if (u === 'ON' || u === 'OFF' || u === 'RESET') return u;
  // Order: RESET, OFF, then ON — avoids substring false positives (e.g. "MONITOR" vs \bON\b)
  if (/\bRESET\b/.test(u)) return 'RESET';
  if (/\bOFF\b/.test(u)) return 'OFF';
  if (/\bON\b/.test(u)) return 'ON';
  return 'OFF';
}

/** Same token rules as parsePowerStateFromMessage, but returns null when no ON/OFF/RESET can be inferred (for toasts). */
export function tryParsePowerStateMessage(text: unknown): PowerStateUi | null {
  const s = String(text ?? '').trim();
  if (s && isPerformCommandFailureMessage(s)) return null;
  const u = s.toUpperCase();
  if (!u) return null;
  if (u === 'ON' || u === 'OFF' || u === 'RESET') return u;
  if (/\bRESET\b/.test(u)) return 'RESET';
  if (/\bOFF\b/.test(u)) return 'OFF';
  if (/\bON\b/.test(u)) return 'ON';
  return null;
}
