<template>
  <div
    class="device-item draggable"
    :class="[
       vendorClass,
       { 'is-dragging': isDragging, 'no-drag': !canDrag },
       isRackView ? 'is-absolute' : 'is-relative'
    ]"
    :style="deviceBackgroundStyle"
    :draggable="canDrag"
    @dragstart="onDragStart"
    @dragend="onDragEnd"
    @contextmenu.prevent="onRightClick"
  >

  <div class="device-content">
      <div v-if="!isDarkMode || !isRackView">
      <span class="device-name">{{ device.name }}</span>
      </div>
    </div>
    <div class="indicators-overlay">

      <div
        v-if="metric1Type && metric1Type !== 'No Scale'"
        class="indicator-box"
        :style="{ backgroundColor: getColor(metric1Value, metric1Type) }"
        :title="`${metric1Type}: ${metric1Value ?? 'No Data'}`"
      ></div>

      <div
        v-if="metric2Type && metric2Type !== 'No Scale'"
        class="indicator-box"
        :style="{ backgroundColor: getColor(metric2Value, metric2Type) }"
        :title="`${metric2Type}: ${metric2Value ?? 'No Data'}`"
      ></div>

      <Teleport v-if="!isRackView" to="body">
        <DeviceContextMenu
          :visible="menuVisible"
          :position="menuPos"
          :device="device"
          @close="closeMenu"
          @action="handleMenuAction"
        />
      </Teleport>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Device } from '@/types/rack';
import { useRackSizing } from '@/composables/useRackSizing';
import { useTheme } from '@/composables/useTheme';
import { useDeviceActions } from '@/composables/useDeviceActions';
import { useDraggedDevice } from '@/composables/useDraggedDevice';
import { useToast } from 'vue-toastification';
import DeviceContextMenu from '@/components/DeviceContextMenu.vue';
import { deviceHeightU, isOtherDevices0U, isOtherDevicesType } from '@/utils/deviceKind';
import { getImageStack, getSwitchImageUrl, getVendorImageUrl } from '@/utils/deviceImageUrls';

const { isDarkMode } = useTheme();
const toast = useToast();
const { setDraggedDevice } = useDraggedDevice();
const { executeDeviceAction } = useDeviceActions();
const props = defineProps<{
  device: Device;
  metric1Value?: number;
  metric1Type?: string | null;
  metric2Value?: number;
  metric2Type?: string | null;
  isRackView?: boolean;
  selected?: boolean;
  selectedDevicesForDrag?: Device[];
}>();
const emit = defineEmits(['device-right-click', 'edit-inventory']);
const isDragging = ref(false);
const { unitPixelHeight } = useRackSizing();

const menuVisible = ref(false);
const menuPos = ref({ x: 0, y: 0 });

const isOtherDevice0U = computed(() => isOtherDevices0U(props.device));
const canDrag = computed(() => !isOtherDevice0U.value);

const heightPixels = computed(() => {
  const h = deviceHeightU(props.device.height);
  const px = (h * unitPixelHeight.value) - 2;
  return h === 0 ? Math.max(20, unitPixelHeight.value - 2) : px;
});

const onRightClick = (event: MouseEvent) => {
  if (props.isRackView) {
    emit('device-right-click', event, props.device);
  } else {
    event.preventDefault();
    menuPos.value = { x: event.clientX, y: event.clientY };
    menuVisible.value = true;
  }
};

const closeMenu = () => {
  menuVisible.value = false;
};

const handleMenuAction = async (payload: { action: string; subAction?: string; device: Device }) => {
  const { action, subAction, device } = payload;
  if (action === 'edit-inventory') {
    emit('edit-inventory', device);
    return;
  }
  try {
    const result = await executeDeviceAction(action, subAction, device);
    if (result?.success) {
      toast.success(result.message);
    }
  } catch {
    toast.error('Action failed');
  }
};

