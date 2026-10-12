<script setup>
import { computed } from 'vue'
import BlockBar from './BlockBar.vue'
import { overviewOf, pctOf } from '../utils/stages.js'
import { formatCount } from '../utils/progress.js'

const props = defineProps({
  images: { type: Array, default: () => [] },
  selected: { type: String, default: null },
})

const emit = defineEmits(['select', 'show-nodes'])

const COLUMNS = ['ipxe', 'download', 'unpack', 'config', 'done']

const rows = computed(() =>
  props.images.flatMap((image) =>
    image.groups.map((group) => ({
      key: `${image.name}/${group.name}`,
      image,
      group,
      counts: overviewOf(group),
    })),
  ),
)

// Images and groups Luna knows about that have no nodes, so the image count in the
// header adds up: images in the table above plus unusedImages. Kept as two lists -
// an image that is in use can still own unused groups, and listing it beside them
// would read as a third unused image.
const unusedImages = computed(() => props.images.filter((image) => !image.groups.length))

const unusedGroups = computed(() =>
  props.images.flatMap((image) =>
    image.unusedGroups.map((group) => ({ key: `${image.name}/${group}`, group, image: image.name })),
  ),
)

const unusedSummary = computed(() => {
  const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`
  return `Not in use: ${plural(unusedImages.value.length, 'image')}, ${plural(unusedGroups.value.length, 'group')}`
})

function cell(value) {
  return value ? formatCount(value) : ''
}

function showNodes(row, reason) {
  const nodes = row.group.failedNodes.filter((n) => row.group.failedReasons[n] === reason)
  if (nodes.length) emit('show-nodes', row.image, { ...row.group, failedNodes: nodes, failed: nodes.length })
}
</script>

<template>
  <section class="panel boot-panel">
    <h2 class="boot-panel-title">Boot Overview</h2>
    <div class="boot-table-wrap">
      <table class="boot-table">
        <thead>
          <tr>
            <th class="num">#</th>
            <th>Group</th>
            <th>OS image</th>
            <th v-for="col in COLUMNS" :key="col" class="num">{{ col }}</th>
            <th class="num">failed</th>
            <th class="num">unknown</th>
            <th class="num">total</th>
            <th class="progress-col">Progress</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in rows"
            :key="row.key"
            class="boot-row"
            :class="{ selected: selected === row.key }"
            :aria-selected="selected === row.key"
            @click="emit('select', selected === row.key ? null : row.key)"
          >
            <td class="num dim fmono">{{ index + 1 }}</td>
            <td class="name">{{ row.group.name }}</td>
            <td class="name dim">{{ row.image.name }}</td>
            <td
              v-for="col in COLUMNS"
              :key="col"
              class="num fmono"
              :class="{ 'is-done': col === 'done' && row.counts.done }"
            >
              {{ cell(row.counts[col]) }}
            </td>
            <td class="num fmono">
              <button
                v-if="row.counts.failed"
                class="count-link is-failed"
                title="Show failed nodes"
                @click.stop="showNodes(row, 'error')"
              >{{ formatCount(row.counts.failed) }}</button>
            </td>
            <td class="num fmono">
              <button
                v-if="row.counts.unknown"
                class="count-link is-unknown"
                title="Show nodes with no reported state"
                @click.stop="showNodes(row, 'not_started')"
              >{{ formatCount(row.counts.unknown) }}</button>
            </td>
            <td class="num fmono strong">{{ formatCount(row.counts.total) }}</td>
            <td class="progress-col">
              <div class="row-progress">
                <BlockBar
                  :booted="row.counts.done"
                  :booting="row.counts.booting"
                  :failed="row.group.failed"
                  :total="row.counts.total"
                  :blocks="10"
                />
                <span class="row-pct fmono">{{ pctOf(row.counts.done, row.counts.total) }}%</span>
              </div>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="13" class="boot-empty">No nodes are assigned to any group yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <details v-if="unusedImages.length || unusedGroups.length" class="unused">
      <summary>{{ unusedSummary }}</summary>
      <ul v-if="unusedImages.length" class="unused-list">
        <li class="unused-item unused-head"><span>OS images with no nodes</span></li>
        <li v-for="image in unusedImages" :key="image.name" class="unused-item">
          <span class="name">{{ image.name }}</span>
        </li>
      </ul>
      <ul v-if="unusedGroups.length" class="unused-list">
        <li class="unused-item unused-head"><span>Groups with no nodes</span><span>OS image</span></li>
        <li v-for="row in unusedGroups" :key="row.key" class="unused-item">
          <span class="name">{{ row.group }}</span>
          <span class="unused-image">{{ row.image }}</span>
        </li>
      </ul>
    </details>
  </section>
</template>
