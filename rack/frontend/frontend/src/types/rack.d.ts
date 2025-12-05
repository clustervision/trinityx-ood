export interface Device {
  name: string;
  type: string; // 'node', 'switch', etc.
  height: number; // The size in U (e.g., 2, 4)
  vendor: string; // 'dell', 'hp', etc.
  position: number; // The starting U slot
  orientation: 'front' | 'back'; // Front or Back view
}

export interface Rack {
  name: string;
  size: number; // usually 42 or 52
  devices: Device[];
}

export interface RackData {
  [key: string]: Rack; // Dictionary mapping "RackName" -> Rack Object
}