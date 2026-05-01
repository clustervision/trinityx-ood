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
        <a href="#" class="tx-breadcrumb-link" @click.prevent>Nodes</a>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { baseUrl } from '../api.js'
import { publicAssetUrl } from '../utils/publicAssets.js'

/** Hostname of the TrinityX controller (from Vite env), not the dev machine. */
function backendHostname() {
  const raw = import.meta.env.VITE_NODE_BACKEND || ''
  if (raw) {
    try {
      return new URL(raw).hostname
    } catch {
      /* fall through */
    }
  }
  const base = baseUrl()
  if (base) {
    try {
      return new URL(base).hostname
    } catch {
      /* fall through */
    }
  }
  return typeof window !== 'undefined' ? window.location.hostname : ''
}

/** Logo + Home → dashboard :8080 (match API scheme when VITE_NODE_BACKEND is set: http avoids ERR_SSL_PROTOCOL_ERROR). */
const homeUrl = computed(() => {
  const raw = import.meta.env.VITE_NODE_BACKEND || ''
  if (raw) {
    try {
      const u = new URL(raw)
      return `${u.protocol}//${u.hostname}:8080`
    } catch {
      /* fall through */
    }
  }
  const h = backendHostname()
  return h ? `https://${h}:8080` : '#'
})

/** Always `public/img/logo.png` (Vite copies `public/` to site root; respects BASE_URL in deploy). */
const logoSrc = computed(() => publicAssetUrl('img/logo.png'))
</script>
