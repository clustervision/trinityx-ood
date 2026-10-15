import { ref } from 'vue'
import { fetchStatus } from '../api.js'

export const images = ref([])
export const progress = ref(null)
export const apiError = ref('')

let pollTimer = null

export async function refreshStatus() {
  try {
    const data = await fetchStatus()
    images.value = data.images || []
    progress.value = data.progress || null
    apiError.value = data.error || ''
  } catch (err) {
    apiError.value = err instanceof Error ? err.message : String(err)
  }
}

export function startPolling(isPaused) {
  refreshStatus()
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(() => {
    if (!isPaused()) refreshStatus()
  }, 2000)
}

export function stopPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = null
}
