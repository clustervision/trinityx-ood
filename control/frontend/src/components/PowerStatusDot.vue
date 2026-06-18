<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

<template>
  <button
    type="button"
    class="tx-power-dot-btn"
    :class="{ 'tx-power-dot-btn--sidebar': size === 'sidebar' }"
    :disabled="disabled || !clickable"
    :aria-label="ariaLabel"
    :title="title"
    @click="$emit('click')"
  >
    <span :class="dotClass" aria-hidden="true" />
  </button>
</template>

<script setup lang="ts">
import { powerStatusDotClass, powerToggleVisualState } from '@/utils'
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  power: string
  loading?: boolean
  disabled?: boolean
  size?: 'row' | 'sidebar'
  label?: string
}>(), {
  loading: false,
  disabled: false,
  size: 'row',
  label: '',
})

defineEmits<{
  click: []
}>()

const visual = computed(() => powerToggleVisualState(props.power, props.loading))

const dotClass = computed(() => {
  if (props.loading || visual.value === 'loading') {
    return 'tx-status-dot tx-status-dot--power tx-status-loading-dot'
  }
  return powerStatusDotClass(props.power)
})

const clickable = computed(() =>
  visual.value === 'on' || visual.value === 'off' || visual.value === 'unknown',
)

const ariaLabel = computed(() => {
  const name = props.label?.trim()
  const target = name ? ` for ${name}` : ''
  if (visual.value === 'on') return `Power on${target} — click to turn off`
  if (visual.value === 'off') return `Power off${target} — click to turn on`
  if (visual.value === 'unknown') return `Power status unknown${target} — click to turn on`
  if (visual.value === 'loading') return `Power status loading${target}`
  return `Power status unknown${target}`
})

const title = computed(() => ariaLabel.value)
</script>
