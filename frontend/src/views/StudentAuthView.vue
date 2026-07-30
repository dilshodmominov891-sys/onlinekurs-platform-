<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib'
import { markRuntimeSession, saveSession } from '../sessionStore'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const error = ref('')
const loading = ref(false)
const lang = ref(localStorage.getItem('edulive_lang_auth') || 'uz')
const langMenuOpen = ref(false)

const langOptions = [
  { code: 'uz', short: 'UZ', label: 'O‘zbek' },
  { code: 'ru', short: 'RU', label: 'Русский' },
]
const text = {
  uz: {
    title: 'Tizimga kirish',
    subtitle: 'Admin, ustoz va o‘quvchi o‘z login va paroli bilan kiradi.',
    login: 'Login',
    password: 'Parol',
    button: 'Kirish',
    error: 'Login yoki parol xato.',
  },
  ru: {
    title: 'Вход в систему',
    subtitle: 'Администратор, учитель и ученик входят со своим логином и паролем.',
    login: 'Логин',
    password: 'Пароль',
    button: 'Войти',
    error: 'Неверный логин или пароль.',
  },
}
function tr(key) { return text[lang.value]?.[key] || text.uz[key] || key }
const currentLang = computed(() => langOptions.find(item => item.code === lang.value) || langOptions[0])

function setLang(next) {
  lang.value = next
  localStorage.setItem('edulive_lang_auth', next)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: next }))
}
function toggleLang() { langMenuOpen.value = !langMenuOpen.value }
function handleDocumentClick(event) {
  if (!event.target.closest('.lang-picker')) langMenuOpen.value = false
}
async function submitLogin() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/access/login', form)
    saveSession(data)
    markRuntimeSession()
    form.password = ''
    if (data.role === 'admin') await router.replace('/admin')
    else if (data.role === 'teacher') await router.replace('/teacher')
    else await router.replace('/home')
  } catch (err) {
    error.value = err.response?.data?.error || tr('error')
  } finally {
    loading.value = false
  }
}

onMounted(() => document.addEventListener('click', handleDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocumentClick))
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <div class="login-card-top">
        <div class="login-brand">EduLive Pro</div>
        <div class="lang-picker auth-lang-picker">
          <button class="lang-toggle simple-lang-toggle" type="button" @click="toggleLang">
            <span>{{ currentLang.label }}</span>
            <span class="lang-arrow">⌄</span>
          </button>
          <div v-if="langMenuOpen" class="lang-menu simple-lang-menu">
            <button
              v-for="item in langOptions"
              :key="item.code"
              type="button"
              class="lang-option simple-lang-option"
              :class="{ active: item.code === lang }"
              @click="setLang(item.code)"
            >{{ item.label }}</button>
          </div>
        </div>
      </div>

      <h1>{{ tr('title') }}</h1>
      <p class="muted">{{ tr('subtitle') }}</p>

      <form class="login-form" autocomplete="off" @submit.prevent="submitLogin">
        <label>
          <span>{{ tr('login') }}</span>
          <input v-model.trim="form.username" autocomplete="username" autocapitalize="none" spellcheck="false" required />
        </label>
        <label>
          <span>{{ tr('password') }}</span>
          <input v-model="form.password" type="password" autocomplete="current-password" required />
        </label>
        <button class="btn login-submit" :disabled="loading">{{ loading ? '...' : tr('button') }}</button>
      </form>

      <div v-if="error" class="flash error">{{ error }}</div>
    </section>
  </main>
</template>
