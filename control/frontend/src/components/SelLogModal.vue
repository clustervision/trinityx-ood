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
