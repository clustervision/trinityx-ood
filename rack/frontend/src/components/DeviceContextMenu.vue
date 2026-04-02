<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import type { Device } from '@/types/rack';

const props = defineProps<{
  visible: boolean;
  position: { x: number; y: number };
  device: Device | null;
}>();

const emit = defineEmits(['close', 'action']);

const menuRef = ref<HTMLElement | null>(null);

// Close menu if clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (props.visible && menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('close');
  }
};

const menuStyle = computed(() => {
  const { x, y } = props.position;
  if (typeof window === 'undefined') return { top: `${y}px`, left: `${x}px` };

  const windowHeight = window.innerHeight;
  const isNearBottom = y > windowHeight * 0.7;

  if (isNearBottom) {
    return {
      left: `${x}px`,
      bottom: `${windowHeight - y}px`,
      top: 'auto'
    };
  } else {
    return {
      left: `${x}px`,
      top: `${y}px`,
      bottom: 'auto'
    };
  }
});
onMounted(() => document.addEventListener('mousedown', handleClickOutside));
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside));


const menuItems = computed(() => {
  if (!props.device) return [];
  const type = (props.device.type || 'node').toLowerCase();
  
  const items = [
    { label: 'Details', action: 'details', icon: 'bx bx-detail' },
  ];

  const hasEditInInventory = ['node', 'switch', 'controller', 'otherdevices'].includes(type);
  if (hasEditInInventory) {
    items.push({ label: 'Edit in Inventory', action: 'edit-inventory', icon: 'bx bx-edit' });
    items.push({ label: 'Edit in Console', action: 'edit', icon: 'bx bx-link-external' });
  } else {
    items.push({ label: 'Edit', action: 'edit', icon: 'bx bx-edit' });
  }

  if (type !== 'controller') {
    items.push({ label: 'Rename', action: 'rename', icon: 'bx bx-pencil' });
    items.push({ label: 'Clone', action: 'clone', icon: 'bx bx-copy' });
  }

  return items;
});

// Specific Power/IPMI actions for Nodes
const isNode = computed(() => props.device?.type === 'node');

const triggerAction = (action: string, subAction?: string) => {
  emit('action', { action, subAction, device: props.device! });
  emit('close');
};
</script>

<template>
  <div
    v-if="visible && device"
    ref="menuRef"
    class="context-menu"
    :style="menuStyle"
    @wheel.stop
  >
    <div class="menu-header">
      <i class="bx bx-chip me-2"></i>
      <strong>{{ device.name }} Settings</strong>
    </div>

    <ul class="menu-list">
      <li v-for="item in menuItems" :key="item.label" @click="triggerAction(item.action)">
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </li>

      <template v-if="isNode">
        <li class="divider"></li>
        <li @click="triggerAction('power', 'status')"><i class="bx bx-pulse"></i> Power Status</li>
        <li @click="triggerAction('power', 'off')"><i class="bx bx-power-off text-danger"></i> Power Off</li>
        <li @click="triggerAction('power', 'on')"><i class="bx bx-power-off text-success"></i> Power ON</li>
        <li @click="triggerAction('power', 'reset')"><i class="bx bx-reset"></i> Power Reset</li>

        <li class="divider"></li>
        <li @click="triggerAction('sel', 'list')"><i class="bx bx-list-ul"></i> Sel List</li>
        <li @click="triggerAction('sel', 'clear')"><i class="bx bx-list-minus"></i> Sel Clear</li>

        <li class="divider"></li>
        <li @click="triggerAction('chassis', 'identify')"><i class="bx bx-tv"></i> Chassis Identify</li>
        <li @click="triggerAction('chassis', 'noidentify')"><i class="bx bx-tv text-muted"></i> Chassis No Identify</li>
      </template>
    </ul>
  </div>
</template>

<style scoped>
.context-menu {
  position: fixed;
  z-index: 9999;
  background: white;
  border: 1px solid #ccc;
  box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
  min-width: 180px;
  font-size: 12px;
  color: #333;
  display: flex;
  flex-direction: column;
  max-height: 40vh;
  box-sizing: border-box;
}

.menu-header {
  background-color: #333;
  color: #fff;
  padding: 5px 10px;
  font-weight: bold;
  border-bottom: 1px solid #444;
  display: flex;
  align-items: center;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  overscroll-behavior: contain;
}

.menu-list li {
  padding: 6px 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-list li:hover {
  background-color: #f0f0f0;
  color: #000;
}

.divider {
  height: 1px;
  background-color: #ddd;
  margin: 4px 0;
  padding: 0 !important;
  cursor: default !important;
}
</style>
