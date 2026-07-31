/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2026  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * @author      Yixin Zhang
 * @copyright   Copyright 2026, Luna2 Project[OOD]
 * @license     GPL
 * @version     2.0
 * @maintainer  Yixin Zhang
 * @email       yixin.zhang@clustervision.com
 * @status      Development
 */

import type { StatusToast } from '@/types'
import { ref } from 'vue'

/** How long each toast stays visible (seconds-scale UX). */
export const TOAST_TTL_MS = 6000
/** Collapsed multi-error toasts stay longer so users can expand them. */
export const TOAST_BATCH_TTL_MS = 20000

export function useToasts() {
  const toasts = ref<StatusToast[]>([])
  const timers = new Map<string, number>()

  function clearTimer(id: string): void {
    const handle = timers.get(id)
    if (handle != null) {
      window.clearTimeout(handle)
      timers.delete(id)
    }
  }

  function scheduleDismiss(toast: StatusToast): void {
    clearTimer(toast.id)
    const ttl = toast.details?.length ? TOAST_BATCH_TTL_MS : TOAST_TTL_MS
    const handle = window.setTimeout(() => dismissToast(toast.id), ttl)
    timers.set(toast.id, handle)
  }

  function pushToast(toast: StatusToast): void {
    if (!toast.message) return
    const existing = toasts.value.find((t) => t.id === toast.id)
    if (existing) {
      if (toast.details?.length) {
        const merged = [...(existing.details ?? [])]
        for (const line of toast.details) {
          if (!merged.includes(line)) merged.push(line)
        }
        const fieldPart = toast.id.startsWith('batch:') ? toast.id.slice('batch:'.length) : existing.field
        const next: StatusToast = {
          ...existing,
          message: `${merged.length} errors${fieldPart && fieldPart !== 'mixed' ? ` · ${fieldPart}` : ''}`,
          details: merged,
        }
        toasts.value = toasts.value.map((t) => (t.id === toast.id ? next : t))
        scheduleDismiss(next)
      }
      return
    }
    toasts.value = [...toasts.value, toast]
    scheduleDismiss(toast)
  }

  function pushToasts(items: StatusToast[]): void {
    for (const toast of items) pushToast(toast)
  }

  function dismissToast(id: string): void {
    clearTimer(id)
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function clearToasts(): void {
    for (const id of timers.keys()) clearTimer(id)
    toasts.value = []
  }

  /** Pause auto-dismiss while the user inspects expanded details. */
  function holdToast(id: string): void {
    clearTimer(id)
  }

  function releaseToast(id: string): void {
    const toast = toasts.value.find((t) => t.id === id)
    if (toast) scheduleDismiss(toast)
  }

  return { toasts, pushToast, pushToasts, dismissToast, clearToasts, holdToast, releaseToast }
}
