<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, socketURL, apiUrl } from '../lib'
import { io } from 'socket.io-client'

const router = useRouter()
const overview = ref({ students_count:0, active_students_count:0, active_students:[], recent_students:[], courses_count:0, unlocked_count:0, results_count:0, teachers_count:0, monthly_students_count:0, monthly_purchases_count:0 })
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
    <div class="card glass admin-info-hero animated-card">
      <div>
        <span class="pill">Ma’lumotlar markazi</span>
        <h1>Saytdagi barcha ma’lumotlar</h1>
        <p class="muted">Bu bo‘lim faqat admin panelida ko‘rinadi. Har bir card o‘z ma’lumotini Excel qilib yuklaydi.</p>
      </div>
      <button class="btn" @click="downloadAll">Hammasini bitta Excelga yuklash</button>
    </div>
  </section>

  <section class="section admin-info-grid">
    <div class="card glass info-data-card hover-card">
      <div class="info-card-top"><span class="info-icon">👥</span><span class="pill">Foydalanuvchilar</span></div>
      <h2>O‘quvchilar</h2>
      <div class="info-big">{{ overview.students_count || 0 }}</div>
      <p class="muted">Jami registratsiyadan o‘tgan o‘quvchilar. Hozir online: {{ overview.active_students_count || 0 }}</p>
      <div class="mini-student-grid">
        <div v-for="item in studentPreview.slice(0,3)" :key="item.id || item.username" class="student-mini-pill">
          <strong>{{ item.name || ((item.first_name || '') + ' ' + (item.last_name || '')).trim() || item.username }}</strong>
          <small>{{ item.email || 'email yo‘q' }}</small>
        </div>
      </div>
      <button class="btn btn-sm" @click="download('students')">O‘quvchilar Excel</button>
    </div>

    <div class="card glass info-data-card hover-card">
      <div class="info-card-top"><span class="info-icon">🗓️</span><span class="pill">1 oy</span></div>
      <h2>Oylik kirishlar</h2>
      <div class="info-big">{{ overview.monthly_students_count || 0 }}</div>
      <p class="muted">Oxirgi 30 kunda registratsiya qilgan foydalanuvchilar soni.</p>
      <button class="btn btn-sm" @click="download('monthly')">Oylik Excel</button>
    </div>

    <div class="card glass info-data-card hover-card">
      <div class="info-card-top"><span class="info-icon">🛒</span><span class="pill">Sotuv</span></div>
      <h2>Kurs sotib olish</h2>
      <div class="info-big">{{ overview.unlocked_count || 0 }}</div>
      <p class="muted">Jami sotib olingan yoki ochilgan kurslar. Oxirgi 30 kun: {{ overview.monthly_purchases_count || 0 }}</p>
      <button class="btn btn-sm" @click="download('purchases')">Sotuv Excel</button>
    </div>

    <div class="card glass info-data-card hover-card all-info-card">
      <div class="info-card-top"><span class="info-icon">📦</span><span class="pill">Umumiy</span></div>
      <h2>Obshi Excel</h2>
      <div class="info-big">{{ overview.courses_count || 0 }}</div>
      <p class="muted">O‘quvchilar, oylik kirishlar, kurs sotib olishlar va umumiy statistika bitta Excel faylda.</p>
      <button class="btn btn-sm" @click="downloadAll">Hammasini yuklash</button>
    </div>
  </section>
</template>
