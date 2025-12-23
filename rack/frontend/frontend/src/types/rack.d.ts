export interface Device {
  name: string;
  type: string; 
  height: number; 
  vendor: string; 
  position: number; 
  orientation: 'front' | 'back'; 
  status?: string; // Optional: 'ok', 'error', etc.
}

export interface RackSlot {
  number: number;
  device: Device | null;
}

export interface Rack {
  name: string;
  size: number;
  order: string;
  slots: RackSlot[]; 
  showBackSide: boolean;
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