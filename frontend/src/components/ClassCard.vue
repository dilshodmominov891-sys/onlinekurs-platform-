<script setup>
import { RouterLink } from 'vue-router'
defineProps({ klass: Object })
</script>

<template>
  <div class="card class-card">
    <div :class="['badge', klass.is_live ? 'live' : 'offline']">{{ klass.is_live ? 'LIVE' : 'OFFLINE' }}</div>
    <h3>{{ klass.title }}</h3>
    <p>{{ klass.description || 'Tavsif kiritilmagan' }}</p>
    <div class="muted">{{ klass.is_live ? 'Jonli dars sahifasi tayyor.' : 'Dars ma’lumoti tayyor.' }}</div>
    <div class="class-actions">
      <RouterLink v-if="klass.is_live" class="btn btn-sm" :to="`/room/${klass.room_code}`">Darsga o‘tish</RouterLink>
      <slot />
    </div>
  </div>
</template>
