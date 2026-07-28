<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import { api, socketURL } from '../lib'

const route = useRoute()
const router = useRouter()
const roomCode = computed(() => route.params.roomCode)
const studentName = computed(() => route.query.student_name || 'Guest')
const klass = ref(null)
const latestTest = ref(null)
const statusText = ref('Ustoz ulanishi kutilmoqda...')
const livePassword = ref(route.query.live_password || '')
const canJoin = computed(() => Boolean(klass.value?.is_live))
const joined = ref(false)
const joinError = ref('')
const videoRef = ref(null)
let socket
const peerConnections = {}

async function load() {
  try {
    const { data } = await api.get(`/classes/${roomCode.value}`)
    klass.value = data.class
    latestTest.value = data.latest_test
    if (livePassword.value) {
      await joinLive()
    }
  } catch {
    router.push('/')
  }
}

async function joinLive() {
  joinError.value = ''
  try {
    await api.post(`/classes/${roomCode.value}/join-live`, { password: livePassword.value, student_name: studentName.value })
    joined.value = true
    livePassword.value = ''
    connectSocket()
  } catch (err) {
    joinError.value = err.response?.data?.error || 'Live darsga kirish bo‘lmadi.'
  }
}

function createPeerConnection(targetId) {
  const pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] })
  peerConnections[targetId] = pc
  pc.onicecandidate = (event) => {
    if (event.candidate) socket.emit('webrtc-ice-candidate', { target: targetId, candidate: event.candidate })
  }
  pc.ontrack = (event) => {
    if (videoRef.value) videoRef.value.srcObject = event.streams[0]
    statusText.value = 'Live dars ulanib bo‘ldi. Endi darsni ko‘rishingiz mumkin.'
  }
  return pc
}

function connectSocket() {
  socket = io(socketURL, { transports: ['websocket', 'polling'], withCredentials: true })
  socket.on('connect', () => {
    socket.emit('join-room', { room: roomCode.value, role: 'student', name: studentName.value })
    statusText.value = `${studentName.value}, siz dars xonasiga qo‘shildingiz. Ustozga xabar yuborildi.`
  })
  socket.on('webrtc-offer', async ({ offer, from }) => {
    const pc = createPeerConnection(from)
    await pc.setRemoteDescription(new RTCSessionDescription(offer))
    const answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    socket.emit('webrtc-answer', { target: from, answer })
  })
  socket.on('webrtc-ice-candidate', async ({ candidate, from }) => {
    const pc = peerConnections[from]
    if (pc && candidate) {
      try { await pc.addIceCandidate(new RTCIceCandidate(candidate)) } catch (e) { console.error(e) }
    }
  })
  socket.on('teacher-disconnected', ({ message }) => {
    statusText.value = message
  })
  socket.on('kicked', ({ message }) => {
    alert(message)
    router.push('/')
  })
}

onMounted(load)
onBeforeUnmount(() => socket?.disconnect())
</script>

<template>
  <section v-if="klass" class="grid-2 gap-lg">
    <div class="card live-stage">
      <div class="video-top">
        <div>
          <h1>{{ klass.title }}</h1>
          <p>{{ klass.description || 'Tavsif kiritilmagan' }}</p>
        </div>
        <span :class="['badge', klass.is_live ? 'live' : 'offline']">{{ klass.is_live ? 'LIVE' : 'OFFLINE' }}</span>
      </div>
      <div v-if="!joined && canJoin" class="stack live-join-panel" style="margin-bottom:16px">
        <div class="flash success">🔴 Live dars yoqildi. Qo‘shilish tugmasini bosing.</div>
        <button class="btn btn-warning" @click="joinLive">Live darsga qo‘shilish</button>
        <details class="muted small-text"><summary>Guest kirish uchun parol</summary><input v-model="livePassword" type="password" placeholder="Live paroli" /></details>
        <div v-if="joinError" class="flash error">{{ joinError }}</div>
      </div>
      <div v-else-if="!joined" class="flash error">Live dars hali yoqilmagan. Ustoz yoqqandan keyin qo‘shilish tugmasi chiqadi.</div>
      <video v-show="joined" ref="videoRef" autoplay playsinline controlsList="nodownload noremoteplayback" disablePictureInPicture @contextmenu.prevent></video>
      <p class="muted">{{ joined ? statusText : "Live yoqilganda shu yerdan darsga qo‘shilasiz." }}</p>
      <RouterLink v-if="latestTest" class="btn" :to="`/test/${latestTest.id}?student_name=${encodeURIComponent(studentName)}`">Darsdan keyin test ishlash</RouterLink>
    </div>
    <div class="card glass">
      <h2>Dars ma'lumoti</h2>
      <div class="info-list">
        <div><strong>O‘quvchi:</strong> {{ studentName }}</div>
                <div><strong>Dars turi:</strong> jonli video dars</div>
        <div><strong>Ustoz holati:</strong> o‘quvchi qo‘shilganini ko‘rib turadi</div>
      </div>
    </div>
  </section>
</template>
