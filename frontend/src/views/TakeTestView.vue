<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../lib'

const route = useRoute()
const router = useRouter()
const testId = computed(() => route.params.testId)
const test = ref(null)
const klass = ref(null)
const studentName = ref('')
const answers = reactive({})
const error = ref('')
const success = ref('')
let timer = null

async function load() {
  try {
    const [{ data }, session] = await Promise.all([
      api.get(`/tests/${testId.value}`),
      api.get('/student/session'),
    ])
    test.value = data.test
    klass.value = data.class
    const fullName = `${session.data.student?.first_name || ''} ${session.data.student?.last_name || ''}`.trim()
    studentName.value = fullName || route.query.student_name || ''
  } catch {
    router.push('/practice-tests')
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  if (!studentName.value.trim()) {
    error.value = 'Ism va familiya topilmadi.'
    return
  }
  try {
    const payload = {}
    test.value.questions.forEach((_, idx) => { payload[String(idx)] = answers[idx] || '' })
    await api.post(`/tests/${testId.value}/submit`, { student_name: studentName.value, answers: payload })
    success.value = 'Test saqlandi. Natija ustozning natijalar bo‘limiga yuborildi.'
    clearTimeout(timer)
    timer = setTimeout(() => router.push('/practice-tests'), 2500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Yuborishda xato.'
  }
}

onMounted(load)
</script>

<template>
  <section v-if="test" class="card glass take-test-card">
    <div class="video-top">
      <div>
        <h1>{{ test.title }}</h1>
        <p class="muted">Dars: {{ klass?.title }}</p>
      </div>
      <RouterLink class="btn btn-sm btn-secondary" to="/practice-tests">Testlarga qaytish</RouterLink>
    </div>

    <div class="stack">
      <div class="mini-card">
        <strong>O‘quvchi:</strong> {{ studentName }}
      </div>
      <div v-for="(q, qIdx) in test.questions" :key="qIdx" class="question-box animated-card">
        <h3>{{ qIdx + 1 }}. {{ q.question }}</h3>
        <label v-for="(value, key) in q.options" :key="key" class="option option-colored single-tone-option">
          <input v-model="answers[qIdx]" type="radio" :name="`q_${qIdx}`" :value="key" />
          <span class="option-badge single-tone-badge">{{ key }}</span>
          <span class="option-text"><strong>{{ key }}.</strong> {{ value }}</span>
        </label>
      </div>
      <button class="btn" @click="submit">Testni saqlash</button>
      <div v-if="error" class="flash error">{{ error }}</div>
      <div v-if="success" class="flash success">{{ success }}</div>
    </div>
  </section>
</template>
