<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { api, socketURL } from './lib'
import { clearSession, hydrateSession, saveSession } from './sessionStore'
import { io } from 'socket.io-client'

const route = useRoute()
const router = useRouter()
const student = ref(null)
const teacher = ref(null)
const role = ref(null)
const activeLive = ref(null)
const mobileMenuOpen = ref(false)
const langMenuOpen = ref(false)
const lang = ref('uz')
let socket = null

const translations = {
  uz: {
    home: 'Bosh sahifa', admin: 'Admin panel', students: 'O‘quvchilar', teachers: 'Ustozlar', info: 'Hisobotlar',
    teacher: 'Ustoz paneli', createCourse: 'Kurs yaratish', tests: 'Testlar', results: 'Natijalar', live: 'Live dars',
    courses: 'Kurslar', liveCourses: 'Dars yozuvlari', practice: 'Test ishlash', questions: 'Savollar',
    logout: 'Chiqish', openMenu: 'Menyuni ochish', liveOn: 'Live dars boshlandi', joinLive: 'Darsga kirish',
    brandSub: 'Online ta’lim platformasi',
  },
  ru: {
    home: 'Главная', admin: 'Админ панель', students: 'Ученики', teachers: 'Учителя', info: 'Отчёты',
    teacher: 'Панель учителя', createCourse: 'Создать курс', tests: 'Тесты', results: 'Результаты', live: 'Live урок',
    courses: 'Курсы', liveCourses: 'Записи уроков', practice: 'Пройти тест', questions: 'Вопросы',
    logout: 'Выйти', openMenu: 'Открыть меню', liveOn: 'Live урок начался', joinLive: 'Войти на урок',
    brandSub: 'Платформа онлайн-обучения',
  },
}
const langOptions = [
  { code: 'uz', label: 'O‘zbek' },
  { code: 'ru', label: 'Русский' },
]
function t(key) { return translations[lang.value]?.[key] || translations.uz[key] || key }
const currentLang = computed(() => langOptions.find(item => item.code === lang.value) || langOptions[0])
const isAdmin = computed(() => role.value === 'admin')
const isTeacher = computed(() => role.value === 'teacher' || role.value === 'admin')
const showSidebar = computed(() => Boolean(role.value) && route.name !== 'student-auth')
const displayName = computed(() => {
  if (role.value === 'admin') return lang.value === 'ru' ? 'Администратор' : 'Admin'
  if (role.value === 'teacher') return teacher.value?.full_name || teacher.value?.username || t('teacher')
  return `${student.value?.first_name || ''} ${student.value?.last_name || ''}`.trim() || student.value?.username || ''
})

function langStorageKey(currentRole = role.value) {
  if (currentRole === 'admin') return 'edulive_lang_admin'
  if (currentRole === 'teacher') return 'edulive_lang_teacher'
  if (currentRole === 'student') return 'edulive_lang_student'
  return 'edulive_lang_auth'
}
function loadRoleLang(currentRole = role.value) {
  const saved = localStorage.getItem(langStorageKey(currentRole)) || 'uz'
  lang.value = ['uz', 'ru'].includes(saved) ? saved : 'uz'
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: lang.value }))
}
function setLang(next) {
  lang.value = next
  localStorage.setItem(langStorageKey(), next)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: next }))
}
function closeMenus() {
  mobileMenuOpen.value = false
  langMenuOpen.value = false
}
function handleDocumentClick(event) {
  if (!event.target.closest('.lang-picker')) langMenuOpen.value = false
}

function applySession(data = {}) {
  role.value = data.role || null
  student.value = data.student || null
  teacher.value = data.teacher || null
  loadRoleLang(role.value)
}
function handleSessionChange(event) {
  applySession(event.detail || {})
}
async function loadSession() {
  const saved = hydrateSession()
  if (saved?.role) applySession(saved)
  else loadRoleLang(null)

  try {
    const { data } = await api.get('/access/session')
    if (data?.role) {
      saveSession(data)
      applySession(data)
    } else if (!saved?.role) {
      clearSession()
      applySession({})
    }
  } catch {
    if (!saved?.role) applySession({})
  }
}
async function loadActiveLive() {
  if (role.value !== 'student') {
    activeLive.value = null
    return
  }
  try {
    const { data } = await api.get('/live/active')
    activeLive.value = data.class || null
  } catch {
    activeLive.value = null
  }
}
function ensureStudentSocket() {
  if (role.value !== 'student') {
    socket?.disconnect()
    socket = null
    return
  }
  if (socket) return
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('connect', () => {
    if (student.value) socket.emit('student-online', { student: student.value })
  })
  socket.on('live-status-changed', ({ class: klass, is_live }) => {
    activeLive.value = is_live ? klass : null
  })
}
function logout() {
  api.post('/student/logout').catch(() => {})
  clearSession()
  applySession({})
  activeLive.value = null
  closeMenus()
  router.replace('/auth')
}

