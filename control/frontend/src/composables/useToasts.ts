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
