<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { formatAge } from '../utils/stages.js'

const props = defineProps({
  rows: { type: Array, required: true },
})

defineEmits(['close', 'open-console'])

const search = ref('')
const searchInput = ref(null)

const filtered = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return props.rows
  return props.rows.filter((row) => [row.node, row.group, row.stage, row.step, row.condition].join(' ').toLowerCase().includes(query))
})

onMounted(() => {
  nextTick(() => searchInput.value?.focus())
})
</script>

<template>
  <div class="modal-overlay open" @click="$emit('close')">
    <div class="modal-box wide" @click.stop>
      <div class="modal-header">
        <span class="modal-title fmono">Not Booted ({{ rows.length }})</span>
        <button class="modal-close" aria-label="Close" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <input
          ref="searchInput"
          v-model="search"
          type="text"
          class="modal-search"
          placeholder="Search nodes, groups, stages..."
        />
        <table v-if="filtered.length" class="boot-table not-booted-table">
          <thead>
            <tr>
              <th class="num">#</th>
              <th>node</th>
              <th>group</th>
              <th>stage</th>
              <th>step</th>
              <th class="num">since</th>
              <th>condition</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in filtered" :key="row.node" class="boot-row" title="Open console" @click="$emit('open-console', row.node)">
              <td class="num dim fmono">{{ index + 1 }}</td>
              <td class="name fmono">{{ row.node }}</td>
              <td class="dim">{{ row.group }}</td>
              <td class="fmono">{{ row.stage }}</td>
              <td class="fmono">{{ row.step }}</td>
              <td class="num fmono">{{ formatAge(row.minutes) }}</td>
              <td><span v-if="row.condition" class="condition" :class="`is-${row.condition}`">{{ row.condition }}</span></td>
            </tr>
          </tbody>
        </table>
        <div v-else class="modal-empty">No nodes match your search.</div>
      </div>
    </div>
  </div>
</template>