onMounted(() => {
  window.addEventListener('edulive-session-change', handleSessionChange)
  document.addEventListener('click', handleDocumentClick)
  loadSession()
})
onBeforeUnmount(() => {
  socket?.disconnect()
  window.removeEventListener('edulive-session-change', handleSessionChange)
  document.removeEventListener('click', handleDocumentClick)
})
watch(role, () => {
  document.body.dataset.eduliveRole = role.value || 'auth'
  loadRoleLang(role.value)
  ensureStudentSocket()
  loadActiveLive()
}, { immediate: true })
watch(() => route.fullPath, closeMenus)
watch(student, () => {
  if (socket?.connected && student.value) socket.emit('student-online', { student: student.value })
})
</script>

<template>
  <div :class="showSidebar ? 'app-shell layout-shell simple-layout' : 'app-shell auth-shell'">
    <div v-if="showSidebar" class="mobile-menu-overlay" :class="{ show: mobileMenuOpen }" @click="mobileMenuOpen = false"></div>

    <aside v-if="showSidebar" class="sidebar simple-sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <div class="sidebar-main">
        <div class="simple-brand">
          <strong>EduLive Pro</strong>
          <small>{{ t('brandSub') }}</small>
        </div>

        <div class="lang-picker sidebar-lang">
          <button class="lang-toggle simple-lang-toggle" type="button" @click="langMenuOpen = !langMenuOpen">
            <span>{{ currentLang.label }}</span><span>⌄</span>
          </button>
          <div v-if="langMenuOpen" class="lang-menu simple-lang-menu">
            <button v-for="item in langOptions" :key="item.code" class="lang-option simple-lang-option" :class="{ active: item.code === lang }" type="button" @click="setLang(item.code)">{{ item.label }}</button>
          </div>
        </div>

        <nav class="sidebar-nav simple-sidebar-nav">
          <RouterLink class="side-link" to="/home"><span>{{ t('home') }}</span></RouterLink>

          <template v-if="isTeacher">
            <RouterLink v-if="isAdmin" class="side-link" to="/admin"><span>{{ t('admin') }}</span></RouterLink>
            <RouterLink class="side-link" to="/students"><span>{{ t('students') }}</span></RouterLink>
            <RouterLink v-if="isAdmin" class="side-link" to="/admin/teachers"><span>{{ t('teachers') }}</span></RouterLink>
            <RouterLink v-if="isAdmin" class="side-link" to="/admin/info"><span>{{ t('info') }}</span></RouterLink>
            <RouterLink class="side-link" to="/teacher"><span>{{ t('teacher') }}</span></RouterLink>
            <RouterLink class="side-link" to="/teacher/courses"><span>{{ t('createCourse') }}</span></RouterLink>
            <RouterLink class="side-link" to="/teacher/tests"><span>{{ t('tests') }}</span></RouterLink>
            <RouterLink class="side-link" to="/results-board"><span>{{ t('results') }}</span></RouterLink>
            <RouterLink class="side-link" to="/live"><span>{{ t('live') }}</span></RouterLink>
          </template>

          <template v-else>
            <RouterLink class="side-link" to="/courses"><span>{{ t('courses') }}</span></RouterLink>
            <RouterLink class="side-link" to="/live-courses"><span>{{ t('liveCourses') }}</span></RouterLink>
            <RouterLink class="side-link" to="/practice-tests"><span>{{ t('practice') }}</span></RouterLink>
            <RouterLink class="side-link" to="/questions"><span>{{ t('questions') }}</span></RouterLink>
          </template>
        </nav>
      </div>

      <div class="sidebar-footer simple-sidebar-footer">
        <div class="current-user">{{ displayName }}</div>
        <button class="btn btn-light logout-button" type="button" @click="logout">{{ t('logout') }}</button>
      </div>
    </aside>

    <main class="main-shell">
      <header v-if="showSidebar" class="mobile-top simple-mobile-top">
        <button class="mobile-menu-btn" type="button" @click="mobileMenuOpen = true" :aria-label="t('openMenu')">
          <span></span><span></span><span></span>
        </button>
        <strong>EduLive Pro</strong>
        <button class="mobile-logout-simple" type="button" @click="logout">{{ t('logout') }}</button>
      </header>

      <div :class="showSidebar ? 'container page page-with-sidebar' : 'page-auth-only'">
        <div v-if="activeLive && role === 'student'" class="live-global-alert simple-live-alert">
          <strong>{{ t('liveOn') }}</strong>
          <RouterLink class="btn btn-sm" :to="`/room/${activeLive.room_code}`">{{ t('joinLive') }}</RouterLink>
        </div>
        <RouterView />
      </div>
    </main>
  </div>
</template>
