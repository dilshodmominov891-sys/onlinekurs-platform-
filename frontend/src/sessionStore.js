import { ref } from 'vue'

const STORAGE_KEY = 'edulive_session_v2'

export const sessionRole = ref('')
export const sessionUser = ref(null)

export function readSavedSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function saveSession(data = {}) {
  const payload = {
    role: data.role || '',
    student: data.student || null,
    teacher: data.teacher || null,
    saved_at: Date.now(),
  }
  sessionRole.value = payload.role
  sessionUser.value = payload.student || payload.teacher || null
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(payload)) } catch {}
  return payload
}

export function clearSession() {
  sessionRole.value = ''
  sessionUser.value = null
  try { localStorage.removeItem(STORAGE_KEY) } catch {}
}

export function hydrateSession() {
  const saved = readSavedSession()
  if (saved?.role) {
    sessionRole.value = saved.role
    sessionUser.value = saved.student || saved.teacher || null
  }
  return saved
}

hydrateSession()
