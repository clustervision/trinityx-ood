<script setup lang="ts">

defineProps({
  app_url: {
    type: String,
    required: true
  },
})
</script>

<template>
  <nav class="tx-navbar">
    <ol class="tx-breadcrumb">
      <li class="tx-breadcrumb-logo">
        <a href="/">
          <img :src="`${$props.app_url}/app/assets/img/logo.png`" alt="Logo" class="tx-navbar-logo" />
        </a>
      </li>
      <li class="tx-breadcrumb-item">
        <a href="/" class="tx-breadcrumb-link">Home</a>
      </li>
      <li class="tx-breadcrumb-item">
        <a :href="`${$props.app_url}`" class="tx-breadcrumb-link">Other Device</a>
      </li>
    </ol>
  </nav>
</template>


