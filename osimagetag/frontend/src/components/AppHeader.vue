<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a :href="homeUrl">
          <img :src="logoUrl" alt="Logo" class="tx-navbar-logo" />
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
import { appStaticAssetUrl } from '../api'

const homeUrl = computed(() => {
  if (typeof window !== 'undefined') {
    return `${window.location.origin}/`
  }
  return '#'
})

const logoUrl = computed(() => appStaticAssetUrl('static/img/logo.png'))
</script>
