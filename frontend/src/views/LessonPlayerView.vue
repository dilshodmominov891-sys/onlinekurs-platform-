<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, resolveAssetUrl } from '../lib'

const route = useRoute()
const router = useRouter()
const slug = computed(() => route.params.slug)
const lessonId = computed(() => route.params.lessonId)
const course = ref(null)
const lesson = ref(null)
const error = ref('')
const videoRef = ref(null)
const maxWatched = ref(0)
const readyText = ref('Video yuklanmoqda...')
const videoLoadError = ref('')
const resolvedVideoUrl = computed(() => resolveAssetUrl(lesson.value?.video_url || ''))

async function load() {
  try {
    const { data } = await api.get(`/courses/${slug.value}/lessons/${lessonId.value}`)
    course.value = data.course
    lesson.value = data.lesson
    readyText.value = 'Video tayyor. Oldinga o‘tkazish cheklangan.'
  } catch (err) {
    error.value = err.response?.data?.error || 'Video darslik ochilmadi.'
  }
}

function onTimeUpdate() {
  const video = videoRef.value
  if (!video) return
  if (video.currentTime > maxWatched.value) {
    maxWatched.value = video.currentTime
  }
}

function onSeeking() {
  const video = videoRef.value
  if (!video) return
  if (video.currentTime > maxWatched.value + 0.6) {
    video.currentTime = maxWatched.value
  }
}

function onContextMenu(event) {
  event.preventDefault()
}

function onVideoError() {
  videoLoadError.value = 'Video link ishlamadi yoki yozuv hali yuklanmagan. Live tugagach Kursga saqlashni yana bosing.'
  readyText.value = 'Video ochilmadi.'
}

onMounted(load)
</script>

<template>
  <section v-if="lesson && course" class="stack section">
    <div class="card glass live-stage">
      <div class="video-top">
        <div>
          <div class="badge">{{ course.technology }}</div>
          <h1>{{ lesson.title }}</h1>
          <p>{{ lesson.summary }}</p>
        </div>
        <RouterLink class="btn btn-sm btn-secondary" :to="`/course/${course.slug}`">Kursga qaytish</RouterLink>
      </div>

      <video
        ref="videoRef"
        :src="resolvedVideoUrl"
        controls
        autoplay
        playsinline
        controlsList="nodownload noplaybackrate noremoteplayback"
        disablePictureInPicture
        @timeupdate="onTimeUpdate"
        @seeking="onSeeking"
        @contextmenu="onContextMenu"
        @error="onVideoError"
      ></video>

      <div class="flash success">{{ readyText }}</div>
      <div v-if="videoLoadError" class="flash error">{{ videoLoadError }}</div>
      <div class="info-grid">
        <div class="mini-card"><strong>Forward</strong><br>Oldinga o‘tkazish bloklangan</div>
        <div class="mini-card"><strong>Ovoz</strong><br>Video bilan birga eshitiladi</div>
        <div class="mini-card"><strong>Nazorat</strong><br>Faqat ochilgan kurs egalari ko‘radi</div>
      </div>
    </div>
  </section>

  <div v-else-if="error" class="center-box">
    <div class="card glass form-card">
      <h2>Xato</h2>
      <div class="flash error">{{ error }}</div>
      <button class="btn" @click="router.push('/')">Bosh sahifa</button>
    </div>
  </div>
</template>
