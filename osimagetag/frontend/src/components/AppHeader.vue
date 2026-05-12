<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img src="/public/img/logo.png" alt="Logo" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="homeUrl" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a href="#" class="tx-breadcrumb-link" @click.prevent>OS Image Tags</a>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { baseUrl } from '../api'

const homeUrl = computed(() => {
  const raw = (typeof window !== 'undefined' && window.APP_URL) || ''
  if (raw) {
    try {
      const u = new URL(raw)
      return `https://${u.hostname}:8080`
    } catch { /* fall through */ }
  }
  const b = baseUrl()
  if (b) {
    try { return `https://${new URL(b, 'http://localhost').hostname}:8080` } catch { /* fall through */ }
  }
  return typeof window !== 'undefined' ? `https://${window.location.hostname}:8080` : '#'
})
</script>
