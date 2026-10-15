<script setup>
import { computed } from 'vue'
import { formatAge } from '../utils/stages.js'

const props = defineProps({
  images: { type: Array, default: () => [] },
  progress: { type: Object, default: null },
  selected: { type: String, default: null },
})

defineEmits(['open-console', 'view-all'])

const view = computed(() => {
  for (const image of props.images) {
    for (const group of image.groups) {
      if (`${image.name}/${group.name}` === props.selected) return group.progress
    }
  }
  return props.progress
})

const rows = computed(() => view.value?.notBooted || [])

// ponytail: the panel shows the first rows; "view all" opens the full list in a modal
const LIMIT = 10
const shown = computed(() => rows.value.slice(0, LIMIT))
</script>

<template>
  <section class="panel boot-panel">
    <h2 class="boot-panel-title">Not Booted</h2>
    <div class="boot-table-wrap">
      <table class="boot-table not-booted-table">
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
          <tr
            v-for="(row, index) in shown"
            :key="row.node"
            class="boot-row"
            title="Open console"
            @click="$emit('open-console', row.node)"
          >
            <td class="num dim fmono">{{ index + 1 }}</td>
            <td class="name fmono">{{ row.node }}</td>
            <td class="dim">{{ row.group }}</td>
            <td class="fmono">{{ row.stage }}</td>
            <td class="fmono">{{ row.step }}</td>
            <td class="num fmono">{{ formatAge(row.minutes) }}</td>
            <td><span v-if="row.condition" class="condition" :class="`is-${row.condition}`">{{ row.condition }}</span></td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="7" class="boot-empty">{{ view ? 'Every node in this boot has booted.' : 'No nodes are assigned to any group yet.' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <button class="clear-view view-all" @click="$emit('view-all', rows)">view all ({{ rows.length }})</button>
  </section>
</template>
