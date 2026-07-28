<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { api, socketURL } from './lib'
import { saveSession, clearSession, hydrateSession } from './sessionStore'
import { io } from 'socket.io-client'

const student = ref(null)
const teacher = ref(null)
const role = ref(null)
const telegramLink = 'https://t.me/mominov9969'
const activeLive = ref(null)
const mobileMenuOpen = ref(false)
const langMenuOpen = ref(false)
let socket
const route = useRoute()

const lang = ref('uz')
const translations = {
  uz: {
    brandSub:'Online kurs platforma',
    home:'Home', homeSub:'Bosh sahifa', admin:'Admin qismi', adminSub:'Barcha nazorat', teacher:'Ustoz bo‘limi', teacherSub:'Kurs, live va testlar',
    createTeacher:'Ustoz yaratish', createTeacherSub:'Yangi ustoz login', info:'Ma’lumot', infoSub:'Sayt statistikasi', courses:'Kurslar', coursesSub:'Barcha pullik kurslar',
    createCourse:'Kurs yaratish', createCourseSub:'Yangi pullik kurs', tests:'Test qo‘shish', testsSub:'Frontend va backend', results:'Natijalar', resultsSub:'Foiz va yechimlar',
    live:'Live dars', liveSub:'Ekran yozish va dars o‘tish', liveCourses:'Live darslar', liveCoursesSub:'Video yozuv kurslari', practice:'Test yechish', practiceSub:'O‘quvchi testi',
    questions:'Savollar', questionsSub:'AI yordamchi', telegram:'Telegram', logout:'Chiqish', openMenu:'Menyuni ochish', liveOn:'Live dars yoqildi', liveInfo:'Ustoz hozir jonli dars o‘tyapti. Qo‘shilish tugmasi faqat live yoqilganda chiqadi.', joinLive:'Live darsga qo‘shilish'
  },
  ru: {
    brandSub:'Онлайн-платформа курсов',
    home:'Главная', homeSub:'Главная страница', admin:'Админ', adminSub:'Контроль', teacher:'Учитель', teacherSub:'Курсы, live и тесты',
    createTeacher:'Создать учителя', createTeacherSub:'Новый логин', info:'Информация', infoSub:'Статистика сайта', courses:'Курсы', coursesSub:'Все платные курсы',
    createCourse:'Создать курс', createCourseSub:'Новый платный курс', tests:'Добавить тест', testsSub:'Frontend и backend', results:'Результаты', resultsSub:'Проценты и ответы',
    live:'Live урок', liveSub:'Запись экрана', liveCourses:'Live курсы', liveCoursesSub:'Видео-записи', practice:'Решать тест', practiceSub:'Тест ученика',
    questions:'Вопросы', questionsSub:'AI помощник', telegram:'Telegram', logout:'Выход', openMenu:'Открыть меню', liveOn:'Live урок включен', liveInfo:'Учитель проводит онлайн урок. Кнопка подключения появляется только при live.', joinLive:'Подключиться'
  },
  en: {
    brandSub:'Online course platform',
    home:'Home', homeSub:'Dashboard', admin:'Admin', adminSub:'Control center', teacher:'Teacher', teacherSub:'Courses, live, tests',
    createTeacher:'Create teacher', createTeacherSub:'New teacher login', info:'Info', infoSub:'Site analytics', courses:'Courses', coursesSub:'All paid courses',
    createCourse:'Create course', createCourseSub:'New paid course', tests:'Add tests', testsSub:'Frontend and backend', results:'Results', resultsSub:'Scores and answers',
    live:'Live class', liveSub:'Screen recording', liveCourses:'Live courses', liveCoursesSub:'Recorded videos', practice:'Practice tests', practiceSub:'Student tests',
    questions:'Questions', questionsSub:'AI assistant', telegram:'Telegram', logout:'Logout', openMenu:'Open menu', liveOn:'Live class is on', liveInfo:'Teacher is teaching live now. Join button appears only when live is enabled.', joinLive:'Join live'
  }
}
function t(key){ return translations[lang.value]?.[key] || translations.uz[key] || key }
const langOptions = [
  { code: 'uz', label: 'Uzbekcha', short: 'UZ', flag: '🇺🇿' },
  { code: 'ru', label: 'Русский', short: 'RU', flag: '🇷🇺' },
  { code: 'en', label: 'English', short: 'EN', flag: '🇬🇧' },
]
const currentLangOption = computed(() => langOptions.find(item => item.code === lang.value) || langOptions[0])
function langStorageKey(currentRole = role.value){
  if (currentRole === 'admin') return 'edulive_lang_admin'
  if (currentRole === 'teacher') return 'edulive_lang_teacher'
  if (currentRole === 'student') return 'edulive_lang_student'
  return 'edulive_lang_auth'
}
function loadRoleLang(currentRole = role.value){
  const saved = localStorage.getItem(langStorageKey(currentRole)) || 'uz'
  lang.value = ['uz','ru','en'].includes(saved) ? saved : 'uz'
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: lang.value }))
}
function setLang(next){
  lang.value = next
  localStorage.setItem(langStorageKey(), lang.value)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: lang.value }))
}
function cycleLang(){
  langMenuOpen.value = !langMenuOpen.value
}
function cycleNextLang(){
  const index = langOptions.findIndex(item => item.code === lang.value)
  const next = langOptions[(index + 1) % langOptions.length]
  setLang(next.code)
}
function closeLangMenu(){
  langMenuOpen.value = false
}


