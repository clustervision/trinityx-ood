<template>
  <header class="header-bar">
    <nav class="navbar navbar-light">
      <ol class="breadcrumb bg-transparent d-flex align-items-center">
        <a
          href="javascript:void(0);"
          class="breadcrumb-logo"
          aria-current="page"
          @click.prevent="goHome"
        >
          <img src="/logo.png" class="img-logo" alt="trinityX" />
        </a>
        <li
          v-for="(crumb, i) in breadcrumbs"
          :key="i"
          class="breadcrumb-item"
          :class="{ active: i === breadcrumbs.length - 1 }"
        >
          <a
            v-if="i < breadcrumbs.length - 1 && crumb.view"
            href="javascript:void(0);"
            class="align-middle"
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
defineProps<{
  breadcrumbs: Array<{ label: string; view?: string }>
}>()

const emit = defineEmits<{
  navigate: [view: string]
}>()

const goHome = () => {
  if (typeof window !== 'undefined') {
    const contextUrl = (window as unknown as { CONTEXT_URL?: string }).CONTEXT_URL || '';
    if (contextUrl) {
      window.location.href = contextUrl;
    } else {
      window.location.href = window.location.origin;
    }
  }
};

const handleCrumbClick = (crumb: { label: string; view?: string }, index: number, lastIndex: number) => {
  if (index === lastIndex || !crumb.view) return;

  if (crumb.label === 'Home') {
    goHome();
  } else {
    emit('navigate', crumb.view);
  }
};
</script>

<style scoped>
.header-bar {
  width: 100%;
  height: 52px;
  min-height: 52px;
  flex-shrink: 0;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  position: relative;
  z-index: 20;
  background-color: #e7e7e7;
  box-shadow: 0 0.125rem 0.25rem rgba(161, 172, 184, 0.4);
  border: none;
}

.header-bar *,
.header-bar *::before,
.header-bar *::after {
  border-left: none !important;
  border-right: none !important;
}

.navbar {
  width: 100%;
  background-color: transparent;
  position: relative;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  height: 100%;
  box-sizing: border-box;
}

.img-logo {
  width: 40px;
  height: 40px;
  margin-right: 20px;
  padding: 0;
}

.breadcrumb-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  cursor: pointer;
}

.breadcrumb {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 0;
  padding: 0;
  list-style: none;
  background: transparent;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: "/";
  padding: 0 0.5rem;
  color: #007bff;
}

.breadcrumb-item .align-middle {
  color: #007bff;
  text-decoration: none;
  background-color: transparent;
  font-family: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  font-size: 0.9375rem;
  font-weight: normal;
}

.breadcrumb-item a.align-middle:hover {
  text-decoration: underline;
}

.breadcrumb-item.active .align-middle {
  cursor: default;
}

.breadcrumb-item.active .align-middle:hover {
  text-decoration: none;
}
</style>
