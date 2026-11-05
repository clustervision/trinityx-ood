<script setup>
import { ref, watch, onMounted } from 'vue'
import { fetchConsole } from '../api.js'

const props = defineProps({
  nodeName: { type: String, required: true },
})

defineEmits(['close'])

const loading = ref(true)
const lines = ref([])
const message = ref('')
const error = ref('')

async function loadConsole() {
  loading.value = true
  error.value = ''
  try {
    const result = await fetchConsole(props.nodeName)
    lines.value = result.lines || []
    message.value = result.message || ''
  } catch (err) {
    error.value = `could not load console output: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    loading.value = false
  }
}

onMounted(loadConsole)
watch(() => props.nodeName, loadConsole)
</script>

<template>
  <div class="modal-overlay open" @click="$emit('close')">
    <div class="modal-box console-mode" @click.stop>
      <div class="modal-header">
        <span class="modal-title fmono">Console — {{ nodeName }}</span>
        <button class="modal-close" aria-label="Close" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="console-output">
          <div v-if="loading">$ connecting to node...</div>
          <div v-else-if="error">$ {{ error }}</div>
          <template v-else-if="lines.length">
            <div v-for="(line, index) in lines" :key="index">$ {{ line }}</div>
          </template>
          <div v-else>$ {{ message || 'no console output captured yet' }}</div>
          <div>
            $ <span class="console-cursor">▋</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