async function loadSession() {
  const saved = hydrateSession()
  if (saved?.role) {
    student.value = saved.student || null
    teacher.value = saved.teacher || null
    role.value = saved.role || null
    loadRoleLang(role.value)
  } else {
    loadRoleLang(null)
  }
  try {
    const { data } = await api.get('/access/session')
    student.value = data.student || null
    teacher.value = data.teacher || null
    role.value = data.role || null
    saveSession(data)
    loadRoleLang(role.value)
    if (role.value === 'student') {
      try {
        const liveRes = await api.get('/live/active')
        activeLive.value = liveRes.data.class || null
      } catch { activeLive.value = null }
    } else {
      activeLive.value = null
    }
    notifyStudentOnline()
  } catch {
    if (!saved?.role) {
      clearSession()
      student.value = null
      teacher.value = null
      role.value = null
      activeLive.value = null
    }
  }
}

function connectLiveSocket() {
  if (socket) return
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('connect', notifyStudentOnline)
  socket.on('live-status-changed', ({ class: klass, is_live }) => {
    if (role.value === 'student') activeLive.value = is_live ? klass : null
  })
}

function notifyStudentOnline() {
  if (socket?.connected && role.value === 'student' && student.value) {
    socket.emit('student-online', { student: student.value })
  }
}

async function logout() {
  await api.post('/student/logout').catch(() => {})
  clearSession()
  student.value = null
  teacher.value = null
  role.value = null
  loadRoleLang(null)
  window.location.href = '/auth'
}

const showSidebar = computed(() => !!role.value && route.name !== 'student-auth' && route.name !== 'admin-login')
const isAdmin = computed(() => role.value === 'admin')
const isTeacher = computed(() => role.value === 'teacher' || role.value === 'admin')
const displayName = computed(() => {
  if (isAdmin.value) return 'Bosh ustoz'
  if (role.value === 'teacher') return teacher.value?.full_name || teacher.value?.username || 'Ustoz'
  return ((student.value?.first_name || '') + ' ' + (student.value?.last_name || '')).trim()
})

onMounted(() => { loadSession(); connectLiveSocket() })
onBeforeUnmount(() => socket?.disconnect())
watch(() => route.fullPath, async () => {
  mobileMenuOpen.value = false
  await loadSession()
}, { immediate: false })
watch(role, (newRole) => {
  document.body.dataset.eduliveRole = newRole || 'auth'
  loadRoleLang(newRole)
}, { immediate: true })
watch([role, student], notifyStudentOnline)
</script>

