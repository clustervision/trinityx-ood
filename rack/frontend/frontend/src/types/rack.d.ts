export interface Device {
  name: string;
  type: string;
  height: number;
  vendor: string;
  position: number;
  orientation: 'front' | 'back';
  status?: string;
}

export interface RackSlot {
  number: number;
  devices: Device[];
}

export interface Rack {
  name: string;
  size: number;
  order: string;
  slots: RackSlot[];
  showBackSide: boolean;
  showFrontSide: boolean;
  powerOn?: boolean;
  backPowerOn?: boolean;
}

export interface RackData {
  [key: string]: Rack;
}

export interface NodeMetric {
  hostname: string;
  load: number;
  temperature: number;
  power: number;
  gpu_temp?: number;
}
