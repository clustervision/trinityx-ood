import type { StatusToast } from '@/types'
import { ref } from 'vue'

/** How long each toast stays visible (seconds-scale UX). */
export const TOAST_TTL_MS = 6000

export function useToasts() {
  const toasts = ref<StatusToast[]>([])

  function pushToast(toast: StatusToast): void {
    if (!toast.message) return
    if (toasts.value.some((t) => t.id === toast.id)) return
    toasts.value = [...toasts.value, toast]
    window.setTimeout(() => dismissToast(toast.id), TOAST_TTL_MS)
  }

  function pushToasts(items: StatusToast[]): void {
    for (const toast of items) pushToast(toast)
  }

  function dismissToast(id: string): void {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function clearToasts(): void {
    toasts.value = []
  }

  return { toasts, pushToast, pushToasts, dismissToast, clearToasts }
}
