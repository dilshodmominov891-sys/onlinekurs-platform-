<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { api, socketURL } from '../lib'
import { io } from 'socket.io-client'
import CourseCard from '../components/CourseCard.vue'

const courses = ref([])
const loading = ref(false)
const activeLive = ref(null)
const latestTest = ref(null)
let socket

const liveCourses = computed(() => courses.value.filter((item) => item.is_live_class))

async function load() {
  loading.value = true
  try {
    const [coursesRes, liveRes] = await Promise.all([api.get('/courses'), api.get('/live/active')])
    courses.value = coursesRes.data.courses || []
    activeLive.value = liveRes.data.class || null
    latestTest.value = liveRes.data.latest_test || null
  } finally {
    loading.value = false
  }
}

function connectSocket() {
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('live-status-changed', ({ class: klass, is_live }) => {
    activeLive.value = is_live ? klass : null
  })
}

onMounted(() => { load(); connectSocket() })
onBeforeUnmount(() => socket?.disconnect())
</script>

<template>
  <section class="section">
    <div v-if="activeLive" class="card glass live-now-banner animated-card">
      <div>
        <span class="pill">🔴 Live dars yoqildi</span>
        <h1>Ustoz hozir jonli dars o‘tyapti</h1>
        <p class="lead">Live bo‘limdan qo‘shiling. Ustoz ekranini ko‘rasiz va ovozini eshitasiz.</p>
      </div>
      <RouterLink class="btn btn-warning" :to="`/room/${activeLive.room_code}`">Live darsga qo‘shilish</RouterLink>
    </div>
  </section>

  <section class="section">
    <div class="card glass live-course-hero hero-spotlight">
      <div>
        <span class="pill">Pullik live darslar</span>
        <h1>Live yozuv kurslari</h1>
        <p class="lead">Bu bo‘limda live olib qo‘yilgan kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.</p>
      </div>
      <div class="hero-illustration-card">
        <div class="hero-orbit hero-orbit-small"></div>
        <div class="hero-logo-ring">LIVE</div>
      </div>
    </div>
  </section>

  <section class="section">
    <div v-if="loading" class="flash success">Live kurslar yuklanmoqda...</div>
    <div v-else class="class-grid">
      <CourseCard v-for="course in liveCourses" :key="course.id" :course="course" />
      <div v-if="!liveCourses.length" class="card glass empty-state-card">Hali live video kurs qo‘shilmagan.</div>
    </div>
  </section>
</template>
