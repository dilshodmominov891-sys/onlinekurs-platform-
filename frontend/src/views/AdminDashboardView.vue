<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api, socketURL } from '../lib'
import { io } from 'socket.io-client'

const overview = ref({ students_count: 0, active_students_count: 0, active_students: [], teachers_count: 0, courses_count: 0, results_count: 0 })
const error = ref('')
const lang = ref(localStorage.getItem('edulive_lang_admin') || 'uz')
let socket = null

const text = {
  uz: {
    title: 'Admin panel', sub: 'O‘quvchilar, ustozlar, kurslar va natijalarni boshqaring.',
    students: 'O‘quvchilar', online: 'Hozir online', teachers: 'Ustozlar', courses: 'Kurslar', results: 'Natijalar',
    onlineList: 'Hozir saytdagi o‘quvchilar', noOnline: 'Hozir online o‘quvchi yo‘q.', manageStudents: 'O‘quvchilarni boshqarish', manageTeachers: 'Ustozlarni boshqarish', reports: 'Hisobotlar'
  },
  ru: {
    title: 'Админ панель', sub: 'Управляйте учениками, учителями, курсами и результатами.',
    students: 'Ученики', online: 'Сейчас онлайн', teachers: 'Учителя', courses: 'Курсы', results: 'Результаты',
    onlineList: 'Ученики сейчас на сайте', noOnline: 'Сейчас нет учеников онлайн.', manageStudents: 'Управление учениками', manageTeachers: 'Управление учителями', reports: 'Отчёты'
  }
}
function tr(key) { return text[lang.value]?.[key] || text.uz[key] || key }
function handleLang(event) { lang.value = ['uz', 'ru'].includes(event.detail) ? event.detail : 'uz' }
async function load() {
  try {
    const { data } = await api.get('/admin/overview')
    overview.value = { ...overview.value, ...data }
  } catch (err) {
    error.value = err.response?.data?.error || 'Ma’lumot yuklanmadi. Sahifani yangilab ko‘ring.'
  }
}
function connect() {
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('connect', () => socket.emit('admin-watch'))
  socket.on('admin-overview-live', payload => { overview.value = { ...overview.value, ...payload } })
}
onMounted(() => {
  window.addEventListener('edulive-lang-change', handleLang)
  load()
  connect()
})
onBeforeUnmount(() => {
  socket?.disconnect()
  window.removeEventListener('edulive-lang-change', handleLang)
})
</script>

<template>
  <section class="section simple-page-head">
    <h1>{{ tr('title') }}</h1>
    <p class="muted">{{ tr('sub') }}</p>
  </section>

  <section class="section simple-stat-grid">
    <div class="card simple-stat-card"><span>{{ tr('students') }}</span><strong>{{ overview.students_count || 0 }}</strong></div>
    <div class="card simple-stat-card"><span>{{ tr('online') }}</span><strong>{{ overview.active_students_count || 0 }}</strong></div>
    <div class="card simple-stat-card"><span>{{ tr('teachers') }}</span><strong>{{ overview.teachers_count || 0 }}</strong></div>
    <div class="card simple-stat-card"><span>{{ tr('courses') }}</span><strong>{{ overview.courses_count || 0 }}</strong></div>
    <div class="card simple-stat-card"><span>{{ tr('results') }}</span><strong>{{ overview.results_count || 0 }}</strong></div>
  </section>

  <section class="section card simple-card">
    <h2>{{ tr('onlineList') }}</h2>
    <div class="simple-list">
      <div v-for="item in overview.active_students || []" :key="item.id || item.username" class="simple-list-item compact-row">
        <strong>{{ item.name || `${item.first_name || ''} ${item.last_name || ''}`.trim() || item.username }}</strong>
        <span class="muted">{{ item.username || item.email || item.phone || '' }}</span>
      </div>
      <p v-if="!(overview.active_students || []).length" class="muted">{{ tr('noOnline') }}</p>
    </div>
  </section>

  <section class="section simple-action-grid">
    <RouterLink class="btn" to="/students">{{ tr('manageStudents') }}</RouterLink>
    <RouterLink class="btn btn-light" to="/admin/teachers">{{ tr('manageTeachers') }}</RouterLink>
    <RouterLink class="btn btn-light" to="/admin/info">{{ tr('reports') }}</RouterLink>
  </section>

  <div v-if="error" class="flash error">{{ error }}</div>
</template>