<template>
  <div :class="showSidebar ? 'app-shell layout-shell' : 'app-shell auth-shell'">

    <div v-if="showSidebar" class="mobile-menu-overlay" :class="{ show: mobileMenuOpen }" @click="mobileMenuOpen = false"></div>

    <aside v-if="showSidebar" class="sidebar glass compact-sidebar clean-sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <div>
        <div class="logo-wrap compact-logo-wrap premium-logo-wrap">
          <div class="logo-mark static-logo-mark">▰</div>
          <div>
            <div class="brand-title">EduLive Pro</div>
            <div class="brand-sub">{{ t('brandSub') }}</div>
          </div>
        </div>
        <div class="lang-picker sidebar-lang">
          <button class="lang-toggle lang-sticker flag-style-toggle" type="button" @click="cycleLang" @dblclick.stop.prevent="cycleNextLang">
            <span class="selected-lang">{{ currentLangOption.short }}</span>
            <span class="lang-arrow">⌄</span>
          </button>
          <div v-if="langMenuOpen" class="lang-menu glass">
            <button v-for="item in langOptions" :key="item.code" type="button" class="lang-option" :class="{active:item.code===lang}" @click="setLang(item.code)">
              <span>{{ item.flag }}</span><strong>{{ item.short }}</strong><small>{{ item.label }}</small>
            </button>
          </div>
        </div>

        <nav class="sidebar-nav compact-sidebar-nav cleaner-nav">
          <RouterLink class="side-link" to="/home">
            <span class="side-icon">🏠</span>
            <span><strong>{{ t('home') }}</strong><small>{{ t('homeSub') }}</small></span>
          </RouterLink>

          <template v-if="isTeacher">
            <RouterLink v-if="isAdmin" class="side-link" to="/admin">
              <span class="side-icon">🛡️</span>
              <span><strong>{{ t('admin') }}</strong><small>{{ t('adminSub') }}</small></span>
            </RouterLink>
            <RouterLink v-if="isAdmin" class="side-link" to="/admin/teachers">
              <span class="side-icon">👤</span>
              <span><strong>{{ t('createTeacher') }}</strong><small>{{ t('createTeacherSub') }}</small></span>
            </RouterLink>
            <RouterLink v-if="isAdmin" class="side-link" to="/admin/info">
              <span class="side-icon">📊</span>
              <span><strong>{{ t('info') }}</strong><small>{{ t('infoSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/teacher">
              <span class="side-icon">👨‍🏫</span>
              <span><strong>{{ t('teacher') }}</strong><small>{{ t('teacherSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/teacher/courses">
              <span class="side-icon">📚</span>
              <span><strong>{{ t('createCourse') }}</strong><small>{{ t('createCourseSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/teacher/tests">
              <span class="side-icon">📝</span>
              <span><strong>{{ t('tests') }}</strong><small>{{ t('testsSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/results-board">
              <span class="side-icon">📈</span>
              <span><strong>{{ t('results') }}</strong><small>{{ t('resultsSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/live">
              <span class="side-icon">🔴</span>
              <span><strong>{{ t('live') }}</strong><small>{{ t('liveSub') }}</small></span>
            </RouterLink>
          </template>

          <template v-else>
            <RouterLink class="side-link" to="/courses">
              <span class="side-icon">📚</span>
              <span><strong>{{ t('courses') }}</strong><small>{{ t('coursesSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/live-courses">
              <span class="side-icon">🎥</span>
              <span><strong>{{ t('liveCourses') }}</strong><small>{{ t('liveCoursesSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/practice-tests">
              <span class="side-icon">🧪</span>
              <span><strong>{{ t('practice') }}</strong><small>{{ t('practiceSub') }}</small></span>
            </RouterLink>
            <RouterLink class="side-link" to="/questions">
              <span class="side-icon">💬</span>
              <span><strong>{{ t('questions') }}</strong><small>{{ t('questionsSub') }}</small></span>
            </RouterLink>
          </template>

          <a class="side-link" :href="telegramLink" target="_blank" rel="noreferrer">
            <span class="side-icon">✈️</span>
            <span><strong>{{ t('telegram') }}</strong><small>@mominov9969</small></span>
          </a>
        </nav>
      </div>

      <div class="sidebar-footer compact-sidebar-footer">
        <div class="student-chip small-chip">{{ displayName }}</div>
        <button class="btn btn-sm btn-secondary" @click="logout">{{ t('logout') }}</button>
      </div>
    </aside>

    <main class="main-shell">
      <header v-if="showSidebar" class="mobile-top glass">
        <button class="mobile-menu-btn" type="button" @click="mobileMenuOpen = true"  :aria-label="t('openMenu')">
          <span></span><span></span><span></span>
        </button>
        <div class="mobile-brand-block">
          <div class="brand-title">EduLive Pro</div>
          <div class="student-chip small-chip mobile-chip">{{ displayName }}</div>
        </div>
        <div class="lang-picker mobile-lang">
          <button class="lang-toggle lang-sticker flag-style-toggle" type="button" @click="cycleLang" @dblclick.stop.prevent="cycleNextLang">
            <span class="selected-lang">{{ currentLangOption.short }}</span>
            <span class="lang-arrow">⌄</span>
          </button>
          <div v-if="langMenuOpen" class="lang-menu glass mobile-lang-menu">
            <button v-for="item in langOptions" :key="item.code" type="button" class="lang-option" :class="{active:item.code===lang}" @click="setLang(item.code)">
              <span>{{ item.flag }}</span><strong>{{ item.short }}</strong><small>{{ item.label }}</small>
            </button>
          </div>
        </div>
        <button class="btn btn-sm btn-secondary mobile-logout" @click="logout">{{ t('logout') }}</button>
      </header>
      <div :class="showSidebar ? 'container page page-with-sidebar' : 'container page page-auth-only'">
        <div v-if="activeLive && !isTeacher" class="card glass live-global-alert">
          <div><strong>🔴 {{ t('liveOn') }}</strong><p class="muted">{{ t('liveInfo') }}</p></div>
          <RouterLink class="btn btn-warning" :to="`/room/${activeLive.room_code}`">{{ t('joinLive') }}</RouterLink>
        </div>
        <RouterView v-slot="{ Component }">
          <component :is="Component" :key="route.fullPath" />
        </RouterView>
      </div>
    </main>
  </div>
</template>
