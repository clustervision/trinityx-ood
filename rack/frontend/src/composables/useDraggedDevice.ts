import { ref } from 'vue';
import type { Device } from '@/types/rack';

const draggedDevice = ref<Device | null>(null);

export function useDraggedDevice() {
  const setDraggedDevice = (device: Device | null) => {
    draggedDevice.value = device;
  };

  return {
    draggedDevice,
    setDraggedDevice
  };
}
