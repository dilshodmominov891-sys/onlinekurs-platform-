<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import { api, socketURL } from '../lib'
import * as XLSX from 'xlsx'

const route = useRoute()
const router = useRouter()
const classId = computed(() => route.params.id)
const klass = ref(null)
const latestTest = ref(null)
const excelNotice = ref('')
const adminCourses = ref([])
const participants = ref([])
const participantCount = ref(0)
const alerts = ref([])
const error = ref('')
const teacherPreview = ref(null)
const localStream = ref(null)
const mediaRecorder = ref(null)
const recordedChunks = ref([])
const recordedBlob = ref(null)
const recordingNotice = ref('')
const recordingUploading = ref(false)
const peerConnections = {}
let socket

const form = reactive({
  title: '',
  questions: [0, 1, 2].map(() => ({
    question: '',
    options: { A: '', B: '', C: '', D: '' },
    correct: 'A',
  })),
})

const saveForm = reactive({
  base_course_id: '',
  title: '',
  summary: '',
  video_url: '',
  price: '99000',
})

function showAlert(message) {
  const id = Date.now() + Math.random()
  alerts.value.unshift({ id, message })
  setTimeout(() => {
    alerts.value = alerts.value.filter((item) => item.id !== id)
  }, 5000)
}

function formatJoinedAt(joinedAt) {
  if (!joinedAt) return 'Hozirgina qo‘shildi'
  return new Date(joinedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function createPeerConnection(targetId) {
  const pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] })
  peerConnections[targetId] = pc
  if (localStream.value) localStream.value.getTracks().forEach((track) => pc.addTrack(track, localStream.value))
  pc.onicecandidate = (event) => {
    if (event.candidate) socket.emit('webrtc-ice-candidate', { target: targetId, candidate: event.candidate })
  }
  return pc
}

async function load() {
  try {
    const { data } = await api.get(`/admin/classes/${classId.value}`)
    klass.value = data.class
    latestTest.value = data.latest_test
    const coursesRes = await api.get('/admin/courses')
    adminCourses.value = coursesRes.data.courses || []
    if (!saveForm.base_course_id && adminCourses.value.length) saveForm.base_course_id = String(adminCourses.value[0].id)
    if (!saveForm.title) saveForm.title = `${data.class.title} live yozuvi`
    connectSocket()
  } catch {
    router.push('/admin/login')
  }
}

function connectSocket() {
  if (!klass.value || socket) return
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('connect', () => {
    socket.emit('join-room', { room: klass.value.room_code, role: 'teacher', name: 'Teacher' })
  })
  socket.on('student-joined', async ({ studentId, name, joinedAt }) => {
    if (!participants.value.find((item) => item.sid === studentId)) {
      participants.value.unshift({ sid: studentId, name, joinedAt })
      showAlert(`${name} darsga qo‘shildi`)
    }
    if (!localStream.value) return
    const pc = createPeerConnection(studentId)
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    socket.emit('webrtc-offer', { target: studentId, offer })
  })
  socket.on('student-left', ({ studentId }) => {
    const leftStudent = participants.value.find((item) => item.sid === studentId)
    if (leftStudent) showAlert(`${leftStudent.name} darsdan chiqdi`)
    participants.value = participants.value.filter((item) => item.sid !== studentId)
    if (peerConnections[studentId]) {
      peerConnections[studentId].close()
      delete peerConnections[studentId]
    }
  })
  socket.on('participants-update', ({ count }) => {
    participantCount.value = count
  })
  socket.on('webrtc-answer', async ({ answer, from }) => {
    const pc = peerConnections[from]
    if (pc) await pc.setRemoteDescription(new RTCSessionDescription(answer))
  })
  socket.on('webrtc-ice-candidate', async ({ candidate, from }) => {
    const pc = peerConnections[from]
    if (pc && candidate) {
      try { await pc.addIceCandidate(new RTCIceCandidate(candidate)) } catch (e) { console.error(e) }
    }
  })
}

