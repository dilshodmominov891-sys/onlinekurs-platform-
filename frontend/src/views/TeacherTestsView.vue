<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { api } from '../lib'
import * as XLSX from 'xlsx'

const track = ref('frontend')
const level = ref('1-bosqich')
const tests = ref([])
const loading = ref(false)
const error = ref('')
const excelNotice = ref('')
const adminCourses = ref([])
const uploadForm = reactive({ course_id: '', title: '', questions: [] })
const summaries = ref({})

const levels = ['1-bosqich', '2-bosqich', '3-bosqich']
const tracks = [
  { value: 'frontend', label: 'Frontend' },
  { value: 'backend', label: 'Backend' },
]

const filteredCourses = computed(() => adminCourses.value.filter((c) => c.track === track.value && c.level === level.value))

async function loadAdminCourses() {
  const { data } = await api.get('/admin/courses')
  adminCourses.value = data.courses || []
  if (!uploadForm.course_id && filteredCourses.value.length) uploadForm.course_id = String(filteredCourses.value[0].id)
}

async function loadTests() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/practice-tests', { params: { track: track.value, level: level.value } })
    tests.value = data.tests || []
    const entries = await Promise.all(
      tests.value.map(async (item) => {
        try {
          const res = await api.get(`/admin/tests/${item.id}/summary`)
          return [item.id, res.data.summary]
        } catch {
          return [item.id, null]
        }
      })
    )
    summaries.value = Object.fromEntries(entries)
  } catch (err) {
    error.value = err.response?.data?.error || 'Testlar yuklanmadi.'
  } finally {
    loading.value = false
  }
}

async function importExcel(event) {
  excelNotice.value = ''
  error.value = ''
  const file = event.target.files?.[0]
  if (!file) return
  try {
    const buffer = await file.arrayBuffer()
    const wb = XLSX.read(buffer, { type: 'array' })
    const ws = wb.Sheets[wb.SheetNames[0]]
    const rows = XLSX.utils.sheet_to_json(ws, { defval: '' })
    const normalized = rows.map((row) => ({
      question: String(row.question || row.Question || row.savol || row.Savol || '').trim(),
      options: {
        A: String(row.a || row.A || row['variant_a'] || '').trim(),
        B: String(row.b || row.B || row['variant_b'] || '').trim(),
        C: String(row.c || row.C || row['variant_c'] || '').trim(),
        D: String(row.d || row.D || row['variant_d'] || '').trim(),
      },
      correct: String(row.correct || row.Correct || 'A').trim().toUpperCase(),
    })).filter((q) => q.question && q.options.A && q.options.B && q.options.C && q.options.D && ['A', 'B', 'C', 'D'].includes(q.correct))

    if (!normalized.length) {
      error.value = 'Excel formati noto‘g‘ri. Ustunlar: question, a, b, c, d, correct'
      return
    }

    uploadForm.questions = normalized
    uploadForm.title = file.name.replace(/\.[^.]+$/, '') || `${track.value} ${level.value} testi`
    excelNotice.value = `${normalized.length} ta savol yuklandi. Endi Testni saqlash tugmasini bosing.`
  } catch {
    error.value = 'Excelni o‘qib bo‘lmadi.'
  } finally {
    event.target.value = ''
  }
}

async function saveImportedTest() {
  error.value = ''
  excelNotice.value = ''
  if (!uploadForm.course_id || !uploadForm.title || !uploadForm.questions.length) {
    error.value = 'Kurs, test nomi va Excel savollari kerak.'
    return
  }
  try {
    const { data } = await api.post('/admin/practice-tests/import', uploadForm)
    excelNotice.value = data.message || 'Test saqlandi.'
    uploadForm.questions = []
    uploadForm.title = ''
    uploadForm.course_id = filteredCourses.value.length ? String(filteredCourses.value[0].id) : ''
    await loadTests()
  } catch (err) {
    error.value = err.response?.data?.error || 'Testni saqlab bo‘lmadi.'
  }
}

onMounted(async () => {
  await loadAdminCourses()
  await loadTests()
})

watch([track, level], async () => {
  if (filteredCourses.value.length) uploadForm.course_id = String(filteredCourses.value[0].id)
  else uploadForm.course_id = ''
  await loadTests()
})
</script>

<template>
  <section class="section">
    <div class="card glass sidebar-info-card practice-layout-card">
      <div class="section-head">
        <div>
          <h2>Test qo‘shish bo‘limi</h2>
          <p class="muted">Ustoz frontend yoki backend yo‘nalishini, bosqichini va kursini tanlab Excel orqali test qo‘shadi.</p>
        </div>
        <span class="pill">Faqat ustoz uchun</span>
      </div>

      <div class="grid-2 gap-lg practice-filter-grid">
        <div class="track-switcher">
          <button v-for="item in tracks" :key="item.value" class="track-btn" :class="{ active: track === item.value }" @click="track = item.value">{{ item.label }}</button>
        </div>
        <select v-model="level">
          <option v-for="item in levels" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>

      <div class="card glass admin-practice-upload teacher-test-upload-card">
        <div class="section-head compact-head">
          <div>
            <h3>Excel orqali test yuklash</h3>
            <p class="muted">Savollar formatida question, a, b, c, d, correct ustunlari bo‘lishi kerak.</p>
          </div>
          <span class="pill">{{ track === 'frontend' ? 'Frontend' : 'Backend' }} · {{ level }}</span>
        </div>
        <div class="stack">
          <select v-model="uploadForm.course_id">
            <option disabled value="">Kursni tanlang</option>
            <option v-for="course in filteredCourses" :key="course.id" :value="String(course.id)">{{ course.title }}</option>
          </select>
          <input v-model="uploadForm.title" placeholder="Test nomi" />
          <label class="excel-inline-upload compact-upload">
            <span class="option-badge excel">XLSX</span>
            <span>Excel yuklash</span>
            <input type="file" accept=".xlsx,.xls" @change="importExcel" />
          </label>
          <button class="btn" @click="saveImportedTest">Testni saqlash</button>
        </div>
      </div>

      <div v-if="loading" class="flash success">Testlar yuklanmoqda...</div>
      <div v-if="error" class="flash error">{{ error }}</div>
      <div v-if="excelNotice" class="flash success">{{ excelNotice }}</div>

      <div class="practice-test-grid teacher-summary-grid">
        <div v-for="test in tests" :key="test.id" class="card glass practice-test-card animated-card">
          <div class="course-card-badges">
            <span class="pill">{{ test.track === 'frontend' ? 'Frontend' : 'Backend' }}</span>
            <span class="pill">{{ test.level || 'Daraja yo‘q' }}</span>
          </div>
          <h3>{{ test.title }}</h3>
          <p class="muted">{{ test.course_title || test.class_title }}</p>
          <div class="practice-meta">
            <span>{{ test.technology || 'Umumiy test' }}</span>
            <span>{{ summaries[test.id]?.attempts_count || 0 }} ta yechilgan</span>
          </div>
          <div class="teacher-mini-stats">
            <div class="mini-stat"><strong>{{ summaries[test.id]?.avg_percent ? Number(summaries[test.id].avg_percent).toFixed(1) : '0.0' }}%</strong><span>o‘rtacha</span></div>
            <div class="mini-stat"><strong>{{ summaries[test.id]?.best_score || 0 }}</strong><span>eng yaxshi</span></div>
          </div>
        </div>
      </div>

      <div v-if="!loading && !tests.length" class="card glass empty-state-card">Bu yo‘nalish va bosqich uchun hali test yo‘q.</div>
    </div>
  </section>
</template>
