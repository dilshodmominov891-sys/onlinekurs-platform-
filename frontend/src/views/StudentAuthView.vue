<script setup>
import { computed, reactive, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib'
import { saveSession } from '../sessionStore'
import brandLogo from '../assets/brand-logo.svg'
import authHero from '../assets/auth-hero.svg'

const router = useRouter()
const reg = reactive({ first_name: '', last_name: '', phone: '', email: '' })
const login = reactive({ username: '', password: '' })
const error = ref('')
const success = ref('')
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
    reg:'Registratsiya', login:'Ustoz login',
    regTitle:'Saytga kirish uchun ro‘yxatdan o‘ting', loginTitle:'Ustoz paneliga kirish',
    regSub:'Ma’lumotlarni to‘liq kiriting. Registratsiyadan keyin siz o‘quvchi sifatida saytga kirasiz.',
    loginSub:'Admin yoki ustoz shu bo‘limdan login va parol bilan kiradi.',
    name:'Ism', last:'Familiya', phone:'Telefon: 881649969 yoki +998881649969', email:'Email',
    regBtn:'Registratsiya qilish', loginPh:'Ustoz yoki admin login', pass:'Parol', loginBtn:'Ustoz paneliga kirish',
    brandTitle:'EduLive Pro', brandSub:'Online kurs platformasi',
    feature1:'Online kurslar va dars yozuvlari', feature2:'Frontend va backend test tizimi', feature3:'Kuchli admin va ustoz boshqaruvi'
  },
  ru:{
    reg:'Регистрация', login:'Вход учителя',
    regTitle:'Зарегистрируйтесь для входа на сайт', loginTitle:'Вход в панель учителя',
    regSub:'Введите данные полностью. После регистрации вы войдёте как ученик.',
    loginSub:'Учитель или админ входит здесь по логину и паролю.',
    name:'Имя', last:'Фамилия', phone:'Телефон: 881649969 или +998881649969', email:'Email',
    regBtn:'Зарегистрироваться', loginPh:'Логин учителя или админа', pass:'Пароль', loginBtn:'Войти в панель учителя',
    brandTitle:'EduLive Pro', brandSub:'Платформа онлайн-курсов',
    feature1:'Онлайн-курсы и записи уроков', feature2:'Система тестов по frontend и backend', feature3:'Удобная админ и учитель панель'
  },
  en:{
    reg:'Registration', login:'Teacher login',
    regTitle:'Register to enter the platform', loginTitle:'Teacher panel login',
    regSub:'Fill in your details completely. After registration you will enter as a student.',
    loginSub:'Teacher or admin can log in here with username and password.',
    name:'First name', last:'Last name', phone:'Phone: 881649969 or +998881649969', email:'Email',
    regBtn:'Register', loginPh:'Teacher or admin login', pass:'Password', loginBtn:'Enter teacher panel',
    brandTitle:'EduLive Pro', brandSub:'Online course platform',
    feature1:'Online courses and lesson recordings', feature2:'Frontend and backend test system', feature3:'Strong admin and teacher control'
  }
}
function tr(k){return dict[lang.value]?.[k] || dict.uz[k] || k}
function setLang(next){
  lang.value = next
  localStorage.setItem('edulive_lang_auth', lang.value)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change',{detail:lang.value}))
}
function toggleLang(){ langMenuOpen.value = !langMenuOpen.value }
const currentLang = computed(() => langOptions.find(i => i.code === lang.value) || langOptions[0])
function handleDocumentClick(event){
  if (!event.target.closest('.lang-picker')) langMenuOpen.value = false
}

async function submitRegister() {
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/student/register', reg)
    saveSession({ role: 'student', student: data.student })
    success.value = data.message || 'Registratsiya bo‘ldi.'
    reg.first_name = ''
    reg.last_name = ''
    reg.phone = ''
    reg.email = ''
    await router.replace('/home')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registratsiya bo‘lmadi.'
  }
}

async function submitTeacherLogin() {
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/access/login', login)
    saveSession(data)
    const role = data?.role || ''
    login.username = ''
    login.password = ''
    if (role === 'admin') {
      await router.replace('/admin')
      return
    }
    if (role === 'teacher') {
      await router.replace('/teacher')
      return
    }
    await router.replace('/home')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login bo‘lmadi.'
  }
}

onMounted(() => document.addEventListener('click', handleDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocumentClick))
</script>

<template>
  <div class="center-box auth-page-wrap auth-page-compact">
    <div class="card glass auth-split-card elegant-auth-card">
      <div class="auth-visual-panel">
        <div class="auth-brand-row">
          <img :src="brandLogo" alt="EduLive Pro" class="auth-brand-logo" />
          <div>
            <div class="auth-brand-title">{{ tr('brandTitle') }}</div>
            <div class="auth-brand-sub">{{ tr('brandSub') }}</div>
          </div>
        </div>
        <img :src="authHero" alt="EduLive Pro visual" class="auth-hero-image" />
        <div class="auth-feature-list">
          <div class="auth-feature-pill">🎓 {{ tr('feature1') }}</div>
          <div class="auth-feature-pill">🧪 {{ tr('feature2') }}</div>
          <div class="auth-feature-pill">⚙️ {{ tr('feature3') }}</div>
        </div>
      </div>

      <div class="auth-form-panel">
        <div class="auth-topline auth-topline-language">
          <span class="pill">{{ activeTab === 'register' ? tr('reg') : tr('login') }}</span>
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

        <h1 class="auth-title" v-if="activeTab === 'register'">{{ tr('regTitle') }}</h1>
        <h1 class="auth-title" v-else>{{ tr('loginTitle') }}</h1>
        <p class="muted auth-subtitle" v-if="activeTab === 'register'">{{ tr('regSub') }}</p>
        <p class="muted auth-subtitle" v-else>{{ tr('loginSub') }}</p>

        <div class="track-switcher auth-switch auth-switch-equal">
          <button class="track-btn" :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">{{ tr('reg') }}</button>
          <button class="track-btn" :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">{{ tr('login') }}</button>
        </div>

        <div v-if="activeTab === 'register'" class="stack" autocomplete="off">
          <input v-model="reg.first_name" :placeholder="tr('name')" autocomplete="off" name="student_first_name_new" />
          <input v-model="reg.last_name" :placeholder="tr('last')" autocomplete="off" name="student_last_name_new" />
          <input v-model="reg.phone" :placeholder="tr('phone')" autocomplete="off" name="student_phone_new" />
          <input v-model="reg.email" :placeholder="tr('email')" autocomplete="off" name="student_email_new" />
          <button class="btn auth-submit-btn" @click="submitRegister">{{ tr('regBtn') }}</button>
        </div>

        <div v-else class="stack" autocomplete="off">
          <input v-model="login.username" :placeholder="tr('loginPh')" autocomplete="off" autocapitalize="none" spellcheck="false" name="edu_login_user_empty" />
          <input v-model="login.password" type="password" :placeholder="tr('pass')" autocomplete="new-password" autocapitalize="none" spellcheck="false" name="edu_login_pass_empty" />
          <button class="btn btn-secondary auth-submit-btn" @click="submitTeacherLogin">{{ tr('loginBtn') }}</button>
        </div>

        <div v-if="error" class="flash error">{{ error }}</div>
        <div v-if="success" class="flash success">{{ success }}</div>
      </div>
    </div>
  </div>
</template>