function setupRecorder(stream) {
  recordedChunks.value = []
  recordedBlob.value = null
  recordingNotice.value = 'Live yozuv tayyorlanmoqda...'
  const mimeCandidates = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm']
  const mimeType = mimeCandidates.find((item) => window.MediaRecorder && MediaRecorder.isTypeSupported(item)) || ''
  const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
  recorder.ondataavailable = (event) => {
    if (event.data && event.data.size > 0) recordedChunks.value.push(event.data)
  }
  recorder.onstop = async () => {
    if (!recordedChunks.value.length) {
      recordingNotice.value = 'Yozuv saqlanmadi. Qaytadan urinib ko‘ring.'
      return
    }
    const finalType = recordedChunks.value[0]?.type || mimeType || 'video/webm'
    recordedBlob.value = new Blob(recordedChunks.value, { type: finalType })
    recordingNotice.value = 'Live yozuv saqlandi. Serverga yuklanmoqda...'
    try {
      await ensureUploadedRecording(true)
      recordingNotice.value = 'Live yozuv saqlandi. Endi Kursga saqlash bossangiz kursga video bo‘lib tushadi.'
    } catch (e) {
      recordingNotice.value = 'Yozuv tayyor, lekin serverga yuklashda xato bo‘ldi. Kursga saqlashni yana bosing.'
    }
  }
  recorder.start(1000)
  mediaRecorder.value = recorder
}

async function startShare() {
  try {
    error.value = ''
    localStream.value = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true })
    if (teacherPreview.value) teacherPreview.value.srcObject = localStream.value
    localStream.value.getVideoTracks()[0]?.addEventListener('ended', stopShare)
    setupRecorder(localStream.value)
    for (const student of participants.value) {
      if (peerConnections[student.sid]) {
        peerConnections[student.sid].close()
        delete peerConnections[student.sid]
      }
      const pc = createPeerConnection(student.sid)
      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)
      socket.emit('webrtc-offer', { target: student.sid, offer })
    }
    showAlert('Live boshlandi. Ekran va ovoz uzatilmoqda.')
  } catch (err) {
    error.value = err.message || 'Screen share xatosi.'
  }
}

function stopShare() {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
  }
  if (localStream.value) {
    localStream.value.getTracks().forEach((track) => track.stop())
    localStream.value = null
  }
  Object.values(peerConnections).forEach((pc) => pc.close())
  Object.keys(peerConnections).forEach((key) => delete peerConnections[key])
  if (teacherPreview.value) teacherPreview.value.srcObject = null
}

