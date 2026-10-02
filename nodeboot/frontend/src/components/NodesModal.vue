<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ICON_CONSOLE } from '../utils/icons.js'

const props = defineProps({
  imgName: { type: String, required: true },
  group: { type: Object, required: true },
})

defineEmits(['close', 'open-console'])

const search = ref('')
const searchInput = ref(null)

const filteredNodes = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return props.group.failedNodes
  return props.group.failedNodes.filter((node) => node.toLowerCase().includes(query))
})

onMounted(() => {
  nextTick(() => searchInput.value?.focus())
})
</script>

<template>
  <div class="modal-overlay open" @click="$emit('close')">
    <div class="modal-box" @click.stop>
      <div class="modal-header">
        <span class="modal-title fmono">
          Not booting ({{ group.failed }}) — {{ imgName }} / {{ group.name }}
        </span>
        <button class="modal-close" aria-label="Close" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <input
          ref="searchInput"
          v-model="search"
          type="text"
          class="modal-search"
          placeholder="Search nodes..."
        />
        <div v-if="filteredNodes.length" class="modal-node-list">
          <div
            v-for="node in filteredNodes"
            :key="node"
            class="modal-node-row"
            @click="$emit('open-console', node)"
          >
            <span>{{ node }}</span>
            <span class="console-icon" v-html="ICON_CONSOLE" />
          </div>
        </div>
        <div v-else class="modal-empty">No nodes match your search.</div>
      </div>
    </div>
  </div>
</template>
