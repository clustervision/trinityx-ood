<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import BlockBar from './BlockBar.vue'
import { formatAge } from '../utils/stages.js'
import { formatCount } from '../utils/progress.js'

const props = defineProps({
  images: { type: Array, default: () => [] },
  progress: { type: Object, default: null },
  selected: { type: String, default: null },
})

const emit = defineEmits(['select'])

// ponytail: open tabs are keys only; labels resolve from images at render time
const tabs = ref([])
watch(() => props.selected, (key) => {
  if (key && !tabs.value.includes(key)) tabs.value.push(key)
}, { immediate: true })

// ponytail: reads Boot Overview's "OS image" header straight from the DOM;
// both panels share width and padding, so its offset lines the tabs up. Column
// widths follow group names, so CSS alone cannot do this.
const tabsLeft = ref(null)
let resizeObserver
onMounted(() => {
  const osImage = document.querySelector('.boot-table thead th:nth-child(3)')
  if (!osImage) return
  const update = () => { tabsLeft.value = osImage.offsetLeft }
  // the table is full width, so column reflows only show up on the cell itself
  resizeObserver = new ResizeObserver(update)
  resizeObserver.observe(osImage)
  update()
})
onUnmounted(() => resizeObserver?.disconnect())

function tabLabel(key) {
  const [image, ...rest] = key.split('/')
  return { group: rest.join('/'), image }
}

function closeAllTabs() {
  tabs.value = []
  emit('select', null)
}

function closeTab(key) {
  tabs.value = tabs.value.filter((k) => k !== key)
  if (props.selected === key) emit('select', null)
}

// All nodes: data.progress. A selected row: that group's own cohort.
const view = computed(() => {
  for (const image of props.images) {
    for (const group of image.groups) {
      if (`${image.name}/${group.name}` === props.selected) return group.progress
    }
  }
  return props.progress
})

const summary = computed(() => {
  const p = view.value
  if (!p) return 'no node has reported a state'
  return `${formatCount(p.nodes)} ${p.anchored ? 'nodes in this boot' : 'nodes, no boot in progress'}`
})

// Same line as the CLI: "<n> silent for over 1h00m   <n> in <stage>, ...   worst <node> <age>"
const stuckLine = computed(() => {
  const stuck = view.value?.stuck || []
  if (!stuck.length) return null
  const byStage = {}
  for (const node of stuck) byStage[node.stage] = (byStage[node.stage] || 0) + 1
  const ranked = Object.entries(byStage).sort((a, b) => b[1] - a[1])
  let where = ranked.slice(0, 3).map(([stage, count]) => `${count} in ${stage}`).join(', ')
  if (ranked.length > 3) where += `, ${ranked.slice(3).reduce((sum, [, count]) => sum + count, 0)} elsewhere`
  const worst = stuck[0]
  return `${stuck.length} silent for over ${formatAge(60)}   ${where}   worst ${worst.node} ${formatAge(worst.minutes)}`
})
</script>

<template>
  <section class="panel boot-panel" :style="{ '--tabs-left': tabsLeft !== null ? `${tabsLeft}px` : null }">
    <div class="boot-panel-head">
      <h2 class="boot-panel-title">Boot Progress</h2>
      <div class="boot-tabs" role="tablist">
        <button class="boot-tab" :class="{ active: !selected }" role="tab" :aria-selected="!selected" @click="emit('select', null)">
          <span class="boot-tab-kind">all nodes</span>
        </button>
        <button
          v-for="key in tabs"
          :key="key"
          class="boot-tab"
          :class="{ active: selected === key }"
          role="tab"
          :aria-selected="selected === key"
          :title="`image: ${tabLabel(key).image}`"
          @click="emit('select', key)"
        >
          <span class="boot-tab-kind">group</span>
          <span class="fmono">{{ tabLabel(key).group }}</span>
          <span class="boot-tab-close" role="button" aria-label="Close tab" @click.stop="closeTab(key)">✕</span>
        </button>
      </div>
      <button v-if="tabs.length" class="clear-view" @click="closeAllTabs">clear view</button>
      <span v-else-if="!selected" class="scope-note">click a row above to focus a group</span>
    </div>

    <div class="funnel">
      <div class="funnel-row funnel-total">
        <span class="stage-name">total</span>
        <span class="stage-hint">{{ summary }}</span>
        <span class="stage-count fmono">{{ view ? formatCount(view.nodes) : 0 }} {{ view && view.nodes === 1 ? 'node' : 'nodes' }}</span>
        <BlockBar :booted="view ? view.total : 0" :total="100" :blocks="10" />
        <span class="stage-pct fmono">{{ view ? view.total : 0 }}%</span>
      </div>

      <template v-if="view">
        <div v-for="m in view.milestones" :key="m.milestone" class="funnel-row">
          <span class="stage-name">{{ m.milestone }}</span>
          <span class="stage-hint">{{ m.note }}</span>
          <span class="stage-count fmono">{{ formatCount(m.nodes) }}/{{ formatCount(view.nodes) }}</span>
          <BlockBar :booted="m.nodes" :total="view.nodes" :blocks="10" />
          <span class="stage-pct fmono">{{ m.progress }}%</span>
        </div>
      </template>
      <div v-else class="boot-empty">No nodes are assigned to any group yet.</div>
      <div class="funnel-row funnel-stuck" :class="{ quiet: !stuckLine }">
        <span class="stage-name">stuck</span>
        <span class="stuck-line fmono">{{ stuckLine || 'no silent nodes' }}</span>
      </div>
    </div>
  </section>
</template>
