<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../lib'
import { hydrateSession } from '../sessionStore'
import CourseCard from '../components/CourseCard.vue'

const props = defineProps({ section: { type: String, default: 'home' } })
const session = ref(hydrateSession() || {})
const courses = ref([])
const coursesLoaded = ref(false)
const loading = ref(false)
const error = ref('')
const lang = ref('uz')

const text = {
  uz: {
    studentTitle: 'O‘quvchi paneli', studentSub: 'Kerakli bo‘limni tanlang va o‘qishni davom ettiring.',
    teacherTitle: 'Ustoz paneli', teacherSub: 'Kurs, test, natija va live darslarni shu yerdan boshqaring.',
    adminTitle: 'Admin bosh sahifasi', adminSub: 'O‘quvchilar, ustozlar va hisobotlarni boshqaring.',
    courses: 'Kurslar', coursesSub: 'Sizga ochilgan kursga kirib darslarni ko‘ring.',
    tests: 'Test ishlash', recordings: 'Dars yozuvlari', questions: 'Savollar', students: 'O‘quvchilar', teachers: 'Ustozlar', reports: 'Hisobotlar',
    createCourse: 'Kurs yaratish', addTests: 'Test qo‘shish', results: 'Natijalar', live: 'Live dars',
    noCourses: 'Hozircha kurs topilmadi.', loadError: 'Kurslar yuklanmadi.'
  },
  ru: {
    studentTitle: 'Панель ученика', studentSub: 'Выберите нужный раздел и продолжайте обучение.',
    teacherTitle: 'Панель учителя', teacherSub: 'Управляйте курсами, тестами, результатами и live-уроками.',
    adminTitle: 'Главная администратора', adminSub: 'Управляйте учениками, учителями и отчётами.',
    courses: 'Курсы', coursesSub: 'Откройте назначенный вам курс и смотрите уроки.',
    tests: 'Пройти тест', recordings: 'Записи уроков', questions: 'Вопросы', students: 'Ученики', teachers: 'Учителя', reports: 'Отчёты',
    createCourse: 'Создать курс', addTests: 'Добавить тест', results: 'Результаты', live: 'Live урок',
    noCourses: 'Курсы пока не найдены.', loadError: 'Курсы не загрузились.'
  }
}
function tr(key) { return text[lang.value]?.[key] || text.uz[key] || key }
const role = computed(() => session.value?.role || '')
const isAdmin = computed(() => role.value === 'admin')
const isTeacher = computed(() => role.value === 'teacher' || role.value === 'admin')
const pageTitle = computed(() => isAdmin.value ? tr('adminTitle') : (isTeacher.value ? tr('teacherTitle') : tr('studentTitle')))
const pageSubtitle = computed(() => isAdmin.value ? tr('adminSub') : (isTeacher.value ? tr('teacherSub') : tr('studentSub')))

function syncLang(next) {
  const key = role.value === 'admin' ? 'edulive_lang_admin' : role.value === 'teacher' ? 'edulive_lang_teacher' : role.value === 'student' ? 'edulive_lang_student' : 'edulive_lang_auth'
  lang.value = ['uz', 'ru'].includes(next) ? next : (localStorage.getItem(key) || 'uz')
}
function handleSession(event) { session.value = event.detail || {}; syncLang() }
function handleLang(event) { syncLang(event.detail) }
async function loadCourses() {
  if (coursesLoaded.value || props.section !== 'courses') return
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/courses')
    courses.value = data.courses || []
    coursesLoaded.value = true
  } catch {
    error.value = tr('loadError')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  syncLang()
  window.addEventListener('edulive-session-change', handleSession)
  window.addEventListener('edulive-lang-change', handleLang)
  loadCourses()
})
onBeforeUnmount(() => {
  window.removeEventListener('edulive-session-change', handleSession)
  window.removeEventListener('edulive-lang-change', handleLang)
})
watch(() => props.section, loadCourses)
</script>

<template>
  <section v-if="section === 'home' || section === 'teacher'" class="section simple-home-page">
    <div class="simple-page-head">
      <h1>{{ pageTitle }}</h1>
      <p class="muted">{{ pageSubtitle }}</p>
    </div>

    <div v-if="isAdmin" class="simple-menu-grid">
      <RouterLink class="simple-menu-card" to="/students"><strong>{{ tr('students') }}</strong><span>{{ tr('students') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/admin/teachers"><strong>{{ tr('teachers') }}</strong><span>{{ tr('teachers') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/admin/info"><strong>{{ tr('reports') }}</strong><span>{{ tr('reports') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/teacher/courses"><strong>{{ tr('createCourse') }}</strong><span>{{ tr('createCourse') }}</span></RouterLink>
    </div>

    <div v-else-if="isTeacher" class="simple-menu-grid">
      <RouterLink class="simple-menu-card" to="/students"><strong>{{ tr('students') }}</strong><span>{{ tr('students') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/teacher/courses"><strong>{{ tr('createCourse') }}</strong><span>{{ tr('createCourse') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/teacher/tests"><strong>{{ tr('addTests') }}</strong><span>{{ tr('addTests') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/results-board"><strong>{{ tr('results') }}</strong><span>{{ tr('results') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/live"><strong>{{ tr('live') }}</strong><span>{{ tr('live') }}</span></RouterLink>
    </div>

    <div v-else class="simple-menu-grid">
      <RouterLink class="simple-menu-card" to="/courses"><strong>{{ tr('courses') }}</strong><span>{{ tr('coursesSub') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/practice-tests"><strong>{{ tr('tests') }}</strong><span>{{ tr('tests') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/live-courses"><strong>{{ tr('recordings') }}</strong><span>{{ tr('recordings') }}</span></RouterLink>
      <RouterLink class="simple-menu-card" to="/questions"><strong>{{ tr('questions') }}</strong><span>{{ tr('questions') }}</span></RouterLink>
    </div>
  </section>

  <section v-else-if="section === 'courses'" class="section simple-courses-page">
    <div class="simple-page-head">
      <h1>{{ tr('courses') }}</h1>
      <p class="muted">{{ tr('coursesSub') }}</p>
    </div>
    <div v-if="loading" class="card simple-card">...</div>
    <div v-else-if="error" class="flash error">{{ error }}</div>
    <div v-else-if="courses.length" class="class-grid simple-course-grid">
      <CourseCard v-for="course in courses" :key="course.id" :course="course" />
    </div>
    <div v-else class="card simple-card muted">{{ tr('noCourses') }}</div>
  </section>
</template>
