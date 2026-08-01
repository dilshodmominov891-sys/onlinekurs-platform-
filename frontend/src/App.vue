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
const theme = ref(localStorage.getItem('edulive_theme') || 'light')
let socket = null

const translations = {
  uz: {
    home: 'Bosh sahifa', homeSub: 'Asosiy ma’lumot va tezkor yo‘llar',
    admin: 'Admin panel', adminSub: 'Umumiy nazorat va statistika',
    students: 'O‘quvchilar', studentsSub: 'Login, parol va kurslarni boshqarish',
    teachers: 'Ustozlar', teachersSub: 'Ustoz yaratish va nazorat qilish',
    info: 'Hisobotlar', infoSub: 'Kunlik, oylik va yillik Excel',
    teacher: 'Ustoz paneli', teacherSub: 'Ustoz uchun boshqaruv markazi',
    createCourse: 'Kurs yaratish', createCourseSub: 'Yangi kurs va darslar qo‘shish',
    tests: 'Testlar', testsSub: 'Test yaratish va Excel yuklash',
    results: 'Natijalar', resultsSub: 'O‘quvchi natijalarini ko‘rish',
    live: 'Live dars', liveSub: 'Jonli dars boshlash va yozib olish',
    courses: 'Kurslar', coursesSub: 'Biriktirilgan kurslarni ko‘rish',
    liveCourses: 'Dars yozuvlari', liveCoursesSub: 'Saqlangan video darslar',
    practice: 'Test ishlash', practiceSub: 'Mavjud testlarni yechish',
    questions: 'Savollar', questionsSub: 'AI yordamchidan javob olish',
    logout: 'Chiqish', openMenu: 'Menyuni ochish', liveOn: 'Live dars boshlandi', joinLive: 'Darsga kirish',
    brandSub: 'Online ta’lim platformasi',
  },
  ru: {
    home: 'Главная', homeSub: 'Основная информация и быстрые ссылки',
    admin: 'Админ панель', adminSub: 'Общий контроль и статистика',
    students: 'Ученики', studentsSub: 'Логины, пароли и доступ к курсам',
    teachers: 'Учителя', teachersSub: 'Создание и управление учителями',
    info: 'Отчёты', infoSub: 'Дневные, месячные и годовые Excel',
    teacher: 'Панель учителя', teacherSub: 'Центр управления учителя',
    createCourse: 'Создать курс', createCourseSub: 'Добавление курсов и уроков',
    tests: 'Тесты', testsSub: 'Создание тестов и загрузка Excel',
    results: 'Результаты', resultsSub: 'Просмотр результатов учеников',
    live: 'Live урок', liveSub: 'Запуск и запись онлайн-урока',
    courses: 'Курсы', coursesSub: 'Просмотр назначенных курсов',
    liveCourses: 'Записи уроков', liveCoursesSub: 'Сохранённые видеоуроки',
    practice: 'Пройти тест', practiceSub: 'Выполнение доступных тестов',
    questions: 'Вопросы', questionsSub: 'Получение ответа от AI помощника',
    logout: 'Выйти', openMenu: 'Открыть меню', liveOn: 'Live урок начался', joinLive: 'Войти на урок',
    brandSub: 'Платформа онлайн-обучения',
  },
}
const langOptions = [
  { code: 'uz', label: 'O‘zbek' },
  { code: 'ru', label: 'Русский' },
]
function t(key) { return translations[lang.value]?.[key] || translations.uz[key] || key }

function applyTheme(next) {
  const value = next === 'dark' ? 'dark' : 'light'
  theme.value = value
  localStorage.setItem('edulive_theme', value)
  document.documentElement.dataset.theme = value
}
function setTheme(next) { applyTheme(next) }

