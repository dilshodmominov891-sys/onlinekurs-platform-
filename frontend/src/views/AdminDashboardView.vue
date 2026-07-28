<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, socketURL, apiUrl } from '../lib'
import { io } from 'socket.io-client'
import ClassCard from '../components/ClassCard.vue'

const router = useRouter()
const classes = ref([])
const results = ref([])
const courses = ref([])
const teachers = ref([])
const overview = ref({ students_count: 0, active_students_count: 0, active_students: [], recent_students: [], teachers_count: 0, courses_count: 0, unlocked_count: 0, live_join_count: 0, tests_count: 0, results_count: 0 })
const error = ref('')
const lessonMessage = ref('')
const teacherMessage = ref('')
const form = reactive({ title: '', description: '' })
const lessonForm = reactive({ course_id: '', title: '', summary: '', video_url: '', order_no: 1, is_preview: false })
const teacherForm = reactive({ full_name: '', username: '', password: '' })
let adminSocket
let overviewTimer

async function load() {
  try {
    const sessionRes = await api.get('/admin/session')
    if (!sessionRes.data.is_admin) {
      router.push('/admin/login')
      return
    }
    const [classesRes, resultsRes, coursesRes, teachersRes, overviewRes] = await Promise.all([
      api.get('/classes'),
      api.get('/admin/results'),
      api.get('/admin/courses'),
      api.get('/admin/teachers'),
      api.get('/admin/overview'),
    ])
    classes.value = classesRes.data.classes || []
    results.value = resultsRes.data.results || []
    courses.value = coursesRes.data.courses || []
    teachers.value = teachersRes.data.teachers || []
    overview.value = overviewRes.data || overview.value
    if (!lessonForm.course_id && courses.value.length) lessonForm.course_id = String(courses.value[0].id)
  } catch {
    router.push('/admin/login')
  }
}


async function refreshOverview() {
  try {
    const { data } = await api.get('/admin/overview')
    overview.value = { ...overview.value, ...data }
  } catch {}
}

function connectAdminSocket() {
  if (adminSocket) return
  adminSocket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  adminSocket.on('connect', () => adminSocket.emit('admin-watch'))
  adminSocket.on('admin-overview-live', (payload) => {
    overview.value = { ...overview.value, ...payload }
  })
}

async function createClass() {
  error.value = ''
  try {
    await api.post('/classes', form)
    form.title = ''
    form.description = ''
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'Saqlashda xato.'
  }
}

async function addLesson() {
  error.value = ''
  lessonMessage.value = ''
  try {
    await api.post(`/admin/courses/${lessonForm.course_id}/lessons`, lessonForm)
    lessonMessage.value = 'Video darslik qo‘shildi.'
    lessonForm.title = ''
    lessonForm.summary = ''
    lessonForm.video_url = ''
    lessonForm.order_no = 1
    lessonForm.is_preview = false
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'Video darslik qo‘shilmadi.'
  }
}

async function createTeacher() {
  error.value = ''
  teacherMessage.value = ''
  try {
    const { data } = await api.post('/admin/teachers', teacherForm)
    teacherMessage.value = data.message || 'Ustoz yaratildi.'
    teacherForm.full_name = ''
    teacherForm.username = ''
    teacherForm.password = ''
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'Ustoz yaratilmadi.'
  }
}

async function deleteTeacher(item) {
  error.value = ''
  teacherMessage.value = ''
  const name = item?.full_name || item?.username || 'ustoz'
  if (!confirm(`${name} o‘chirilsinmi?`)) return
  try {
    const { data } = await api.delete(`/admin/teachers/${item.id}`)
    teacherMessage.value = data.message || 'Ustoz o‘chirildi.'
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'Ustoz o‘chirilmadi.'
  }
}

function exportSummary() {
  window.open(apiUrl('/admin/export/summary.csv'), '_blank')
}

function exportStudents() {
  window.open(apiUrl('/admin/export/students.xls'), '_blank')
}

async function logout() {
  await api.post('/admin/logout')
  router.push('/')
}

onMounted(async () => {
  await load()
  connectAdminSocket()
  overviewTimer = setInterval(refreshOverview, 2000)
})
onBeforeUnmount(() => {
  if (overviewTimer) clearInterval(overviewTimer)
  adminSocket?.disconnect()
})
</script>

