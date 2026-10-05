import { tryParsePowerStateMessage } from '@/utils/powerState';

type ToastLike = {
  success: (msg: string) => void;
  warning: (msg: string) => void;
  error: (msg: string) => void;
};

/**
 * Power API success toasts: A/B/C fixed copy, D when response is not a recognized power state/message.
 */
export function showPowerOperationToast(
  toast: ToastLike,
  nodeName: string,
  subAction: string | undefined,
  rawMessage: string
): void {
  const sub = (subAction || '').toLowerCase();
  const msg = String(rawMessage ?? '').trim();
  const parsed = tryParsePowerStateMessage(msg);

  if (sub === 'status') {
    if (parsed === 'ON') {
      toast.success(`${nodeName} is powered on`);
      return;
    }
    if (parsed === 'OFF') {
      toast.warning(`${nodeName} is powered off`);
      return;
    }
    if (parsed === 'RESET') {
      toast.success(`${nodeName} is powered on.`);
      return;
    }
    toast.error(`Failed to perform operation on ${nodeName}.\n${msg || 'Unknown response.'}`);
    return;
  }

  if (sub === 'on') {
    if (parsed === 'ON' || parsed === 'RESET') {
      toast.success(`${nodeName} is powered on`);
      return;
    }
    toast.error(`Failed to perform operation on ${nodeName}.\n${msg || 'Unknown response.'}`);
    return;
  }

  if (sub === 'off') {
    if (parsed === 'OFF') {
      toast.warning(`${nodeName} is powered off`);
      return;
    }
    toast.error(`Failed to perform operation on ${nodeName}.\n${msg || 'Unknown response.'}`);
    return;
  }

  if (sub === 'reset') {
    if (parsed === 'ON' || parsed === 'RESET') {
      toast.success(`${nodeName} is powered on.`);
      return;
    }
    toast.error(`Failed to perform operation on ${nodeName}.\n${msg || 'Unknown response.'}`);
    return;
  }

  toast.error(`Failed to perform operation on ${nodeName}.\n${msg || 'Unknown response.'}`);
}
