import type { Rack } from '@/types/rack';
import { parsePowerStateFromMessage } from '@/utils/powerState';
import { isPerformCommandFailureMessage } from '@/utils/performCommandResponse';

/** Meta keys on API objects — not node names. */
const RESERVED_NODE_MAP_KEYS = new Set([
  'status',
  'message',
  'error',
  'data',
  'result',
]);

export function nodeResultValueToMessageString(val: unknown): string {
  if (typeof val === 'string') return val;
  if (val != null && typeof val === 'object') {
    try {
      return JSON.stringify(val);
    } catch {
      return String(val);
    }
  }
  return String(val ?? '');
}

/**
 * Rack power SSE may stream `{ node001: "...", node002: "..." }` (not `{ message, status }`).
 * Empty `{}` heartbeats are not this shape. Many servers use the default SSE `message` event only.
 */
export function isRackPowerNodeResultPayload(raw: unknown): boolean {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return false;
  const o = raw as Record<string, unknown>;
  if (Array.isArray(o.message)) return false;
  return Object.entries(o).some(([key, v]) => {
    if (RESERVED_NODE_MAP_KEYS.has(key.toLowerCase())) return false;
    return nodeResultValueToMessageString(v).trim().length > 0;
  });
}

export type RackPowerStreamApplyResult = {
  failedNodes: string[];
  succeededNodes: string[];
};

/** Mutates matching node devices' powerState; caller runs syncRackPowerFromNodes + saveRackPowerCache. */
export function applyRackPowerNodeResultPayload(
  rack: Rack,
  raw: unknown
): RackPowerStreamApplyResult {
  const failedNodes: string[] = [];
  const succeededNodes: string[] = [];
  if (!isRackPowerNodeResultPayload(raw)) {
    return { failedNodes, succeededNodes };
  }
  const o = raw as Record<string, unknown>;
  for (const [name, val] of Object.entries(o)) {
    if (RESERVED_NODE_MAP_KEYS.has(name.toLowerCase())) continue;
    const msg = nodeResultValueToMessageString(val);
    if (!msg.trim()) continue;
    let matched = false;
    for (const slot of rack.slots) {
      for (const device of slot.devices) {
        if (device.name !== name || device.type !== 'node') continue;
        matched = true;
        if (isPerformCommandFailureMessage(msg)) {
          device.powerState = 'OFF';
          failedNodes.push(name);
        } else {
          device.powerState = parsePowerStateFromMessage(msg);
          succeededNodes.push(name);
        }
      }
    }
    if (!matched) {
      // Payload names a node not in this rack view — ignore
    }
  }
  return { failedNodes, succeededNodes };
}
