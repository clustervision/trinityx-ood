<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img :src="logoSrc" alt="Logo" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="homeUrl" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a href="#" class="tx-breadcrumb-link" @click.prevent>OS Images</a>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { baseUrl } from '../api.js'
import { publicAssetUrl } from '../utils/publicAssets.js'

function backendHostname() {
  const raw = import.meta.env.VITE_APP_URL || ''
  if (raw) {
    try { return new URL(raw).hostname } catch { /* fall through */ }
  }
  const base = baseUrl()
  if (base) {
    try { return new URL(base, 'http://localhost').hostname } catch { /* fall through */ }
  }
  return typeof window !== 'undefined' ? window.location.hostname : ''
}

const homeUrl = computed(() => {
  const raw = import.meta.env.VITE_APP_URL || ''
  if (raw) {
    try {
      const u = new URL(raw)
      return `${u.protocol}//${u.hostname}:8080`
    } catch { /* fall through */ }
  }
  const h = backendHostname()
  return h ? `https://${h}:8080` : '#'
})

const logoSrc = computed(() => publicAssetUrl('img/logo.png'))
</script>
