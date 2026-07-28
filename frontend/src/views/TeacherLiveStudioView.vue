<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { io } from 'socket.io-client'
import { api, socketURL } from '../lib'

const klass = ref(null)
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
const showSaveLevelInput = ref(false)
const saveSuccessCourse = ref(null)
const isPaused = ref(false)
const isStarting = ref(false)
const peerConnections = {}
let socket

const classId = computed(() => klass.value?.id)
const liveOn = computed(() => Boolean(klass.value?.is_live))
const recordingStopped = computed(() => Boolean(recordedBlob.value || saveForm.video_url) && !localStream.value && !(mediaRecorder.value && mediaRecorder.value.state && mediaRecorder.value.state !== 'inactive'))
const canShowSaveButton = computed(() => recordingStopped.value && !saveSuccessCourse.value)
const saveStepReady = computed(() => showSaveLevelInput.value && canShowSaveButton.value)

const saveForm = reactive({
  base_course_id: '',
  title: '',
  summary: '',
  level: '',
  video_url: '',
  price: '99000',
})

function showAlert(message) {
  const id = Date.now() + Math.random()
  alerts.value.unshift({ id, message })
  setTimeout(() => { alerts.value = alerts.value.filter((item) => item.id !== id) }, 5000)
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

async function sendOfferToStudent(studentId) {
  if (!localStream.value) return
  if (peerConnections[studentId]) {
    peerConnections[studentId].close()
    delete peerConnections[studentId]
  }
  const pc = createPeerConnection(studentId)
  const offer = await pc.createOffer()
  await pc.setLocalDescription(offer)
  socket.emit('webrtc-offer', { target: studentId, offer })
}

function connectSocket() {
  if (!klass.value || socket) return
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('connect', () => {
    socket.emit('join-room', { room: klass.value.room_code, role: 'teacher', name: 'Ustoz' })
  })
  socket.on('student-joined', async ({ studentId, name, joinedAt }) => {
    if (!participants.value.find((item) => item.sid === studentId)) {
      participants.value.unshift({ sid: studentId, name, joinedAt })
      showAlert(`${name} darsga qo‘shildi`)
    }
    await sendOfferToStudent(studentId)
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
  socket.on('participants-update', ({ count }) => { participantCount.value = count })
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

async function load() {
  error.value = ''
  try {
    const { data } = await api.get('/admin/live/default-class')
    klass.value = data.class
    const coursesRes = await api.get('/admin/courses')
    adminCourses.value = coursesRes.data.courses || []
    if (!saveForm.base_course_id && adminCourses.value.length) saveForm.base_course_id = String(adminCourses.value[0].id)
    if (!saveForm.title) saveForm.title = `${klass.value.title} yozuvi`
    connectSocket()
  } catch (err) {
    error.value = err.response?.data?.error || 'Live bo‘lim yuklanmadi. Avval ustoz login qiling.'
  }
}

function setupRecorder(stream) {
  recordedChunks.value = []
  recordedBlob.value = null
  recordingNotice.value = 'Live yozuv boshlandi. Pauza kerak bo‘lsa “Pauza” ni bosing. Kursga saqlash faqat dars to‘xtagandan keyin chiqadi.'
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
    recordingNotice.value = 'Live yozuv tayyor. Serverga yuklanmoqda...'
    try {
      await ensureUploadedRecording(true)
      recordingNotice.value = 'Live yozuv serverga saqlandi. Endi “Kursga saqlash” tugmasi orqali darajani yozib kurslarga qo‘shing.'
    } catch {
      recordingNotice.value = 'Yozuv tayyor, lekin serverga yuklashda xato bo‘ldi. Dars darajasini yozib, saqlashni yana bosing.'
    }
  }
  recorder.start(1000)
  mediaRecorder.value = recorder
  isPaused.value = false
}

async function startShare() {
  localStream.value = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true })
  if (teacherPreview.value) teacherPreview.value.srcObject = localStream.value
  localStream.value.getVideoTracks()[0]?.addEventListener('ended', stopShare)
  setupRecorder(localStream.value)
  for (const student of participants.value) await sendOfferToStudent(student.sid)
}

async function toggleLiveStatus(forceValue = null) {
  if (!classId.value) return
  const shouldChange = forceValue === null || Boolean(klass.value.is_live) !== Boolean(forceValue)
  if (!shouldChange) return
  const { data } = await api.post(`/admin/classes/${classId.value}/toggle-live`)
  klass.value = data.class
}

async function startLive() {
  if (isStarting.value) return
  isStarting.value = true
  error.value = ''
  try {
    if (!liveOn.value) await toggleLiveStatus(true)
    await startShare()
    showAlert('Live dars yoqildi. O‘quvchilar panelida qo‘shilish tugmasi chiqadi.')
  } catch (err) {
    error.value = err.message || 'Ekran yozish/ulashga ruxsat berilmadi.'
    if (!localStream.value && liveOn.value) await toggleLiveStatus(false)
  } finally {
    isStarting.value = false
  }
}

function pauseOrResume() {
  if (!localStream.value || !mediaRecorder.value) return
  if (!isPaused.value) {
    if (mediaRecorder.value.state === 'recording') mediaRecorder.value.pause()
    localStream.value.getTracks().forEach((track) => { track.enabled = false })
    isPaused.value = true
    recordingNotice.value = 'Live pauza qilindi. Yana bossangiz davom etadi.'
  } else {
    localStream.value.getTracks().forEach((track) => { track.enabled = true })
    if (mediaRecorder.value.state === 'paused') mediaRecorder.value.resume()
    isPaused.value = false
    recordingNotice.value = 'Live davom etmoqda.'
  }
}

function stopShare() {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') mediaRecorder.value.stop()
  if (localStream.value) {
    localStream.value.getTracks().forEach((track) => track.stop())
    localStream.value = null
  }
  isPaused.value = false
  Object.values(peerConnections).forEach((pc) => pc.close())
  Object.keys(peerConnections).forEach((key) => delete peerConnections[key])
  if (teacherPreview.value) teacherPreview.value.srcObject = null
}

async function stopLive() {
  error.value = ''
  stopShare()
  try {
    if (liveOn.value) await toggleLiveStatus(false)
    showAlert('Live dars to‘xtatildi. Yozuv tayyor bo‘lsa kursga saqlang.')
  } catch (err) {
    error.value = err.response?.data?.error || 'Live o‘chmadi.'
  }
}

async function ensureUploadedRecording(force = false) {
  if (saveForm.video_url && !force) return saveForm.video_url
  if (!recordedBlob.value) return saveForm.video_url || ''
  recordingUploading.value = true
  try {
    const formData = new FormData()
    const ext = recordedBlob.value.type.includes('webm') ? 'webm' : 'mp4'
    formData.append('file', recordedBlob.value, `live-recording.${ext}`)
    const { data } = await api.post('/admin/uploads/live-recording', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    saveForm.video_url = data.url
    return saveForm.video_url
  } finally {
    recordingUploading.value = false
  }
}

async function saveLiveCourse() {
  error.value = ''
  saveSuccessCourse.value = null
  if (localStream.value || (mediaRecorder.value && mediaRecorder.value.state !== 'inactive')) {
    error.value = 'Avval “Live to‘xtatish” tugmasini bosing. Dars tugagandan keyin saqlash chiqadi.'
    return
  }
  showSaveLevelInput.value = true
  if (!saveForm.level.trim()) {
    error.value = 'Dars darajasini yozing. Masalan: HTML, JS, Vue yoki Backend. Keyin yana “Saqlashni tasdiqlash” bosing.'
    return
  }
  try {
    const uploadedUrl = await ensureUploadedRecording()
    if (!uploadedUrl) {
      error.value = 'Avval live darsni boshlang va “Live to‘xtatish” tugmasini bosing.'
      return
    }
    const payload = { ...saveForm, level: saveForm.level.trim(), video_url: uploadedUrl }
    const { data } = await api.post(`/admin/classes/${classId.value}/save-live-course`, payload)
    saveSuccessCourse.value = data.course
    recordingNotice.value = 'Live dars kurslar bo‘limiga saqlandi. Kurs kartasida tepada “Live dars”, pastida daraja ko‘rinadi.'
    showAlert(data.message || 'Live dars kurslarga saqlandi')
  } catch (err) {
    error.value = err.response?.data?.error || 'Kursga saqlashda xato.'
  }
}

function kickStudent(studentId) {
  socket?.emit('kick-student', { studentId })
  participants.value = participants.value.filter((item) => item.sid !== studentId)
}

onMounted(load)
onBeforeUnmount(() => { stopShare(); socket?.disconnect() })
</script>

<template>
  <div class="stack section">
    <section class="card glass live-teacher-hero hero-spotlight animated-card">
      <div class="section-head">
        <div>
          <span class="pill">Ustoz live studiyasi</span>
          <h1>Live dars o‘tish</h1>
          <p class="lead">Live darsni yoqing: o‘quvchi panelida “Live dars yoqildi” xabari va qo‘shilish tugmasi chiqadi. Faqat ustoz gapiradi, o‘quvchilar ekran va ovozni ko‘radi.</p>
        </div>
        <span :class="['badge', liveOn ? 'live' : 'offline']">{{ liveOn ? 'LIVE YOQILGAN' : 'OFFLINE' }}</span>
      </div>
      <div v-if="klass" class="info-grid">
        <div class="mini-card"><strong>Xona kodi</strong><br>{{ klass.room_code }}</div>
        <div class="mini-card"><strong>O‘quvchilar</strong><br>{{ participantCount }} ta online</div>
        <div class="mini-card"><strong>Holat</strong><br>{{ localStream ? (isPaused ? 'Pauza' : 'Ekran uzatilmoqda') : 'Kutilmoqda' }}</div>
      </div>
      <div v-if="error" class="flash error">{{ error }}</div>
    </section>

    <div v-if="alerts.length" class="alert-stack">
      <div v-for="item in alerts" :key="item.id" class="flash success teacher-alert">{{ item.message }}</div>
    </div>

    <section v-if="klass" class="grid-2 gap-lg">
      <div class="card glass live-stage animated-card">
        <div class="video-top">
          <div>
            <h2>100% ekran yozish va live uzatish</h2>
            <p class="muted">Chrome oynasida “Entire screen / Весь экран” ni tanlang va “Share audio” ni belgilang.</p>
          </div>
          <span class="pill">{{ isPaused ? 'PAUZA' : (localStream ? 'UZATILMOQDA' : 'TAYYOR') }}</span>
        </div>
        <video ref="teacherPreview" autoplay muted playsinline></video>
        <div class="row gap-sm wrap live-control-row">
          <button class="btn" :disabled="isStarting" @click="startLive">{{ isStarting ? 'Yoqilmoqda...' : 'Live darsni yoqish' }}</button>
          <button class="btn btn-secondary" :disabled="!localStream" @click="pauseOrResume">{{ isPaused ? 'Davom ettirish' : 'Pauza' }}</button>
          <button class="btn btn-danger-soft" :disabled="!localStream && !liveOn" @click="stopLive">Live to‘xtatish</button>
          <button v-if="canShowSaveButton" class="btn btn-warning" :disabled="recordingUploading" @click="saveLiveCourse">{{ recordingUploading ? 'Yuklanmoqda...' : (saveStepReady ? 'Saqlashni tasdiqlash' : 'Kursga saqlash') }}</button>
        </div>
        <div v-if="showSaveLevelInput && canShowSaveButton" class="inline-save-level card-soft save-level-focus">
          <label>Dars darajasi / mavzusi</label>
          <input v-model="saveForm.level" type="text" placeholder="Masalan: HTML, JS, Vue, React, Backend" @keyup.enter="saveLiveCourse" />
          <small class="hint">Kurslar bo‘limida tepasida “Live dars”, pastida shu daraja ko‘rinadi. Yozib bo‘lgach “Saqlashni tasdiqlash” bosing.</small>
        </div>
        <div v-if="recordingNotice" class="flash success">{{ recordingNotice }}</div>
        <RouterLink v-if="saveSuccessCourse" class="btn btn-sm btn-secondary" :to="`/course/${saveSuccessCourse.slug}`">Saqlangan kursni ko‘rish</RouterLink>
        <div class="flash success">O‘quvchilar faqat videoni ko‘radi va ovozni eshitadi. Ularning kamerasi/mikrofoni olinmaydi.</div>
      </div>

      <div class="card glass animated-card">
        <h2>Kursga saqlash sozlamasi</h2>
        <p class="muted small-text">Saqlash tugmasi dars to‘xtatilgandan keyin chiqadi. Darajani yozmasdan kursga tushmaydi.</p>
        <div class="stack live-save-panel">
          <select v-model="saveForm.base_course_id">
            <option disabled value="">Kursni tanlang</option>
            <option v-for="course in adminCourses" :key="course.id" :value="String(course.id)">{{ course.title }}</option>
          </select>
          <input v-model="saveForm.title" type="text" placeholder="Saqlanadigan kurs nomi" />
          <input v-model="saveForm.summary" type="text" placeholder="Qisqa izoh" />
          <input v-model="saveForm.level" type="text" placeholder="Dars darajasi: HTML, JS, Vue, Backend..." />
          <input v-model="saveForm.video_url" type="text" placeholder="Yozuv video linki (avtomatik tushadi)" />
          <input v-model="saveForm.price" type="number" placeholder="Narx" />
          <small class="hint">Saqlangandan keyin live yozuv “Live darslar” kurslari bo‘limiga tushadi va sotib olish paroli bilan ochiladi.</small>
        </div>
      </div>
    </section>

    <section class="card glass animated-card">
      <div class="section-head">
        <div><h2>Livega kirgan o‘quvchilar</h2><p class="muted">O‘quvchi qo‘shilsa shu yerda ko‘rinadi.</p></div>
        <span class="pill">{{ participants.length }} ta</span>
      </div>
      <div class="student-list">
        <div v-for="student in participants" :key="student.sid" class="student-item student-item-rich">
          <div><strong>{{ student.name }}</strong><div class="muted small-text">Qo‘shilgan vaqti: {{ formatJoinedAt(student.joinedAt) }}</div></div>
          <button class="btn btn-sm btn-secondary" @click="kickStudent(student.sid)">Chiqarish</button>
        </div>
        <p v-if="!participants.length" class="muted">Hali o‘quvchi qo‘shilmadi.</p>
      </div>
    </section>
  </div>
</template>
