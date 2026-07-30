<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../lib'

const route = useRoute()
const router = useRouter()
const course = ref(null)
const linkedClass = ref(null)
const latestTest = ref(null)
const student = ref(null)
const error = ref('')
const lang = ref(localStorage.getItem('edulive_lang_student') || 'uz')

const text = {
  uz: {
    duration: 'Davomiyligi', level: 'Bosqich', accessOpen: 'Kurs sizga ochilgan.', accessClosed: 'Bu kurs sizga hali ochilmagan.',
    accessHelp: 'Kursni admin o‘quvchi akkauntingizga biriktiradi.', live: 'Live darsga kirish', test: 'Test ishlash', recording: 'Dars yozuvini ko‘rish',
    lessons: 'Darslar', noLessons: 'Hali dars qo‘shilmagan.', view: 'Ko‘rish', locked: 'Yopiq'
  },
  ru: {
    duration: 'Продолжительность', level: 'Уровень', accessOpen: 'Курс открыт для вас.', accessClosed: 'Этот курс вам пока не открыт.',
    accessHelp: 'Администратор назначает курс вашему аккаунту.', live: 'Войти на live урок', test: 'Пройти тест', recording: 'Смотреть запись урока',
    lessons: 'Уроки', noLessons: 'Уроки ещё не добавлены.', view: 'Открыть', locked: 'Закрыто'
  }
}
function tr(key) { return text[lang.value]?.[key] || text.uz[key] || key }
const firstLesson = computed(() => course.value?.lessons?.[0] || null)
const hasSavedVideo = computed(() => Boolean(course.value?.is_unlocked && firstLesson.value?.video_url))
function handleLang(event) { lang.value = ['uz', 'ru'].includes(event.detail) ? event.detail : 'uz' }
async function load() {
  try {
    const sessionRes = await api.get('/student/session')
    student.value = sessionRes.data.student
    if (!student.value) {
      router.replace('/auth')
      return
    }
    const { data } = await api.get(`/courses/${route.params.slug}`)
    course.value = data.course
    linkedClass.value = data.class
    latestTest.value = data.latest_test
  } catch (err) {
    error.value = err.response?.data?.error || 'Kurs yuklanmadi.'
  }
}
onMounted(() => {
  window.addEventListener('edulive-lang-change', handleLang)
  load()
})
onBeforeUnmount(() => window.removeEventListener('edulive-lang-change', handleLang))
</script>

<template>
  <section v-if="course" class="section simple-course-detail">
    <div class="simple-page-head">
      <h1>{{ course.title }}</h1>
      <p class="muted">{{ course.description }}</p>
    </div>

    <div class="card simple-card course-summary-card">
      <div class="simple-info-row"><strong>{{ tr('duration') }}</strong><span>{{ course.duration || '—' }}</span></div>
      <div class="simple-info-row"><strong>{{ tr('level') }}</strong><span>{{ course.level || '—' }}</span></div>
    </div>

    <div v-if="course.is_unlocked" class="flash success">{{ tr('accessOpen') }}</div>
    <div v-else class="card simple-card locked-course-note">
      <strong>{{ tr('accessClosed') }}</strong>
      <p class="muted">{{ tr('accessHelp') }}</p>
    </div>

    <div v-if="course.is_unlocked" class="simple-action-grid section">
      <RouterLink v-if="linkedClass?.is_live" class="btn" :to="`/room/${linkedClass.room_code}`">{{ tr('live') }}</RouterLink>
      <RouterLink v-if="latestTest" class="btn btn-light" :to="`/test/${latestTest.id}`">{{ tr('test') }}</RouterLink>
      <RouterLink v-if="hasSavedVideo" class="btn btn-light" :to="`/course/${course.slug}/lesson/${firstLesson.id}`">{{ tr('recording') }}</RouterLink>
    </div>

    <div class="section card simple-card">
      <h2>{{ tr('lessons') }}</h2>
      <div class="simple-list">
        <div v-for="lesson in course.lessons || []" :key="lesson.id" class="simple-list-item lesson-simple-row">
          <div><strong>{{ lesson.order_no }}. {{ lesson.title }}</strong><p class="muted">{{ lesson.summary || '' }}</p></div>
          <RouterLink v-if="course.is_unlocked || lesson.is_preview" class="btn btn-sm" :to="`/course/${course.slug}/lesson/${lesson.id}`">{{ tr('view') }}</RouterLink>
          <span v-else class="plain-count">{{ tr('locked') }}</span>
        </div>
        <p v-if="!course.lessons?.length" class="muted">{{ tr('noLessons') }}</p>
      </div>
    </div>
  </section>
  <div v-if="error" class="flash error">{{ error }}</div>
</template>
