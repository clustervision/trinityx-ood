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
  const ctx = typeof window !== 'undefined' ? (window.CONTEXT_URL || '') : ''
  if (ctx) {
    try {
      return new URL(ctx).hostname
    } catch {
      /* fall through */
    }
  }
  return typeof window !== 'undefined' ? window.location.hostname : ''
}

const homeUrl = computed(() => {
  const ctx = window.CONTEXT_URL || ''
  if (ctx) return ctx
  const h = backendHostname()
  return h ? `https://${h}:8080` : '#'
})

/** Place logo at frontend/public/static/img/logo.png → URL /static/img/logo.png */
const logoSrc = computed(() => {
  const appUrl = window.APP_URL || ''
  if (appUrl) return `${appUrl.replace(/\/$/, '')}/static/img/logo.png`
  const base = import.meta.env.BASE_URL || '/'
  return (base.endsWith('/') ? base : base + '/') + 'static/img/logo.png'
})
</script>
