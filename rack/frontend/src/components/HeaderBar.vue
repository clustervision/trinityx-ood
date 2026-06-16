<template>
  <header class="rack-header">
    <nav class="tx-navbar">
      <ol class="tx-breadcrumb">
        <li class="tx-breadcrumb-logo">
          <a
            :href="contextUrl || 'javascript:void(0);'"
            aria-current="page"
            @click.prevent="goHome"
          >
            <img :src="logoUrl" alt="Logo" class="tx-navbar-logo" />
          </a>
        </li>
        <li
          v-for="(crumb, i) in breadcrumbs"
          :key="i"
          class="tx-breadcrumb-item"
          :class="{ active: i === breadcrumbs.length - 1 }"
        >
          <a
            v-if="i < breadcrumbs.length - 1 && crumb.view"
            :href="crumb.label === 'Home' && contextUrl ? contextUrl : 'javascript:void(0);'"
            class="tx-breadcrumb-link"
            @click.prevent="handleCrumbClick(crumb, i, breadcrumbs.length - 1)"
          >
            {{ crumb.label }}
          </a>
          <span v-else class="align-middle">{{ crumb.label }}</span>
        </li>
      </ol>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { rackStaticUrl } from '@/utils/publicAssets'

defineProps<{
  breadcrumbs: Array<{ label: string; view?: string }>
}>()

const emit = defineEmits<{
  navigate: [view: string]
}>()

const logoUrl = rackStaticUrl('static/img/logo.png')

const contextUrl =
  typeof window !== 'undefined'
    ? ((window as unknown as { CONTEXT_URL?: string }).CONTEXT_URL || window.location.origin)
    : ''

const goHome = () => {
  if (!contextUrl) return
  window.location.href = contextUrl
}

const handleCrumbClick = (crumb: { label: string; view?: string }, index: number, lastIndex: number) => {
  if (index === lastIndex || !crumb.view) return

  if (crumb.label === 'Home') {
    goHome()
  } else {
    emit('navigate', crumb.view)
  }
}
</script>

<style scoped>
.rack-header {
  width: 100%;
  min-height: 42px;
  flex-shrink: 0;
  box-sizing: border-box;
  position: relative;
  z-index: 20;
}
</style>
