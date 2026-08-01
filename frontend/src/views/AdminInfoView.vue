<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { api, socketURL, apiUrl } from '../lib'
import { io } from 'socket.io-client'
import analyticsHero from '../assets/analytics-hero.svg'

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
const error = ref('')
let socket
const studentPreview = computed(() => (overview.value.active_students || []).length ? overview.value.active_students : (overview.value.recent_students || []))

async function load(){
  loading.value = true
  error.value = ''
  try{
    // Router admin rolini bir marta tekshiradi. Bu sahifada /admin/session
    // ni qayta chaqirmaymiz — cross-site cookie kechiksa noto‘g‘ri login
    // sahifasiga chiqarib yubormasligi uchun to‘g‘ridan-to‘g‘ri ma’lumotni olamiz.
    const { data } = await api.get('/admin/overview')
    overview.value = { ...overview.value, ...data }
  }catch(err){
    error.value = err.response?.data?.error || 'Hisobotlar yuklanmadi. Sahifani bir marta yangilab ko‘ring.'
  } finally {
    loading.value = false
  }
}
function connect(){
  socket = io(socketURL, { transports:['websocket','polling'], withCredentials:true })
  socket.on('connect', () => socket.emit('admin-watch'))
  socket.on('admin-overview-live', (payload) => overview.value = { ...overview.value, ...payload })
}
function download(kind){ window.open(apiUrl(`/admin/export/${kind}.xls`), '_blank') }
function downloadAll(){ window.open(apiUrl('/admin/export/all-info.xls'), '_blank') }
onMounted(() => { load(); connect() })
onBeforeUnmount(() => { socket?.disconnect() })
</script>

<template>
  <section class="section report-page-intro">
    <div class="card admin-info-hero admin-info-hero-rich">
      <div class="admin-info-hero-text">
        <span class="pill">Excel markazi</span>
        <h1>Hisobotlar</h1>
        <p class="muted">Kunlik, oylik va yillik ko‘rsatkichlarni ko‘ring. Kerakli hisobotni Excel shaklida yuklab oling.</p>
        <div class="row wrap gap-sm admin-info-actions">
          <button class="btn" type="button" @click="downloadAll">Barcha hisobotlarni yuklash</button>
          <button class="btn btn-secondary" type="button" @click="download('students')">O‘quvchilar Excel</button>
        </div>
      </div>
      <div class="admin-info-hero-media" aria-hidden="true">
        <img :src="analyticsHero" alt="" class="hero-dashboard-image" />
      </div>
    </div>
  </section>

  <div v-if="loading" class="section card report-status-card">Hisobotlar yuklanmoqda...</div>
  <div v-if="error" class="section flash error report-status-card">{{ error }}</div>

  <section class="section quick-strip-grid">
    <div class="mini-card quick-strip-item hover-card">
      <span>👥</span>
      <div><strong>{{ overview.students_count || 0 }}</strong><small class="muted">Jami o‘quvchi</small></div>
    </div>
    <div class="mini-card quick-strip-item hover-card">
      <span>●</span>
      <div><strong>{{ overview.active_students_count || 0 }}</strong><small class="muted">Hozir online</small></div>
    </div>
    <div class="mini-card quick-strip-item hover-card">
      <span>▣</span>
      <div><strong>{{ overview.unlocked_count || 0 }}</strong><small class="muted">Jami sotuv</small></div>
    </div>
    <div class="mini-card quick-strip-item hover-card">
      <span>✓</span>
      <div><strong>{{ overview.results_count || 0 }}</strong><small class="muted">Test natijalari</small></div>
    </div>
  </section>

  <section class="section admin-info-grid admin-info-grid-rich">
    <div class="card info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">01</span><span class="pill">Kunlik</span></div>
      <h2>Bugungi ma’lumot</h2>
      <div class="info-big">{{ overview.daily_students_count || 0 }}</div>
      <p class="muted">Bugun ro‘yxatga qo‘shilgan o‘quvchilar. Bugungi sotuvlar: {{ overview.daily_purchases_count || 0 }}</p>
      <button class="btn btn-sm" type="button" @click="download('daily')">Kunlik Excel</button>
    </div>

    <div class="card info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">30</span><span class="pill">Oylik</span></div>
      <h2>Oylik ma’lumot</h2>
      <div class="info-big">{{ overview.monthly_students_count || 0 }}</div>
      <p class="muted">Joriy oyda qo‘shilgan o‘quvchilar. Shu oy sotuvlar: {{ overview.monthly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" type="button" @click="download('monthly')">Oylik Excel</button>
    </div>

    <div class="card info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">12</span><span class="pill">Yillik</span></div>
      <h2>Yillik ma’lumot</h2>
      <div class="info-big">{{ overview.yearly_students_count || 0 }}</div>
      <p class="muted">Joriy yilda qo‘shilgan o‘quvchilar. Yillik sotuvlar: {{ overview.yearly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" type="button" @click="download('yearly')">Yillik Excel</button>
    </div>

    <div class="card info-data-card hover-card info-data-card-rich">
      <div class="info-card-top"><span class="info-icon">$</span><span class="pill">Sotuv</span></div>
      <h2>Kurs sotib olishlar</h2>
      <div class="info-big">{{ overview.unlocked_count || 0 }}</div>
      <p class="muted">Barcha ochilgan kurslar va sotuvlar ro‘yxati. Oxirgi 30 kun: {{ overview.monthly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" type="button" @click="download('purchases')">Sotuv Excel</button>
    </div>

    <div class="card info-data-card hover-card info-data-card-rich all-info-card">
      <div class="info-card-top"><span class="info-icon">ALL</span><span class="pill">Umumiy</span></div>
      <h2>Umumiy hisobot</h2>
      <div class="info-big">{{ overview.courses_count || 0 }}</div>
      <p class="muted">O‘quvchilar, kunlik-oylik-yillik hisobotlar va sotuvlar bitta Excel faylda.</p>
      <button class="btn btn-sm" type="button" @click="downloadAll">Hammasini yuklash</button>
    </div>
  </section>

  <section class="section">
    <div class="card preview-students-card hover-card">
      <div class="section-head compact-head">
        <div>
          <h3>Tezkor o‘quvchi ko‘rinishi</h3>
          <p class="muted">Hozir online yoki oxirgi qo‘shilgan o‘quvchilar.</p>
        </div>
        <span class="pill">{{ studentPreview.length }} ta</span>
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
