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
  <div class="tx-field tx-tri-field tx-field-match tx-network-bool-toggle">
    <span class="tx-label">{{ label }}:</span>
    <div class="tx-tri-inner">
      <div class="tx-segmented" role="group" :aria-label="label">
        <button
          type="button"
          class="tx-seg"
          :class="{ 'is-active': modelValue === true }"
          data-v="true"
          @click="$emit('update:modelValue', true)"
        >
          TRUE
        </button>
        <button
          type="button"
          class="tx-seg"
          :class="{ 'is-active': modelValue === false }"
          data-v="false"
          @click="$emit('update:modelValue', false)"
        >
          FALSE
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  modelValue: boolean
}>()

defineEmits<{ 'update:modelValue': [value: boolean] }>()
</script>
