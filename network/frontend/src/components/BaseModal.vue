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
  <Teleport to="body">
    <div class="tx-modal-overlay" @mousedown.self="$emit('close')">
      <div class="tx-modal-container" :class="sizeClass">
        <button type="button" class="tx-modal-x" @click="$emit('close')">&times;</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: 'small' | 'medium' | 'large' | 'wide'
  }>(),
  { size: 'large' },
)

const emit = defineEmits<{ close: [] }>()

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

const sizeClass = computed(() => {
  if (props.size === 'small') return 'tx-modal-sm'
  if (props.size === 'medium') return 'tx-modal-md'
  if (props.size === 'wide') return 'tx-modal-wide'
  return 'tx-modal-lg'
})

onMounted(() => {
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', handleEscKey)
})
onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleEscKey)
})
</script>
