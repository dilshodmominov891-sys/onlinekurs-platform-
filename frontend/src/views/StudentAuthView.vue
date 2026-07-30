<script setup>
import { computed, reactive, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib'
import { saveSession } from '../sessionStore'

const router = useRouter()
const reg = reactive({
  first_name: '',
  last_name: '',
  phone: '',
  email: '',
  username: '',
  password: '',
  password_confirm: '',
})
const loginForm = reactive({ username: '', password: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)
const activeTab = ref('register')

const lang = ref(localStorage.getItem('edulive_lang_auth') || 'uz')
const langMenuOpen = ref(false)
const langOptions = [
  { code:'uz', flag:'🇺🇿', short:'UZ', label:'O‘zbek' },
  { code:'ru', flag:'🇷🇺', short:'RU', label:'Русский' },
  { code:'en', flag:'🇬🇧', short:'EN', label:'English' },
]
const dict = {
  uz:{
    register:'Registratsiya', loginTab:'Login',
    regTitle:'Saytga kirish uchun ro‘yxatdan o‘ting', loginTitle:'Tizimga kirish',
    regSub:'Ma’lumotlarni kiriting va o‘zingiz uchun login hamda parol yarating. Registratsiyadan keyin login orqali kirasiz.',
    loginSub:'Login va parolingizni kiriting. Tizim sizni o‘quvchi, ustoz yoki admin paneliga avtomatik yo‘naltiradi.',
    name:'Ism', last:'Familiya', phone:'Telefon: 881649969 yoki +998881649969', email:'Email',
    newLogin:'Yangi login yarating', newPass:'Yangi parol yarating', confirmPass:'Parolni qayta kiriting',
    login:'Login', pass:'Parol', regBtn:'Registratsiya qilish', loginBtn:'Kirish',
    passMismatch:'Parollar bir xil emas.'
  },
  ru:{
    register:'Регистрация', loginTab:'Вход',
    regTitle:'Зарегистрируйтесь для входа на сайт', loginTitle:'Вход в систему',
    regSub:'Введите данные и создайте собственный логин и пароль. После регистрации войдите через форму входа.',
    loginSub:'Введите логин и пароль. Система автоматически откроет панель ученика, учителя или администратора.',
    name:'Имя', last:'Фамилия', phone:'Телефон: 881649969 или +998881649969', email:'Email',
    newLogin:'Создайте новый логин', newPass:'Создайте новый пароль', confirmPass:'Повторите пароль',
    login:'Логин', pass:'Пароль', regBtn:'Зарегистрироваться', loginBtn:'Войти',
    passMismatch:'Пароли не совпадают.'
  },
  en:{
    register:'Registration', loginTab:'Login',
    regTitle:'Register to enter the platform', loginTitle:'Sign in',
    regSub:'Enter your details and create your own username and password. After registration, sign in through the login form.',
    loginSub:'Enter your username and password. The system will automatically open the student, teacher, or admin panel.',
    name:'First name', last:'Last name', phone:'Phone: 881649969 or +998881649969', email:'Email',
    newLogin:'Create a new username', newPass:'Create a new password', confirmPass:'Repeat password',
    login:'Username', pass:'Password', regBtn:'Register', loginBtn:'Login',
    passMismatch:'Passwords do not match.'
  }
}

function tr(key){ return dict[lang.value]?.[key] || dict.uz[key] || key }
const currentLang = computed(() => langOptions.find(item => item.code === lang.value) || langOptions[0])
const activeLabel = computed(() => activeTab.value === 'login' ? tr('loginTab') : tr('register'))
const activeTitle = computed(() => activeTab.value === 'login' ? tr('loginTitle') : tr('regTitle'))
const activeSubtitle = computed(() => activeTab.value === 'login' ? tr('loginSub') : tr('regSub'))

function setTab(tab) {
  activeTab.value = tab
  error.value = ''
  success.value = ''
}
function setLang(next){
  lang.value = next
  localStorage.setItem('edulive_lang_auth', next)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change', { detail: next }))
}
function toggleLang(){ langMenuOpen.value = !langMenuOpen.value }
function handleDocumentClick(event){
  if (!event.target.closest('.lang-picker')) langMenuOpen.value = false
}

async function submitRegister() {
  error.value = ''
  success.value = ''
  if (reg.password !== reg.password_confirm) {
    error.value = tr('passMismatch')
    return
  }
  loading.value = true
  try {
    const payload = {
      first_name: reg.first_name,
      last_name: reg.last_name,
      phone: reg.phone,
      email: reg.email,
      username: reg.username,
      password: reg.password,
    }
    const { data } = await api.post('/student/register', payload)
    loginForm.username = reg.username
    loginForm.password = ''
    Object.keys(reg).forEach((key) => { reg[key] = '' })
    activeTab.value = 'login'
    success.value = data.message || 'Registratsiya muvaffaqiyatli. Endi login va parol bilan kiring.'
  } catch (err) {
    error.value = err.response?.data?.error || 'Registratsiya bo‘lmadi.'
  } finally {
    loading.value = false
  }
}

async function submitLogin() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/access/login', loginForm)
    saveSession(data)
    loginForm.password = ''
    if (data?.role === 'admin') {
      await router.replace('/admin')
      return
    }
    if (data?.role === 'teacher') {
      await router.replace('/teacher')
      return
    }
    await router.replace('/home')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login yoki parol xato.'
  } finally {
    loading.value = false
  }
}

