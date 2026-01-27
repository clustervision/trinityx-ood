import { ref } from 'vue';
import axios from 'axios';
import type { Device } from '@/types/rack';

export function useDeviceActions() {
  const isActionLoading = ref(false);

  const executeDeviceAction = async (
    action: string,
    subAction: string | undefined,
    device: Device
  ): Promise<{ success: true; message: string } | undefined> => {
    const baseUrl = (typeof window !== 'undefined' && (window as unknown as { CONTEXT_URL?: string }).CONTEXT_URL) || '';
    const appUrl = (typeof window !== 'undefined' && (window as unknown as { APP_URL?: string }).APP_URL) || '';

    // 1. URL Navigation Actions (跳转逻辑)
    if (['details', 'edit', 'rename', 'clone'].includes(action)) {
      let route = '';
      const typeMap: Record<string, string> = {
        node: 'trinity_node',
        switch: 'trinity_switch',
        controller: 'trinity_cluster',
        otherdevices: 'trinity_otherdev'
      };

      const section = typeMap[device.type] || 'trinity_node';

      if (device.type === 'controller') {
        if (action === 'details') route = `${baseUrl}/${section}/`;
        if (action === 'edit') route = `${baseUrl}/${section}/edit`;
      } else {
        if (action === 'details') route = `${baseUrl}/${section}/show/${device.name}`;
        if (action === 'edit') route = `${baseUrl}/${section}/edit/${device.name}`;
        if (action === 'rename') route = `${baseUrl}/${section}/rename/${device.name}`;
        if (action === 'clone') route = `${baseUrl}/${section}/clone/${device.name}`;
      }

      if (route) {
        window.open(route, '_blank')?.focus();
        return;
      }
    }

    // 2. API Actions (API 请求逻辑)
    if (['power', 'sel', 'chassis'].includes(action)) {
      console.log(`Executing ${action} - ${subAction} on ${device.name}`);
      isActionLoading.value = true;
      try {
        const response = await axios.get(
          `${appUrl}perform/${action}/${subAction}/${device.name}`
        );
        return {
          success: true,
          message: response.data.message || `Command sent: ${subAction}`
        };
      } catch (e) {
        console.error(e);
        throw new Error('Action failed');
      } finally {
        isActionLoading.value = false;
      }
    }

    return undefined;
  };

  return {
    isActionLoading,
    executeDeviceAction
  };
}
