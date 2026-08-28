<script setup>
import { computed } from 'vue'
import GroupCard from './GroupCard.vue'
import { expandedIds, toggleExpanded } from '../composables/useStatus.js'
import { useProgressTrack } from '../composables/useProgressTrack.js'
import { distributeBlocks, sumGroupCounts, formatCount } from '../utils/progress.js'
import { ICON_CHECK, ICON_BOOTING, ICON_WARNING, ICON_GRID } from '../utils/icons.js'

defineProps({
  images: { type: Array, default: () => [] },
})

defineEmits(['open-console', 'see-all'])

const curveSeeds = [
  [70, 170, 65, 95],
  [90, 150, 80, 110],
  [60, 180, 55, 100],
  [100, 140, 70, 90],
  [75, 165, 90, 105],
]

const { trackEl, blockCount } = useProgressTrack(1, 24, 6, 5, 3)

function imageTotals(image) {
  return sumGroupCounts(image.groups)
}

function setFirstTrack(el) {
  trackEl.value = el instanceof HTMLElement ? el : null
}

function blockClass(image, index) {
  const totals = imageTotals(image)
  return distributeBlocks(totals.booted, totals.booting, totals.failed, totals.total, blockCount.value)[index - 1]
}
</script>

<template>
  <div class="panel images-panel">
    <div class="images-table-head">
      <div>Image Name</div>
      <div>
        <span class="nodes-head-cell">Nodes</span>
        <span class="nodes-head-cell" style="color: var(--c-green)" v-html="ICON_CHECK" />
        <span class="nodes-head-cell" style="color: var(--c-blue-strong)" v-html="ICON_BOOTING" />
        <span class="nodes-head-cell" style="color: var(--c-tan)" v-html="ICON_WARNING" />
      </div>
      <div>
        <span class="progress-head-row">
          <span class="progress-head-spacer" />
          <span class="progress-head">Progress</span>
        </span>
      </div>
    </div>

    <div>
      <div
        v-for="(image, imageIndex) in images"
        :key="image.id"
        class="image-row-wrap"
        :class="{ open: expandedIds.has(image.id) }"
      >
        <div class="image-row" @click="toggleExpanded(image.id)">
          <div class="image-row-name">
            <span class="chevron">›</span>
            <span class="image-row-title fmono">{{ image.name }}</span>
          </div>

          <div class="image-row-pills">
            <span class="pill neutral">
              <span class="pill-icon" v-html="ICON_GRID" />
              {{ formatCount(imageTotals(image).total) }}
            </span>
            <span class="pill green">
              <span class="pill-icon" v-html="ICON_CHECK" />
              {{ formatCount(imageTotals(image).booted) }}
            </span>
            <span class="pill blue">
              <span class="pill-icon" v-html="ICON_BOOTING" />
              {{ formatCount(imageTotals(image).booting) }}
            </span>
            <span class="pill tan">
              <span class="pill-icon" v-html="ICON_WARNING" />
              {{ formatCount(imageTotals(image).failed) }}
            </span>
          </div>

          <div class="image-row-progress">
            <span class="image-row-fraction fmono">
              {{ formatCount(imageTotals(image).booted) }}/{{ formatCount(imageTotals(image).total) }}
            </span>
            <div
              :ref="imageIndex === 0 ? setFirstTrack : undefined"
              class="progress-track blocks"
            >
              <div
                v-for="i in blockCount"
                :key="i"
                class="progress-block"
                :class="blockClass(image, i)"
              />
            </div>
          </div>
        </div>

        <div class="image-detail" :hidden="!expandedIds.has(image.id)">
          <p v-if="expandedIds.has(image.id) && image.groups.length === 0" class="no-groups">
            No groups for this image.
          </p>
          <div v-else-if="expandedIds.has(image.id)" class="groups-row">
            <GroupCard
              v-for="(group, groupIndex) in image.groups"
              :key="group.name"
              :group="group"
              :curve-seed="curveSeeds[groupIndex % curveSeeds.length]"
              @open-console="$emit('open-console', $event)"
              @see-all="$emit('see-all', image, $event)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
