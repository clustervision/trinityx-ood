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
  if (typeof window === 'undefined') return '#'
  return `${location.protocol}//${location.hostname}:8080`
})

const logoSrc = computed(() => {
  const base = import.meta.env.BASE_URL || '/'
  return (base.endsWith('/') ? base : base + '/') + 'static/img/logo.png'
})
</script>
