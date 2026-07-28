<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../lib'

const route = useRoute()
const router = useRouter()
const slug = computed(() => route.params.slug)
const course = ref(null)
const linkedClass = ref(null)
const latestTest = ref(null)
const student = ref(null)
const unlockForm = reactive({ purchase_password: '' })
const telegramLink = 'https://t.me/mominov9969'
const message = ref('')
const error = ref('')
const firstLesson = computed(() => (course.value?.lessons || [])[0] || null)
const hasSavedVideo = computed(() => Boolean(course.value?.is_unlocked && firstLesson.value?.video_url))

async function load() {
  try {
    const sessionRes = await api.get('/student/session')
    student.value = sessionRes.data.student
  } catch {
    student.value = null
    router.replace('/auth')
    return
  }
  try {
    const { data } = await api.get(`/courses/${slug.value}`)
    course.value = data.course
    linkedClass.value = data.class
    latestTest.value = data.latest_test
  } catch {
    router.push('/')
  }
}

async function unlockCourse() {
  error.value = ''
  message.value = ''
  try {
    const { data } = await api.post(`/courses/${slug.value}/unlock`, unlockForm)
    course.value = data.course
    message.value = data.message
    unlockForm.purchase_password = ''
  } catch (err) {
    if (err.response?.status === 401 && !student.value) {
      router.push('/auth')
      return
    }
    error.value = err.response?.data?.error || 'Kurs ochilmadi.'
  }
}

onMounted(load)
</script>

<template>
  <div v-if="course" class="stack section">
    <section class="card glass course-hero-detail">
      <div class="badge">{{ course.track.toUpperCase() }} · {{ course.technology }}</div>
      <h1>{{ course.title }}</h1>
      <p class="lead">{{ course.description }}</p>
      <div class="info-grid">
        <div class="mini-card"><strong>Davomiyligi</strong><br>{{ course.duration }}</div>
        <div class="mini-card"><strong>Bosqich</strong><br>{{ course.level }}</div>
        <div class="mini-card"><strong>Narxi</strong><br>{{ Number(course.price).toLocaleString() }} so‘m</div>
      </div>

      <div v-if="course.is_unlocked" class="flash success">
        Kurs ochilgan. Video darsliklar, live dars va testlar endi sizga ochiq.
      </div>
      <div v-else class="lock-panel">
        <div class="lock-icon big">🔒</div>
        <div>
          <strong>Sotib olish bilan ochiladi</strong>
          <p class="muted">Kirish ma’lumoti ko‘rinmaydi. Uni Telegram orqali olib, shu yerga o‘zingiz kiriting.</p>
        </div>
        <a class="btn btn-secondary" :href="telegramLink" target="_blank" rel="noreferrer">@mominov9969 dan kirish ma’lumoti olish</a>
        <input v-model="unlockForm.purchase_password" type="password" autocomplete="off" placeholder="Kirish paroli" />
        <button class="btn" @click="unlockCourse">Kursni ochish</button>
      </div>

      <div class="row gap-sm wrap">
        <RouterLink v-if="course.is_unlocked && linkedClass && linkedClass.is_live" class="btn btn-secondary" :to="`/room/${linkedClass.room_code}?student_name=${encodeURIComponent(student ? `${student.first_name} ${student.last_name}` : 'Guest')}`">Online darsga qo‘shilish</RouterLink>
        <RouterLink v-if="course.is_unlocked && latestTest" class="btn" :to="`/test/${latestTest.id}?student_name=${encodeURIComponent(student ? `${student.first_name} ${student.last_name}` : 'Guest')}`">Test ishlash</RouterLink>
        <RouterLink v-if="hasSavedVideo" class="btn btn-warning" :to="`/course/${course.slug}/lesson/${firstLesson.id}`">Live yozuvni ko‘rish</RouterLink>
      </div>

      <div v-if="linkedClass?.is_live" class="flash success">Online dars hozir yoqilgan. {{ linkedClass.participants_count || 0 }} ta o‘quvchi online. Kurs ochilgandan keyin shu yerdan live darsga qo‘shilasiz.</div>

      <div class="feature-grid">
        <div class="mini-card"><strong>🎥 Online live</strong><br>Ustoz ekranini va ovozini jonli ko‘rasiz.</div>
        <div class="mini-card"><strong>🔐 Himoyalangan video</strong><br>Video darsliklarda oldinga o‘tkazish cheklangan.</div>
        <div class="mini-card"><strong>👀 Ustoz nazorati</strong><br>Ustoz kim kirganini ko‘rib turadi.</div>
      </div>

      <div v-if="message" class="flash success">{{ message }}</div>
      <div v-if="error" class="flash error">{{ error }}</div>
    </section>

    <section class="card glass">
      <div class="video-top">
        <div>
          <h2>Video darsliklar</h2>
          <p class="muted">Ustoz xohlagan payt admin paneldan yangi darslik qo‘sha oladi. Live saqlangan bo‘lsa, shu yerda videoni ko‘rasiz.</p>
        </div>
        <span class="pill">{{ course.lesson_count || course.lessons?.length || 0 }} ta dars</span>
      </div>

      <div class="lesson-list">
        <div v-for="lesson in (course.lessons || [])" :key="lesson.id" class="lesson-card">
          <div>
            <div class="badge">{{ lesson.order_no }}-dars</div>
            <h3>{{ lesson.title }}</h3>
            <p class="muted">{{ lesson.summary || 'Video darslik tayyor.' }}</p>
          </div>
          <RouterLink
            v-if="course.is_unlocked || lesson.is_preview"
            class="btn btn-sm"
            :to="`/course/${course.slug}/lesson/${lesson.id}`"
          >Ko‘rish</RouterLink>
          <button v-else class="btn btn-sm btn-ghost" disabled>Quluflangan</button>
        </div>
        <div v-if="!course.lessons?.length" class="flash error">Hali video darslik qo‘shilmagan.</div>
      </div>
    </section>
  </div>
</template>