const currentLang = computed(() => langOptions.find(item => item.code === lang.value) || langOptions[0])
const isAdmin = computed(() => role.value === 'admin')
const isTeacher = computed(() => role.value === 'teacher' || role.value === 'admin')
const showSidebar = computed(() => Boolean(role.value) && route.name !== 'student-auth')
const displayName = computed(() => {
  if (role.value === 'admin') return lang.value === 'ru' ? 'Администратор' : 'Admin'
  if (role.value === 'teacher') return teacher.value?.full_name || teacher.value?.username || t('teacher')
  return `${student.value?.first_name || ''} ${student.value?.last_name || ''}`.trim() || student.value?.username || ''
})
const sectionMeta = computed(() => {
  const routeMap = {
    home: ['home', 'homeSub'],
    'admin-dashboard': ['admin', 'adminSub'],
    'admin-students': ['students', 'studentsSub'],
    'admin-teachers-create': ['teachers', 'teachersSub'],
    'admin-info': ['info', 'infoSub'],
    teacher: ['teacher', 'teacherSub'],
    'teacher-courses': ['createCourse', 'createCourseSub'],
    'teacher-tests': ['tests', 'testsSub'],
    'results-board': ['results', 'resultsSub'],
    live: ['live', 'liveSub'],
    courses: ['courses', 'coursesSub'],
    'live-courses': ['liveCourses', 'liveCoursesSub'],
    'practice-tests': ['practice', 'practiceSub'],
    questions: ['questions', 'questionsSub'],
  }
  const keys = routeMap[route.name] || ['home', 'homeSub']
  return { title: t(keys[0]), description: t(keys[1]) }
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
function handleSessionChange(event) { applySession(event.detail || {}) }
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
  applyTheme(theme.value)
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

        <nav class="sidebar-nav simple-sidebar-nav">
          <RouterLink class="side-link" to="/home"><span class="nav-copy"><strong>{{ t('home') }}</strong><small>{{ t('homeSub') }}</small></span></RouterLink>

          <template v-if="isTeacher">
            <RouterLink v-if="isAdmin" class="side-link" to="/admin"><span class="nav-copy"><strong>{{ t('admin') }}</strong><small>{{ t('adminSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/students"><span class="nav-copy"><strong>{{ t('students') }}</strong><small>{{ t('studentsSub') }}</small></span></RouterLink>
            <RouterLink v-if="isAdmin" class="side-link" to="/admin/teachers"><span class="nav-copy"><strong>{{ t('teachers') }}</strong><small>{{ t('teachersSub') }}</small></span></RouterLink>
            <RouterLink v-if="isAdmin" class="side-link" to="/admin/info"><span class="nav-copy"><strong>{{ t('info') }}</strong><small>{{ t('infoSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/teacher"><span class="nav-copy"><strong>{{ t('teacher') }}</strong><small>{{ t('teacherSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/teacher/courses"><span class="nav-copy"><strong>{{ t('createCourse') }}</strong><small>{{ t('createCourseSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/teacher/tests"><span class="nav-copy"><strong>{{ t('tests') }}</strong><small>{{ t('testsSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/results-board"><span class="nav-copy"><strong>{{ t('results') }}</strong><small>{{ t('resultsSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/live"><span class="nav-copy"><strong>{{ t('live') }}</strong><small>{{ t('liveSub') }}</small></span></RouterLink>
          </template>

          <template v-else>
            <RouterLink class="side-link" to="/courses"><span class="nav-copy"><strong>{{ t('courses') }}</strong><small>{{ t('coursesSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/live-courses"><span class="nav-copy"><strong>{{ t('liveCourses') }}</strong><small>{{ t('liveCoursesSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/practice-tests"><span class="nav-copy"><strong>{{ t('practice') }}</strong><small>{{ t('practiceSub') }}</small></span></RouterLink>
            <RouterLink class="side-link" to="/questions"><span class="nav-copy"><strong>{{ t('questions') }}</strong><small>{{ t('questionsSub') }}</small></span></RouterLink>
          </template>
        </nav>
      </div>

      <div class="sidebar-footer simple-sidebar-footer">
        <div class="current-user">{{ displayName }}</div>
        <button class="btn btn-light logout-button" type="button" @click="logout">{{ t('logout') }}</button>
      </div>
    </aside>

    <main :class="['main-shell', { 'questions-main-shell': route.name === 'questions' }]">
      <header v-if="showSidebar" class="mobile-top simple-mobile-top">
        <button class="mobile-menu-btn" type="button" @click="mobileMenuOpen = true" :aria-label="t('openMenu')">
          <span></span><span></span><span></span>
        </button>
        <div class="mobile-section-copy">
          <strong>{{ sectionMeta.title }}</strong>
          <small>{{ sectionMeta.description }}</small>
        </div>
        <div class="top-control-actions mobile-control-actions">
          <div class="lang-picker top-lang-picker">
            <button class="lang-toggle simple-lang-toggle compact-lang-toggle" type="button" @click="langMenuOpen = !langMenuOpen">
              <span>{{ currentLang.label }}</span><span class="simple-lang-chevron" aria-hidden="true"></span>
            </button>
            <div v-if="langMenuOpen" class="lang-menu simple-lang-menu top-lang-menu">
              <button v-for="item in langOptions" :key="item.code" class="lang-option simple-lang-option" :class="{ active: item.code === lang }" type="button" @click="setLang(item.code)">{{ item.label }}</button>
            </div>
          </div>
          <div class="theme-switch" role="group" aria-label="Sayt mavzusi">
            <button class="theme-button" :class="{ active: theme === 'light' }" type="button" aria-label="Oq rang" title="Oq rang" @click="setTheme('light')">☀</button>
            <button class="theme-button" :class="{ active: theme === 'dark' }" type="button" aria-label="Tungi rang" title="Tungi rang" @click="setTheme('dark')">☾</button>
          </div>
        </div>
      </header>

      <header v-if="showSidebar" class="desktop-top-controls">
        <div class="desktop-section-context">
          <strong>{{ sectionMeta.title }}</strong>
          <small>{{ sectionMeta.description }}</small>
        </div>
        <div class="top-control-actions">
          <div class="lang-picker top-lang-picker">
            <button class="lang-toggle simple-lang-toggle compact-lang-toggle" type="button" @click="langMenuOpen = !langMenuOpen">
              <span>{{ currentLang.label }}</span><span class="simple-lang-chevron" aria-hidden="true"></span>
            </button>
            <div v-if="langMenuOpen" class="lang-menu simple-lang-menu top-lang-menu">
              <button v-for="item in langOptions" :key="item.code" class="lang-option simple-lang-option" :class="{ active: item.code === lang }" type="button" @click="setLang(item.code)">{{ item.label }}</button>
            </div>
          </div>
          <div class="theme-switch" role="group" aria-label="Sayt mavzusi">
            <button class="theme-button" :class="{ active: theme === 'light' }" type="button" aria-label="Oq rang" title="Oq rang" @click="setTheme('light')">☀</button>
            <button class="theme-button" :class="{ active: theme === 'dark' }" type="button" aria-label="Tungi rang" title="Tungi rang" @click="setTheme('dark')">☾</button>
          </div>
        </div>
      </header>

      <div :class="[showSidebar ? 'container page page-with-sidebar' : 'page-auth-only', { 'questions-page-shell': route.name === 'questions' }]">
        <div v-if="activeLive && role === 'student'" class="live-global-alert simple-live-alert">
          <strong>{{ t('liveOn') }}</strong>
          <RouterLink class="btn btn-sm" :to="`/room/${activeLive.room_code}`">{{ t('joinLive') }}</RouterLink>
        </div>
        <RouterView v-slot="{ Component }">
          <Transition name="route-fade" mode="out-in">
            <component :is="Component" :key="route.name" />
          </Transition>
        </RouterView>
      </div>
    </main>
  </div>
</template>
