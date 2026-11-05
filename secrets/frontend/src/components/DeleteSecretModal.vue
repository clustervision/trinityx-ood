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
  <BaseModal @close="$emit('close')">
    <div class="tx-delete-confirm">
      <h3 class="tx-delete-title">Delete secret <strong>{{ item.name }}</strong>?</h3>
      <p class="tx-delete-desc">{{ item.entity }} / {{ item.owner }}</p>
      <div class="tx-delete-actions">
        <button class="tx-btn tx-btn-outline-blue" @click="$emit('close')">Cancel</button>
        <button class="tx-btn tx-btn-danger" @click="$emit('confirm')">Delete</button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import BaseModal from './BaseModal.vue'
import type { SecretRecord } from '@/types'

defineProps<{ item: SecretRecord }>()
defineEmits<{ close: []; confirm: [] }>()
</script>
