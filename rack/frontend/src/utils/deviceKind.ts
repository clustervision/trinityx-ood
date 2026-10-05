/** Backend inventory type for “other” equipment (plural). */
export const OTHER_DEVICES_TYPE = 'otherdevices';

export function isOtherDevicesType(type: string | undefined | null): boolean {
  return (type || '').toLowerCase() === OTHER_DEVICES_TYPE;
}

/** Rack height in U; backend may send string numbers. */
export function deviceHeightU(height: unknown): number {
  const n = Number(height);
  return Number.isFinite(n) ? n : 0;
}

export function isOtherDevices0U(device: { type?: string; height?: unknown }): boolean {
  return isOtherDevicesType(device.type) && deviceHeightU(device.height) === 0;
}
