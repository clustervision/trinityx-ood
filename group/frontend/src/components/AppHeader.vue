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
        <a href="#" class="tx-breadcrumb-link" @click.prevent>Group</a>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { baseUrl } from '../api.js'

/** Hostname of the TrinityX controller (from Vite env), not the dev machine. */
function backendHostname() {
  const raw = import.meta.env.VITE_GROUP_BACKEND || ''
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

/** Logo + Home → dashboard :8080 (match API scheme when VITE_GROUP_BACKEND is set: http avoids ERR_SSL_PROTOCOL_ERROR). */
const homeUrl = computed(() => {
  const raw = import.meta.env.VITE_GROUP_BACKEND || ''
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

/** Always load from this SPA's public/static/img/logo.png (same origin as the page), not window.APP_URL. */
const logoSrc = computed(() => {
  const base = import.meta.env.BASE_URL || '/'
  const path = (base.endsWith('/') ? base : base + '/') + 'static/img/logo.png'
  if (typeof window !== 'undefined') {
    try {
      return new URL(path, window.location.origin).href
    } catch {
      /* fall through */
    }
  }
  return path
})
</script>
