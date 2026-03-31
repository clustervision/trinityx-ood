import { ref } from 'vue';
import axios from 'axios';
import type { Device } from '@/types/rack';
import { isPerformCommandFailureMessage } from '@/utils/performCommandResponse';

/** Result of /perform/... calls; success is derived from message (not `status`, which is on/off). */
export type DevicePerformResult = { success: boolean; message: string };

export function useDeviceActions() {
  const isActionLoading = ref(false);

  const executeDeviceAction = async (
    action: string,
    subAction: string | undefined,
    device: Device
  ): Promise<DevicePerformResult | undefined> => {
    const appUrl = (typeof window !== 'undefined' && (window as unknown as { APP_URL?: string }).APP_URL) || '';
    const contextUrl = (typeof window !== 'undefined' && (window as unknown as { CONTEXT_URL?: string }).CONTEXT_URL) || '';
    const baseForLinks = contextUrl.replace(/\/$/, '') + '/pun/sys';

    if (['details', 'edit', 'rename', 'clone'].includes(action)) {
      let route = '';
      const typeMap: Record<string, string> = {
        node: 'trinity_node',
        switch: 'trinity_switch',
        controller: 'trinity_cluster',
        otherdevices: 'trinity_otherdev'
      };

      const typeKey = (device.type || '').toLowerCase();
      const section = typeMap[typeKey] || 'trinity_node';

      if (device.type === 'controller') {
        if (action === 'details') route = `${baseForLinks}/${section}/`;
        if (action === 'edit') route = `${baseForLinks}/${section}/edit`;
      } else {
        if (action === 'details') route = `${baseForLinks}/${section}/show/${device.name}`;
        if (action === 'edit') route = `${baseForLinks}/${section}/edit/${device.name}`;
        if (action === 'rename') route = `${baseForLinks}/${section}/rename/${device.name}`;
        if (action === 'clone') route = `${baseForLinks}/${section}/clone/${device.name}`;
      }

      if (route) {
        window.open(route, '_blank')?.focus();
        return;
      }
    }

    // API actions (power, sel, chassis)
    if (['power', 'sel', 'chassis'].includes(action)) {
      console.log(`Executing ${action} - ${subAction} on ${device.name}`);
      isActionLoading.value = true;
      try {
        const response = await axios.get(
          `${appUrl}/perform/${action}/${subAction}/${device.name}`
        );
        const data = response.data as { message?: string };
        const message =
          typeof data.message === 'string' && data.message.trim() !== ''
            ? data.message
            : `Command sent: ${subAction}`;
        const success = !isPerformCommandFailureMessage(message);
        return { success, message };
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
