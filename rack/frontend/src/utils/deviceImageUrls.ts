import type { Device, Rack } from '@/types/rack';
import { deviceHeightU, isOtherDevicesType } from '@/utils/deviceKind';

function assetUrl(file: string): string {
  return new URL(`../assets/img/${file}`, import.meta.url).href;
}

/** Vendors with shipped chassis artwork; all others use default-* images. */
const VENDORS_WITH_CHASSIS_ART = new Set(['supermicro', 'dell', 'hp', 'lenovo']);

export function getSwitchImageUrl(): string {
  return assetUrl('switch.png');
}

export function getVendorImageUrl(device: Device, size: number): string {
  if (isOtherDevicesType(device.type)) {
    const otherDeviceSizes = [0, 1, 2, 3, 4, 8];
    const safeSize = otherDeviceSizes.includes(size) ? size : 1;
    return assetUrl(`devices-${safeSize}u.png`);
  }
  let vendor = device.vendor ? device.vendor.toLowerCase() : '';
  if (vendor.includes('supermicro')) vendor = 'supermicro';
  else if (vendor.includes('dell')) vendor = 'dell';
  else if (vendor.includes('hp')) vendor = 'hp';
  else if (vendor.includes('lenovo')) vendor = 'lenovo';
  else vendor = '';
  const validSizes = [1, 2, 3, 4, 8];
  const safeSize = validSizes.includes(size) ? size : 1;

  if (!vendor || !VENDORS_WITH_CHASSIS_ART.has(vendor)) {
    return assetUrl(`default-${safeSize}u.png`);
  }
  return assetUrl(`${vendor}-${safeSize}u.png`);
}

export function getImageStack(device: Device): number[] {
  const h = deviceHeightU(device.height);
  if (isOtherDevicesType(device.type) && h === 0) return [0];
  const availableSizes = [8, 4, 3, 2, 1];

  let remaining = h;
  const parts: number[] = [];
  for (const size of availableSizes) {
    while (remaining >= size) {
      parts.push(size);
      remaining -= size;
    }
    if (remaining === 0) break;
  }
  if (remaining > 0) parts.push(1);

  return parts;
}

/** All distinct image URLs used for this device's rack background (for preloading). */
export function getDeviceBackgroundImageUrls(device: Device): string[] {
  if ((device.type || '').toLowerCase() === 'switch') {
    return [getSwitchImageUrl()];
  }
  return getImageStack(device).map((sizeU) => getVendorImageUrl(device, sizeU));
}

export function collectRackDeviceImageUrls(racks: Rack[]): string[] {
  const seen = new Set<string>();
  for (const rack of racks) {
    for (const slot of rack.slots) {
      for (const device of slot.devices) {
        for (const url of getDeviceBackgroundImageUrls(device)) {
          seen.add(url);
        }
      }
    }
  }
  return [...seen];
}

export function preloadImageUrls(urls: string[]): void {
  for (const url of urls) {
    const img = new Image();
    img.src = url;
  }
}