onMounted(() => document.addEventListener('click', handleDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocumentClick))
</script>

<template>
  <div class="center-box auth-page-wrap auth-page-compact">
    <div class="card glass form-card auth-card-wide auth-card-tall elegant-auth-card auth-simple-card auth-unified-card">
      <div class="auth-topline auth-topline-language">
        <span class="pill">{{ activeLabel }}</span>
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

      <h1 class="auth-title">{{ activeTitle }}</h1>
      <p class="muted auth-subtitle">{{ activeSubtitle }}</p>

      <div class="track-switcher auth-switch auth-switch-two">
        <button class="track-btn" :class="{ active: activeTab === 'register' }" @click="setTab('register')">{{ tr('register') }}</button>
        <button class="track-btn" :class="{ active: activeTab === 'login' }" @click="setTab('login')">{{ tr('loginTab') }}</button>
      </div>

      <form v-if="activeTab === 'register'" class="stack auth-form-stack" autocomplete="off" @submit.prevent="submitRegister">
        <div class="auth-name-grid">
          <input v-model="reg.first_name" :placeholder="tr('name')" autocomplete="given-name" required />
          <input v-model="reg.last_name" :placeholder="tr('last')" autocomplete="family-name" required />
        </div>
        <input v-model="reg.phone" :placeholder="tr('phone')" inputmode="tel" autocomplete="tel" required />
        <input v-model="reg.email" type="email" :placeholder="tr('email')" autocomplete="email" required />
        <input v-model.trim="reg.username" :placeholder="tr('newLogin')" autocomplete="username" autocapitalize="none" spellcheck="false" required />
        <div class="auth-name-grid">
          <input v-model="reg.password" type="password" :placeholder="tr('newPass')" autocomplete="new-password" minlength="6" required />
          <input v-model="reg.password_confirm" type="password" :placeholder="tr('confirmPass')" autocomplete="new-password" minlength="6" required />
        </div>
        <button class="btn auth-submit-btn" :disabled="loading">{{ loading ? '...' : tr('regBtn') }}</button>
      </form>

      <form v-else class="stack auth-form-stack" autocomplete="off" @submit.prevent="submitLogin">
        <input v-model.trim="loginForm.username" :placeholder="tr('login')" autocomplete="username" autocapitalize="none" spellcheck="false" required />
        <input v-model="loginForm.password" type="password" :placeholder="tr('pass')" autocomplete="current-password" required />
        <button class="btn auth-submit-btn" :disabled="loading">{{ loading ? '...' : tr('loginBtn') }}</button>
      </form>

      <div v-if="error" class="flash error">{{ error }}</div>
      <div v-if="success" class="flash success">{{ success }}</div>
    </div>
  </div>
</template>
