<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const state = computed(() => history.state || {})
const percentage = computed(() => {
  const total = Number(state.value.total || 0)
  const score = Number(state.value.score || 0)
  return total ? Math.round((score / total) * 100) : 0
})
const incorrect = computed(() => Math.max(0, Number(state.value.total || 0) - Number(state.value.score || 0)))
const circleStyle = computed(() => ({
  background: `conic-gradient(#22c55e 0 ${percentage.value}%, rgba(255,255,255,0.08) ${percentage.value}% 100%)`
}))
</script>

<template>
  <div class="center-box">
    <div class="card glass form-card text-center result-card-wide">
      <h1>Test natijasi</h1>
      <div class="score-ring" :style="circleStyle">
        <div class="score-ring-inner">
          <strong>{{ percentage }}%</strong>
          <span>{{ state.score ?? 0 }}/{{ state.total ?? 0 }}</span>
        </div>
      </div>
      <p>{{ state.total ?? 0 }} ta testdan {{ state.score ?? 0 }} tasini to‘g‘ri yechdingiz.</p>
      <div class="info-list result-grid-stats">
        <div class="mini-card"><strong>Foiz</strong><span>{{ percentage }}%</span></div>
        <div class="mini-card"><strong>To‘g‘ri</strong><span>{{ state.score ?? 0 }}</span></div>
        <div class="mini-card"><strong>Noto‘g‘ri</strong><span>{{ incorrect }}</span></div>
        <div class="mini-card"><strong>Jami</strong><span>{{ state.total ?? 0 }}</span></div>
      </div>
      <button class="btn" @click="router.push('/practice-tests')">Yana test yechish</button>
    </div>
  </div>
</template>
