<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import BlockBar from './BlockBar.vue'
import { FUNNEL_STAGES, funnelOf, pctOf } from '../utils/stages.js'
import { formatCount } from '../utils/progress.js'

const props = defineProps({
  images: { type: Array, default: () => [] },
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
const hintPad = ref(null)
const funnelEl = ref(null)
let resizeObserver
onMounted(() => {
  const heads = [...document.querySelectorAll('.boot-table thead th')]
  const osImage = heads[2]
  const done = heads.find((th) => th.textContent.trim() === 'done')
  if (!osImage) return
  const update = () => {
    tabsLeft.value = osImage.offsetLeft
    const hint = funnelEl.value?.querySelector('.stage-hint')
    if (!done || !hint) return
    // "done" is centred in its cell, so find where the word itself starts
    const range = document.createRange()
    range.selectNodeContents(done)
    const scale = done.getBoundingClientRect().width / done.offsetWidth || 1
    const wordLeft = done.offsetLeft + (done.offsetWidth - range.getBoundingClientRect().width / scale) / 2
    hintPad.value = Math.max(0, Math.round(wordLeft - hint.offsetLeft))
  }
  // the table is full width, so column reflows only show up on the cells themselves
  resizeObserver = new ResizeObserver(update)
  resizeObserver.observe(osImage)
  if (done) resizeObserver.observe(done)
  if (funnelEl.value) resizeObserver.observe(funnelEl.value)
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

const scope = computed(() => {
  for (const image of props.images) {
    for (const group of image.groups) {
      if (`${image.name}/${group.name}` === props.selected) return { label: group.name, image: image.name, groups: [group] }
    }
  }
  return { label: null, image: null, groups: props.images.flatMap((image) => image.groups) }
})

const funnel = computed(() => funnelOf(scope.value.groups))

const summary = computed(() => {
  const { booting, failed } = funnel.value
  const parts = [booting ? `${formatCount(booting)} booting` : 'no boot in progress']
  if (failed) parts.push(`${formatCount(failed)} not booting`)
  return parts.join(', ')
})
</script>

<template>
  <section class="panel boot-panel" :style="{ '--tabs-left': tabsLeft !== null ? `${tabsLeft}px` : null, '--hint-pad': hintPad !== null ? `${hintPad}px` : null }">
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

    <div ref="funnelEl" class="funnel">
      <div class="funnel-row funnel-total">
        <span class="stage-name">total</span>
        <BlockBar :booted="funnel.booted" :booting="funnel.booting" :failed="funnel.failed" :total="funnel.total" />
        <span class="stage-pct fmono">{{ pctOf(funnel.booted, funnel.total) }}%</span>
        <span class="stage-count fmono">{{ formatCount(funnel.total) }} {{ funnel.total === 1 ? 'node' : 'nodes' }}</span>
        <span class="stage-hint">{{ summary }}</span>
      </div>

      <div v-for="stage in FUNNEL_STAGES" :key="stage.key" class="funnel-row">
        <span class="stage-name">{{ stage.key }}</span>
        <BlockBar :booted="funnel.reached[stage.key]" :total="funnel.total" />
        <span class="stage-pct fmono">{{ pctOf(funnel.reached[stage.key], funnel.total) }}%</span>
        <span class="stage-count fmono">{{ formatCount(funnel.reached[stage.key]) }}/{{ formatCount(funnel.total) }}</span>
        <span class="stage-hint">{{ stage.hint }}</span>
      </div>
    </div>
  </section>
</template>
