<template>
  <div class="tx-shell">
    <div class="tx-header">
      <h2 class="tx-title">Control Nodes</h2>
      <div class="tx-actions">
        <button class="tx-btn tx-btn-blue" @click="$emit('bulk', 'power', 'status')">Power Status</button>
        <button class="tx-btn tx-btn-green" @click="$emit('bulk', 'power', 'on')">Power ON</button>
        <button class="tx-btn tx-btn-orange" @click="$emit('bulk', 'power', 'reset')">Reset</button>
        <button class="tx-btn tx-btn-red" @click="$emit('bulk', 'power', 'off')">Power OFF</button>
      </div>
    </div>

    <div class="tx-table-wrap">
      <table class="tx-table">
        <thead>
          <tr>
            <th><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
            <th>NODE</th>
            <th>POWER</th>
            <th>SEL</th>
            <th>CHASSIS</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.node">
            <td><input type="checkbox" :checked="selectedSet.has(row.node)" @change="toggleOne(row.node)" /></td>
            <td>{{ row.node }}</td>
            <td>{{ row.power }}</td>
            <td>{{ row.sel }}</td>
            <td>{{ row.chassis }}</td>
            <td class="tx-actions-cell">
              <button class="tx-link" @click="$emit('single', 'power', 'status', row.node)">Status</button>
              <button class="tx-link" @click="$emit('single', 'power', 'on', row.node)">On</button>
              <button class="tx-link" @click="$emit('single', 'power', 'off', row.node)">Off</button>
              <button class="tx-link" @click="$emit('single', 'power', 'reset', row.node)">Reset</button>
              <button class="tx-link" @click="$emit('single', 'sel', 'list', row.node)">SEL List</button>
              <button class="tx-link" @click="$emit('single', 'chassis', 'identify', row.node)">Identify</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ControlStatusRow } from '@/types'
import { computed } from 'vue'

const props = defineProps<{ rows: ControlStatusRow[]; selected: string[] }>()
const emit = defineEmits<{
  bulk: [system: string, action: string]
  single: [system: string, action: string, node: string]
  toggleSelect: [next: string[]]
}>()

const selectedSet = computed(() => new Set(props.selected))
const allSelected = computed(() => props.rows.length > 0 && props.rows.every((r) => selectedSet.value.has(r.node)))

function toggleOne(node: string) {
  const next = new Set(selectedSet.value)
  if (next.has(node)) next.delete(node)
  else next.add(node)
  emit('toggleSelect', [...next])
}

function toggleAll() {
  if (allSelected.value) emit('toggleSelect', [])
  else emit('toggleSelect', props.rows.map((r) => r.node))
}
</script>