const deviceBackgroundStyle = computed(() => {

  if (props.device.type === 'switch') {
    const url = getSwitchImageUrl();
    return {
      height: heightPixels.value + 'px',
      backgroundImage: `url(${url})`,
      backgroundRepeat: 'repeat-y',
      backgroundSize: `100% ${unitPixelHeight.value}px`,
      backgroundColor: 'transparent',
      border: 'none'
    };
  }

  const heightParts = getImageStack(props.device);

  const bgImages: string[] = [];
  const bgPositions: string[] = [];
  const bgSizes: string[] = [];

  let currentOffsetY = 0;

  heightParts.forEach((sizeU) => {
    const url = getVendorImageUrl(props.device, sizeU);
    const pixelH = sizeU === 0 ? Math.max(20, unitPixelHeight.value) : sizeU * unitPixelHeight.value;
    bgImages.push(`url(${url})`);
    bgPositions.push(`0px ${currentOffsetY}px`);
    bgSizes.push(`100% ${pixelH}px`);
    currentOffsetY += pixelH;
  });

  return {
    height: heightPixels.value + 'px',
    backgroundImage: bgImages.join(', '),
    backgroundPosition: bgPositions.join(', '),
    backgroundSize: bgSizes.join(', '),
    backgroundRepeat: 'no-repeat',
    backgroundColor: 'transparent',
    border: 'none'
  };
});

const getColor = (val: number | undefined | null, type: string | null) => {
  if (!type || type === 'No Scale') return 'transparent';

  if (val === undefined || val === null) {
    return '#666666';
  }

  const value = parseFloat(val.toString());

  if (type === 'Temperature') {
    const ratio = Math.min(Math.max(value, 0), 100) / 100;
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  }

  if (type === 'System Load') {
    const ratio = Math.min(Math.max(value, 0), 1);
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  }
  if (type === 'Power Consumption') {
    const ratio = Math.min(Math.max(value, 0), 500) / 500;
    const hue = (1 - ratio) * 120;
    return `hsl(${hue}, 100%, 45%)`;
  }
  return '#cccccc';
};

const vendorClass = computed(() => {
  const type = (props.device.type || '').toLowerCase();
  const vendor = props.device.vendor ? props.device.vendor.toLowerCase() : '';
  const height = props.device.height;
  if (type === 'switch') return 'switch';
  if (isOtherDevicesType(props.device.type)) return 'otherdevices';
  if (!vendor || vendor === 'none') return 'default';
  return `${vendor}-${height}`;
});

const onDragStart = (event: DragEvent) => {
  if (!canDrag.value) {
    event.preventDefault();
    return;
  }
  isDragging.value = true;
  setDraggedDevice(props.device);
  if (event.dataTransfer) {
    const offsetY = event.offsetY;
    const uOffset = Math.floor(offsetY / unitPixelHeight.value);

    event.dataTransfer.effectAllowed = 'move';
    const fromPool = !props.isRackView;
    const multi =
      fromPool &&
      props.selectedDevicesForDrag &&
      props.selectedDevicesForDrag.length > 1 &&
      props.selectedDevicesForDrag.some((d) => d.name === props.device.name);

    if (multi && props.selectedDevicesForDrag) {
      const draggableDevices = props.selectedDevicesForDrag.filter((d) => !isOtherDevices0U(d));
      const payload = {
        multi: true,
        devices: draggableDevices.map((d) => ({ ...d, dragSource: 'pool' as const })),
        uOffset
      };
      event.dataTransfer.setData('application/json', JSON.stringify(payload));
    } else {
      const payload = {
        ...props.device,
        dragSource: props.isRackView ? 'rack' : 'pool',
        uOffset
      };
      event.dataTransfer.setData('application/json', JSON.stringify(payload));
    }
  }
};

const onDragEnd = () => {
  isDragging.value = false;
  setDraggedDevice(null);
};
</script>

<style scoped>
.device-item {
  width: 100%;
  z-index: 10;
  cursor: grab;
  border: 1px solid #333;
  background-color: #3a3a3a;
  color: white;
  position: relative;
  display: flex;
  align-items: center;
  padding-left: 5px;
  overflow: hidden;
}
.device-item.no-drag {
  cursor: not-allowed;
}

.device-item.is-absolute { position: absolute; }
.device-item.is-relative { position: relative; margin-bottom: 5px; }

.device-content {
  overflow: hidden;
  white-space: nowrap;
  font-size: 10px;
  text-shadow: 1px 1px 2px black;
  width: 80%;
}


.indicators-overlay {
  position: absolute;
  top: 2px;
  right: 2px;
  display: flex;
  gap: 2px;
  z-index: 20;
}


.indicator-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
</style>
