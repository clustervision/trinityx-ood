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
        <a href="#" class="tx-breadcrumb-link" @click.prevent>Networks</a>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { baseUrl } from '@/api'
import { appUrlFromRuntime, punAppAssetUrl } from '@/utils'

function backendHostname(): string {
  const raw = appUrlFromRuntime()
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
      return new URL(base, 'http://localhost').hostname
    } catch {
      /* fall through */
    }
  }
  return window.location.hostname
}

const homeUrl = computed(() => {
  const raw = appUrlFromRuntime()
  if (raw) {
    try {
      const u = new URL(raw)
      return `https://${u.hostname}:8080`
    } catch {
      /* fall through */
    }
  }
  const h = backendHostname()
  return h ? `https://${h}:8080` : '#'
})

const logoSrc = computed(() => punAppAssetUrl('static/img/logo.png'))
</script>
