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
    <div v-if="open" class="tx-modal-overlay" @mousedown.self="emit('close')">
      <div class="tx-sel-log-dialog" role="dialog" aria-labelledby="sel-log-title" aria-modal="true">
        <button type="button" class="tx-modal-x" aria-label="Close" @click="emit('close')">&times;</button>
        <h2 id="sel-log-title" class="tx-sel-log-title">{{ title }}</h2>

        <div v-if="loading" class="tx-sel-log-loading" aria-live="polite">
          <span class="tx-table-loading-spinner" aria-hidden="true" />
          <span>{{ loadingLabel }}</span>
        </div>

        <pre v-else-if="displayText" class="tx-sel-log-compact">{{ displayText }}</pre>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import type { SelLogEntry } from '@/types'
import { formatSelLogText, selLogModalTitle } from '@/utils/selLogDisplay'
import { computed } from 'vue'

const props = defineProps<{
  open: boolean
  loading?: boolean
  entries: SelLogEntry[]
  nodeCount?: number
  loadingDetail?: string
}>()

const emit = defineEmits<{
  close: []
}>()

const title = computed(() =>
  selLogModalTitle(props.entries, Boolean(props.loading), props.nodeCount),
)

const displayText = computed(() => formatSelLogText(props.entries))

const loadingLabel = computed(() => props.loadingDetail || 'Fetching system event log…')
</script>