async function ensureUploadedRecording(force = false) {
  if (saveForm.video_url && !force) return saveForm.video_url
  if (!recordedBlob.value) return saveForm.video_url || ''
  recordingUploading.value = true
  const formData = new FormData()
  const ext = recordedBlob.value.type.includes('webm') ? 'webm' : 'mp4'
  formData.append('file', recordedBlob.value, `live-recording.${ext}`)
  const { data } = await api.post('/admin/uploads/live-recording', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  saveForm.video_url = data.url
  recordingUploading.value = false
  return saveForm.video_url
}

async function toggleLive() {
  const { data } = await api.post(`/admin/classes/${classId.value}/toggle-live`)
  klass.value = data.class
  showAlert(data.class.is_live ? 'Live dars yoqildi' : 'Live dars o‘chirildi')
}

async function saveTest() {
  error.value = ''
  try {
    const { data } = await api.post(`/admin/classes/${classId.value}/tests`, form)
    latestTest.value = data.test
    showAlert('Test saqlandi')
  } catch (err) {
    error.value = err.response?.data?.error || 'Test saqlanmadi.'
  }
}



async function saveLiveCourse() {
  error.value = ''
  try {
    const uploadedUrl = await ensureUploadedRecording()
    if (!uploadedUrl) {
      error.value = 'Avval live darsni boshlating va to‘xtating yoki video link kiriting.'
      return
    }
    const payload = { ...saveForm, video_url: uploadedUrl }
    const { data } = await api.post(`/admin/classes/${classId.value}/save-live-course`, payload)
    showAlert(data.message || 'Live dars kurslarga saqlandi')
  } catch (err) {
    error.value = err.response?.data?.error || 'Saqlashda xato.'
  }
}

function kickStudent(studentId) {
  socket.emit('kick-student', { studentId })
  participants.value = participants.value.filter((item) => item.sid !== studentId)
}

function emptyQuestion(idx) {
  return { question: `Savol ${idx + 1}`, options: { A: '', B: '', C: '', D: '' }, correct: 'A' }
}

async function importExcelInline(event) {
  excelNotice.value = ''
  error.value = ''
  const file = event.target.files?.[0]
  if (!file) return
  try {
    const buffer = await file.arrayBuffer()
    const wb = XLSX.read(buffer, { type: 'array' })
    const ws = wb.Sheets[wb.SheetNames[0]]
    const rows = XLSX.utils.sheet_to_json(ws, { defval: '' })
    const normalized = rows.map((row) => ({
      question: String(row.question || row.Question || row.savol || row.Savol || '').trim(),
      options: {
        A: String(row.a || row.A || row['variant_a'] || row['A variant'] || '').trim(),
        B: String(row.b || row.B || row['variant_b'] || row['B variant'] || '').trim(),
        C: String(row.c || row.C || row['variant_c'] || row['C variant'] || '').trim(),
        D: String(row.d || row.D || row['variant_d'] || row['D variant'] || '').trim(),
      },
      correct: String(row.correct || row.Correct || row.javob || row.Javob || 'A').trim().toUpperCase(),
    })).filter((q) => q.question && q.options.A && q.options.B && q.options.C && q.options.D && ['A','B','C','D'].includes(q.correct))

    if (!normalized.length) {
      error.value = 'Excel formati noto‘g‘ri. Ustunlar: question, a, b, c, d, correct'
      return
    }

    form.title = file.name.replace(/\.[^.]+$/, '') || 'Excel test'
    form.questions.splice(0, form.questions.length, ...normalized)
    excelNotice.value = `Excel yuklandi: ${normalized.length} ta savol shu formga joylandi.`
  } catch (e) {
    error.value = 'Excel faylni o‘qib bo‘lmadi.'
  } finally {
    event.target.value = ''
  }
}

onMounted(load)
onBeforeUnmount(() => { stopShare(); socket?.disconnect() })
</script>

<template>
  <div v-if="klass">
    <section class="card glass">
      <div class="room-head">
        <div>
          <h1>{{ klass.title }}</h1>
          <p>{{ klass.description || 'Tavsif kiritilmagan' }}</p>
        </div>
        <button class="btn" @click="toggleLive">{{ klass.is_live ? 'Live ni o‘chirish' : 'Live ni yoqish' }}</button>
      </div>
    </section>

    <div v-if="alerts.length" class="alert-stack">
      <div v-for="item in alerts" :key="item.id" class="flash success teacher-alert">{{ item.message }}</div>
    </div>

    <section class="grid-2 gap-lg section">
      <div class="card live-stage">
        <div class="video-top">
          <h2>Ustoz live studiyasi</h2>
          <span class="pill">{{ participantCount }} o‘quvchi</span>
        </div>
        <video ref="teacherPreview" autoplay muted playsinline></video>
        <div class="row gap-sm wrap">
          <button class="btn" @click="startShare">Ekran + ovoz ulash</button>
          <button class="btn btn-warning" :disabled="recordingUploading" @click="saveLiveCourse">{{ recordingUploading ? 'Yuklanmoqda...' : 'Kursga saqlash' }}</button>
          <button class="btn btn-secondary" @click="stopShare">To‘xtatish</button>
        </div>
        <div class="stack live-save-panel">
          <select v-model="saveForm.base_course_id">
            <option disabled value="">Kursni tanlang</option>
            <option v-for="course in adminCourses" :key="course.id" :value="String(course.id)">{{ course.title }}</option>
          </select>
          <input v-model="saveForm.title" type="text" placeholder="Saqlanadigan kurs nomi" />
          <input v-model="saveForm.summary" type="text" placeholder="Qisqa izoh" />
          <input v-model="saveForm.video_url" type="text" placeholder="Yozuv video linki (ixtiyoriy)" />
        <small class="hint">{{ recordingUploading ? 'Yozuv serverga yuklanmoqda...' : (saveForm.video_url ? `Tayyor video: ${saveForm.video_url}` : 'Live to‘xtagach yozuv shu yerga avtomatik tushadi.') }}</small>
          <div class="muted small-text">Agar live yozuv olingan bo‘lsa, link avtomatik to‘ladi. Shu link keyin kursdagi <strong>Live yozuvni ko‘rish</strong> tugmasida ochiladi.</div>
          <input v-model="saveForm.price" type="number" placeholder="Chegirma narx" />
        </div>
        <div class="flash success">Brauzer ruxsat bersa, o‘quvchilar ustoz ekranini va ovozini online ko‘radi.</div>
        <div v-if="recordingNotice" class="flash success">{{ recordingNotice }}</div>
        <div v-if="error" class="flash error">{{ error }}</div>
      </div>
      <div class="card">
        <h2>O‘quvchilar</h2>
        <div class="student-list">
          <div v-for="student in participants" :key="student.sid" class="student-item student-item-rich">
            <div>
              <strong>{{ student.name }}</strong>
              <div class="muted small-text">Qo‘shilgan vaqti: {{ formatJoinedAt(student.joinedAt) }}</div>
            </div>
            <button class="btn btn-sm btn-secondary" @click="kickStudent(student.sid)">Chiqarish</button>
          </div>
          <p v-if="!participants.length" class="muted">Hali o‘quvchi yo‘q.</p>
        </div>
      </div>
    </section>

    <section class="section card">
      <h2>Test yaratish</h2>
      <div class="stack">
        <input v-model="form.title" type="text" placeholder="Test nomi" />
        <label class="excel-inline-upload">
          <span class="option-badge excel">XLSX</span>
          <span>Excel yuklash va savollarni shu formga tushirish</span>
          <input type="file" accept=".xlsx,.xls" @change="importExcelInline" />
        </label>
        <div v-if="excelNotice" class="flash success">{{ excelNotice }}</div>
        <div v-for="(question, idx) in form.questions" :key="idx" class="question-box">
          <input v-model="question.question" type="text" :placeholder="`Savol ${idx + 1}`" />
          <div class="grid-2 option-grid-admin">
            <label class="option-input admin-option a"><span class="option-badge">A</span><input v-model="question.options.A" type="text" placeholder="A variant" /></label>
            <label class="option-input admin-option b"><span class="option-badge">B</span><input v-model="question.options.B" type="text" placeholder="B variant" /></label>
            <label class="option-input admin-option c"><span class="option-badge">C</span><input v-model="question.options.C" type="text" placeholder="C variant" /></label>
            <label class="option-input admin-option d"><span class="option-badge">D</span><input v-model="question.options.D" type="text" placeholder="D variant" /></label>
          </div>
          <select v-model="question.correct">
            <option value="A">To‘g‘ri javob: A</option>
            <option value="B">To‘g‘ri javob: B</option>
            <option value="C">To‘g‘ri javob: C</option>
            <option value="D">To‘g‘ri javob: D</option>
          </select>
        </div>
        <button class="btn" @click="saveTest">Testni saqlash</button>
        <div v-if="error" class="flash error">{{ error }}</div>
      </div>
    </section>
  </div>
</template>
