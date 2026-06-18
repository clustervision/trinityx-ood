<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

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
