<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../lib'

const frontendResults = ref([])
const backendResults = ref([])
const error = ref('')

async function load() {
  try {
    const [front, back] = await Promise.all([
      api.get('/admin/results', { params: { track: 'frontend' } }),
      api.get('/admin/results', { params: { track: 'backend' } }),
    ])
    frontendResults.value = front.data.results || []
    backendResults.value = back.data.results || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Natijalar yuklanmadi.'
  }
}
onMounted(load)
</script>

<template>
  <section class="section">
    <div class="section-head">
      <div>
        <h2>Natijalar bo‘limi</h2>
        <p class="muted">O‘quvchilarning test natijalari faqat ustozlarga ko‘rinadi.</p>
      </div>
      <span class="pill">Admin nazorati</span>
    </div>
    <div v-if="error" class="flash error">{{ error }}</div>
  </section>

  <section class="grid-2 gap-lg">
    <div class="card glass">
      <div class="section-head"><div><h3>Frontend natijalari</h3></div><span class="pill">Frontend</span></div>
      <div class="results-list">
        <div v-for="item in frontendResults" :key="item.id" class="result-item rich-result-item tall-result-item">
          <div>
            <strong>{{ item.student_name }}</strong>
            <div class="muted small-text">{{ item.test_title }} · {{ item.level || '-' }} · {{ item.technology || '-' }}</div>
            <div class="muted small-text">To‘g‘ri: {{ item.score }} / Noto‘g‘ri: {{ item.wrong }}</div>
          </div>
          <div class="result-summary-right">
            <strong>{{ item.score }}/{{ item.total }}</strong>
            <span>{{ item.percent }}%</span>
          </div>
        </div>
        <p v-if="!frontendResults.length" class="muted">Hali frontend natijasi yo‘q.</p>
      </div>
    </div>

    <div class="card glass">
      <div class="section-head"><div><h3>Backend natijalari</h3></div><span class="pill">Backend</span></div>
      <div class="results-list">
        <div v-for="item in backendResults" :key="item.id" class="result-item rich-result-item tall-result-item">
          <div>
            <strong>{{ item.student_name }}</strong>
            <div class="muted small-text">{{ item.test_title }} · {{ item.level || '-' }} · {{ item.technology || '-' }}</div>
            <div class="muted small-text">To‘g‘ri: {{ item.score }} / Noto‘g‘ri: {{ item.wrong }}</div>
          </div>
          <div class="result-summary-right">
            <strong>{{ item.score }}/{{ item.total }}</strong>
            <span>{{ item.percent }}%</span>
          </div>
        </div>
        <p v-if="!backendResults.length" class="muted">Hali backend natijasi yo‘q.</p>
      </div>
    </div>
  </section>
</template>
