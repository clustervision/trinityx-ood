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

const homeUrl = computed(() => {
  const ctx = window.CONTEXT_URL || ''
  if (ctx) return ctx
  try {
    return `https://${window.location.hostname}:8080`
  } catch {
    return '#'
  }
})

const logoSrc = computed(() => {
  const appUrl = window.APP_URL || ''
  if (appUrl) return `${appUrl.replace(/\/$/, '')}/static/img/logo.png`
  return '/static/img/logo.png'
})
</script>
