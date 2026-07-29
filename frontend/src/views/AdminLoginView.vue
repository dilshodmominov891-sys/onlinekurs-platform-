<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api } from '../lib'
import { saveSession, hydrateSession } from '../sessionStore'

const form = reactive({ username: '', password: '' })
const error = ref('')
const router = useRouter()
const lang = ref(localStorage.getItem('edulive_lang_auth') || 'uz')
const langMenuOpen = ref(false)
const langOptions = [
  { code:'uz', flag:'🇺🇿', short:'UZ', label:'O‘zbek' },
  { code:'ru', flag:'🇷🇺', short:'RU', label:'Русский' },
  { code:'en', flag:'🇬🇧', short:'EN', label:'English' },
]
const dict = {
  uz: { reg:'Registratsiya', title:'Admin paneliga kirish', sub:'Admin login va parol bilan kiriladi.', user:'Login', pass:'Parol', btn:'Admin paneliga kirish' },
  ru: { reg:'Регистрация', title:'Вход в админ панель', sub:'Вход по логину и паролю администратора.', user:'Логин', pass:'Пароль', btn:'Войти в админ панель' },
  en: { reg:'Registration', title:'Admin panel login', sub:'Log in with admin username and password.', user:'Login', pass:'Password', btn:'Enter admin panel' },
}
function tr(k){ return dict[lang.value]?.[k] || dict.uz[k] || k }
function setLang(next){
  lang.value = next
  localStorage.setItem('edulive_lang_auth', next)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: next }))
}
function toggleLang(){ langMenuOpen.value = !langMenuOpen.value }
const currentLang = computed(() => langOptions.find(i => i.code === lang.value) || langOptions[0])
function handleDocumentClick(event){
  if (!event.target.closest('.lang-picker')) langMenuOpen.value = false
}

async function login() {
  error.value = ''
  try {
    const { data } = await api.post('/access/login', { username: form.username, password: form.password })
    saveSession(data)
    form.password = ''
    await router.replace('/admin')
  } catch (err) {
    error.value = err.response?.data?.error || 'Backend ishlamayapti yoki login/parol xato.'
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  const saved = hydrateSession()
  if (saved?.role === 'admin') router.replace('/admin')
})
onBeforeUnmount(() => document.removeEventListener('click', handleDocumentClick))
</script>

<template>
  <div class="center-box auth-page-wrap auth-page-compact">
    <div class="card glass form-card auth-card-wide elegant-auth-card auth-simple-card admin-login-card-clean">
      <div class="auth-topline auth-topline-language">
        <RouterLink class="pill" to="/auth">{{ tr('reg') }}</RouterLink>
        <div class="lang-picker auth-lang-picker">
          <button class="lang-toggle lang-sticker flag-style-toggle" type="button" @click="toggleLang">
            <span class="selected-lang">{{ currentLang.short }}</span>
            <span class="lang-arrow">⌄</span>
          </button>
          <div v-if="langMenuOpen" class="lang-menu auth-lang-menu">
            <button v-for="item in langOptions" :key="item.code" type="button" class="lang-option" :class="{active:item.code===lang}" @click="setLang(item.code)">
              <span>{{ item.flag }}</span><strong>{{ item.short }}</strong><small>{{ item.label }}</small>
            </button>
          </div>
        </div>
      </div>

      <h1 class="auth-title">{{ tr('title') }}</h1>
      <p class="muted auth-subtitle">{{ tr('sub') }}</p>
      <div class="stack" autocomplete="off">
        <input v-model="form.username" :placeholder="tr('user')" autocomplete="off" autocapitalize="none" spellcheck="false" name="admin_login_empty" @keyup.enter="login" />
        <input v-model="form.password" type="password" :placeholder="tr('pass')" autocomplete="new-password" autocapitalize="none" spellcheck="false" name="admin_pass_empty" @keyup.enter="login" />
        <button class="btn auth-submit-btn" @click="login">{{ tr('btn') }}</button>
        <div v-if="error" class="flash error">{{ error }}</div>
      </div>
    </div>
  </div>
</template>
