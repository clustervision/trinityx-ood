import type { Rack } from '@/types/rack';

export type RackPowerCachePayload = {
  powerOn?: boolean;
  backPowerOn?: boolean;
  devices: Record<string, string | undefined>;
};

export function getRackPowerCacheKey(rackName: string | undefined): string {
  return `rackPowerCache:${rackName || 'unknown'}`;
}

/**
 * Merge last-known per-device power states from localStorage into a rack built from show_rack.
 * The API often omits power fields; without this, loadRacks() resets all nodes to OFF and LEDs / rack button break.
 */
export function mergeRackPowerCacheFromStorage(rack: Rack): void {
  if (typeof window === 'undefined') return;
  try {
    const raw = window.localStorage.getItem(getRackPowerCacheKey(rack.name));
    if (!raw) return;
    const cache = JSON.parse(raw) as RackPowerCachePayload | null;
    if (!cache?.devices) return;
    rack.slots.forEach((slot) => {
      slot.devices.forEach((device) => {
        const cached = cache.devices[device.name];
        if (cached === 'ON' || cached === 'OFF' || cached === 'RESET') {
          device.powerState = cached;
        }
      });
    });
  } catch (e) {
    console.error('[Rack Power Cache] merge from storage failed', e);
  }
}