<template>
  <section class="section admin-dashboard-clean">
    <div class="card glass admin-main-card animated-card">
      <div class="video-top admin-topline">
        <div>
          <span class="pill">Admin panel</span>
          <h2>Admin nazorat markazi</h2>
          <p class="muted">Bu bo‘limda faqat umumiy nazorat cardlari turadi. Ustoz yaratish va ma’lumotlar alohida bo‘limlarga ajratildi.</p>
        </div>
        <button class="btn btn-secondary btn-sm" @click="logout">Chiqish</button>
      </div>

      <div class="admin-live-hero">
        <div>
          <span class="pill admin-kicker">Real vaqt nazorati</span>
          <h3>Platformadagi o‘quvchilar soni avtomatik yangilanadi</h3>
          <p class="muted">O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.</p>
        </div>
        <div class="online-orb">
          <strong>{{ overview.active_students_count || 0 }}</strong>
          <span>hozir online</span>
        </div>
      </div>

      <div class="stats-grid premium-stats-grid">
        <div class="mini-card premium-stat-card active hover-card"><strong>Hozir saytda</strong><div class="big-stat">{{ overview.active_students_count || 0 }}</div><span class="muted">Real vaqt o‘quvchilar</span></div>
        <div class="mini-card premium-stat-card hover-card"><strong>Jami o‘quvchi</strong><div class="big-stat">{{ overview.students_count }}</div><span class="muted">Registratsiyadan o‘tganlar</span></div>
        <div class="mini-card premium-stat-card hover-card"><strong>Ustoz</strong><div class="big-stat">{{ overview.teachers_count }}</div><span class="muted">Yaratilgan o‘qituvchilar</span></div>
        <div class="mini-card premium-stat-card hover-card"><strong>Kurs</strong><div class="big-stat">{{ overview.courses_count }}</div><span class="muted">Jami kurslar</span></div>
        <div class="mini-card premium-stat-card hover-card"><strong>Sotib olingan</strong><div class="big-stat">{{ overview.unlocked_count }}</div><span class="muted">Kurs ochish soni</span></div>
        <div class="mini-card premium-stat-card hover-card"><strong>Natijalar</strong><div class="big-stat">{{ overview.results_count }}</div><span class="muted">Test topshirishlar</span></div>
      </div>

      <div class="online-list-card section compact-online-card hover-card">
        <div class="section-head compact-head">
          <div><h3>Hozir platformadagi o‘quvchilar</h3><p class="muted">Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.</p></div>
          <span class="pill live-dot">{{ overview.active_students_count || 0 }} online</span>
        </div>
        <div class="student-list compact-student-list">
          <div v-for="item in (overview.active_students || []).slice(0, 3)" :key="'online-' + (item.id || item.username)" class="student-item online-student-row hover-card">
            <div class="avatar-mini">{{ (item.first_name || item.name || 'O').slice(0,1) }}</div>
            <div>
              <strong>{{ item.name || ((item.first_name || '') + ' ' + (item.last_name || '')).trim() }}</strong>
              <div class="muted small-text">{{ item.email || 'email yo‘q' }} • {{ item.phone || 'telefon yo‘q' }}</div>
            </div>
            <span class="pill live-dot">online</span>
          </div>
          <template v-if="!(overview.active_students || []).length">
            <div v-for="item in (overview.recent_students || []).slice(0, 3)" :key="'recent-' + item.id" class="student-item online-student-row offline-preview-row hover-card">
              <div class="avatar-mini">{{ (item.first_name || 'O').slice(0,1) }}</div>
              <div>
                <strong>{{ ((item.first_name || '') + ' ' + (item.last_name || '')).trim() || item.username }}</strong>
                <div class="muted small-text">{{ item.email || 'email yo‘q' }} • {{ item.phone || 'telefon yo‘q' }}</div>
              </div>
              <span class="pill">ro‘yxatda</span>
            </div>
            <p v-if="!(overview.recent_students || []).length" class="muted">Hali o‘quvchi yo‘q.</p>
          </template>
        </div>
      </div>

      <div class="row gap-sm wrap section compact-export-row">
        <RouterLink class="btn" to="/admin/teachers">Ustoz yaratish bo‘limi</RouterLink>
        <RouterLink class="btn btn-secondary" to="/admin/info">Ma’lumotlar bo‘limi</RouterLink>
      </div>
      <div v-if="error" class="flash error">{{ error }}</div>
    </div>
  </section>
</template>
