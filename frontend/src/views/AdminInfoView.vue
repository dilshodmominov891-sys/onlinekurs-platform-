<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, socketURL, apiUrl } from '../lib'
import { io } from 'socket.io-client'
import analyticsHero from '../assets/analytics-hero.svg'

const router = useRouter()
const overview = ref({
  students_count:0,
  active_students_count:0,
  active_students:[],
  recent_students:[],
  courses_count:0,
  unlocked_count:0,
  results_count:0,
  teachers_count:0,
  monthly_students_count:0,
  monthly_purchases_count:0,
  daily_students_count:0,
  daily_purchases_count:0,
  yearly_students_count:0,
  yearly_purchases_count:0,
})
const loading = ref(false)
let socket, timer
const studentPreview = computed(() => (overview.value.active_students || []).length ? overview.value.active_students : (overview.value.recent_students || []))

async function load(){
  loading.value = true
  try{
    const session = await api.get('/admin/session')
    if(!session.data.is_admin){ router.replace('/auth'); return }
    const { data } = await api.get('/admin/overview')
    overview.value = { ...overview.value, ...data }
  }catch{ router.replace('/auth') }
  finally{ loading.value = false }
}
function connect(){
  socket = io(socketURL, { transports:['websocket','polling'], withCredentials:true })
  socket.on('connect', () => socket.emit('admin-watch'))
  socket.on('admin-overview-live', (payload) => overview.value = { ...overview.value, ...payload })
}
function download(kind){ window.open(apiUrl(`/admin/export/${kind}.xls`), '_blank') }
function downloadAll(){ window.open(apiUrl('/admin/export/all-info.xls'), '_blank') }
onMounted(() => { load(); connect(); timer=setInterval(load,3000) })
onBeforeUnmount(() => { if(timer) clearInterval(timer); socket?.disconnect() })
</script>

<template>
  <section class="section">
    <div class="card glass admin-info-hero animated-card admin-info-hero-rich">
      <div class="admin-info-hero-text">
        <span class="pill">Excel markazi</span>
        <h1>Saytdagi barcha ma’lumotlar</h1>
        <p class="muted">Kunlik, oylik va yillik hisobotlarni bitta joydan yuklang. Har bir blok alohida Excel fayl ochadi.</p>
        <div class="row wrap gap-sm admin-info-actions">
          <button class="btn" @click="downloadAll">Hammasini bitta Excelga yuklash</button>
          <button class="btn btn-secondary" @click="download('students')">O‘quvchilar Excel</button>
        </div>
      </div>
      <div class="admin-info-hero-media">
        <img :src="analyticsHero" alt="Analitika" class="hero-dashboard-image" />
      </div>
    </div>
  </section>

  <section class="section quick-strip-grid">
    <div class="mini-card quick-strip-item hover-card">
      <span>👥</span>
      <div><strong>{{ overview.students_count || 0 }}</strong><small class="muted">Jami o‘quvchi</small></div>
    </div>
    <div class="mini-card quick-strip-item hover-card">
      <span>🟢</span>
      <div><strong>{{ overview.active_students_count || 0 }}</strong><small class="muted">Hozir online</small></div>
    </div>
    <div class="mini-card quick-strip-item hover-card">
      <span>🛒</span>
      <div><strong>{{ overview.unlocked_count || 0 }}</strong><small class="muted">Jami sotuv</small></div>
    </div>
    <div class="mini-card quick-strip-item hover-card">
      <span>🧪</span>
      <div><strong>{{ overview.results_count || 0 }}</strong><small class="muted">Natijalar</small></div>
    </div>
  </section>

  <section class="section admin-info-grid admin-info-grid-rich">
    <div class="card glass info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">☀️</span><span class="pill">Kunlik</span></div>
      <h2>Kunlik ma’lumot</h2>
      <div class="info-big">{{ overview.daily_students_count || 0 }}</div>
      <p class="muted">Bugun ro‘yxatdan o‘tgan o‘quvchilar soni. Bugungi sotuvlar: {{ overview.daily_purchases_count || 0 }}</p>
      <button class="btn btn-sm" @click="download('daily')">Kunlik Excel</button>
    </div>

    <div class="card glass info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">🗓️</span><span class="pill">Oylik</span></div>
      <h2>Oylik ma’lumot</h2>
      <div class="info-big">{{ overview.monthly_students_count || 0 }}</div>
      <p class="muted">Joriy oyda qo‘shilgan o‘quvchilar. Shu oy sotuvlar: {{ overview.monthly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" @click="download('monthly')">Oylik Excel</button>
    </div>

    <div class="card glass info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">📅</span><span class="pill">Yillik</span></div>
      <h2>Yillik ma’lumot</h2>
      <div class="info-big">{{ overview.yearly_students_count || 0 }}</div>
      <p class="muted">Joriy yilda qo‘shilgan o‘quvchilar. Yillik sotuvlar: {{ overview.yearly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" @click="download('yearly')">Yillik Excel</button>
    </div>

    <div class="card glass info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">🛒</span><span class="pill">Sotuv</span></div>
      <h2>Kurs sotib olishlar</h2>
      <div class="info-big">{{ overview.unlocked_count || 0 }}</div>
      <p class="muted">Barcha ochilgan kurslar va sotuvlar ro‘yxati. Oxirgi 30 kun: {{ overview.monthly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" @click="download('purchases')">Sotuv Excel</button>
    </div>

    <div class="card glass info-data-card hover-card info-data-card-rich all-info-card">
      <div class="info-card-top"><span class="info-icon">📦</span><span class="pill">Umumiy</span></div>
      <h2>Obshiy hisobot</h2>
      <div class="info-big">{{ overview.courses_count || 0 }}</div>
      <p class="muted">O‘quvchilar, kunlik-oylik-yillik hisobotlar va sotuvlar bitta Excel faylda.</p>
      <button class="btn btn-sm" @click="downloadAll">Hammasini yuklash</button>
    </div>
  </section>

  <section class="section">
    <div class="card glass preview-students-card hover-card">
      <div class="section-head compact-head">
        <div>
          <h3>Tezkor o‘quvchi ko‘rinishi</h3>
          <p class="muted">Aktiv yoki so‘nggi o‘quvchilar kichik preview ko‘rinishida.</p>
        </div>
        <span class="pill">{{ studentPreview.length }} ta ko‘rinish</span>
      </div>
      <div class="mini-student-grid big-preview-grid">
        <div v-for="item in studentPreview.slice(0,4)" :key="item.id || item.username" class="student-mini-pill student-mini-pill-rich">
          <strong>{{ item.name || ((item.first_name || '') + ' ' + (item.last_name || '')).trim() || item.username }}</strong>
          <small>{{ item.email || 'email yo‘q' }}</small>
          <small>{{ item.phone || 'telefon yo‘q' }}</small>
        </div>
        <p v-if="!studentPreview.length" class="muted">Hozircha ko‘rinadigan o‘quvchi yo‘q.</p>
      </div>
    </div>
  </section>
</template>
