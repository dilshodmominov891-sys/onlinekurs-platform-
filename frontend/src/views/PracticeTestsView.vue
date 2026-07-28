<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib'

const router = useRouter()
const track = ref('frontend')
const level = ref('1-bosqich')
const tests = ref([])
const loading = ref(false)
const error = ref('')
const sessionRole = ref(null)

const levels = ['1-bosqich', '2-bosqich', '3-bosqich']
const tracks = [
  { value: 'frontend', label: 'Frontend' },
  { value: 'backend', label: 'Backend' },
]

const isAdmin = computed(() => sessionRole.value === 'admin')

async function loadSession() {
  try {
    const { data } = await api.get('/access/session')
    sessionRole.value = data.role || null
  } catch {
    sessionRole.value = null
  }
}

async function loadTests() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/practice-tests', { params: { track: track.value, level: level.value } })
    tests.value = data.tests || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Testlar yuklanmadi.'
  } finally {
    loading.value = false
  }
}

function startTest(testId) {
  router.push({ name: 'test', params: { testId } })
}

onMounted(async () => {
  await loadSession()
  if (isAdmin.value) {
    router.push('/teacher/tests')
    return
  }
  await loadTests()
})

watch([track, level], async () => {
  if (!isAdmin.value) await loadTests()
})
</script>

<template>
  <section class="section">
    <div class="card glass sidebar-info-card practice-layout-card">
      <div class="section-head">
        <div>
          <h2>Test yechish</h2>
          <p class="muted">O‘quvchi frontend yoki backend yo‘nalishini tanlab testni yechadi. Natijalar avtomatik ustoz bo‘limidagi natijalar sahifasiga tushadi.</p>
        </div>
        <span class="pill">O‘quvchi bo‘limi</span>
      </div>

      <div class="grid-2 gap-lg practice-filter-grid">
        <div class="track-switcher">
          <button v-for="item in tracks" :key="item.value" class="track-btn" :class="{ active: track === item.value }" @click="track = item.value">{{ item.label }}</button>
        </div>
        <select v-model="level">
          <option v-for="item in levels" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>

      <div v-if="loading" class="flash success">Testlar yuklanmoqda...</div>
      <div v-if="error" class="flash error">{{ error }}</div>

      <div class="practice-test-grid">
        <div v-for="test in tests" :key="test.id" class="card glass practice-test-card animated-card">
          <div class="course-card-badges">
            <span class="pill">{{ test.track === 'frontend' ? 'Frontend' : 'Backend' }}</span>
            <span class="pill">{{ test.level || 'Daraja yo‘q' }}</span>
          </div>
          <h3>{{ test.title }}</h3>
          <p class="muted">{{ test.course_title || test.class_title }}</p>
          <div class="practice-meta"><span>{{ test.technology || 'Umumiy test' }}</span><span>{{ test.attempts_count || 0 }} ta urinish</span></div>
          <button class="btn" @click="startTest(test.id)">Testni yechish</button>
        </div>
      </div>

      <div v-if="!loading && !tests.length" class="card glass empty-state-card">Hozircha bu yo‘nalish va darajada test yo‘q.</div>
    </div>
  </section>
</template>
