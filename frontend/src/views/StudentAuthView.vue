<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib'
import { saveSession } from '../sessionStore'

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
  uz:{reg:'Registratsiya', login:'Ustoz login', regTitle:'Saytga kirish uchun ro‘yxatdan o‘ting', loginTitle:'Ustoz paneliga kirish', regSub:'Ism, familiya, telefon va email to‘liq bo‘lishi kerak. Registratsiyadan keyin siz o‘quvchi sifatida saytga kirasiz.', loginSub:'Ustoz yoki admin login va parol bilan kiradi. Admin yoki ustoz login va parol bilan shu yerdan kiradi.', name:'Ism', last:'Familiya', phone:'Telefon: 881649969 yoki +998881649969', email:'Email', regBtn:'Registratsiya qilish', loginPh:'Ustoz yoki admin login', pass:'Parol', loginBtn:'Ustoz paneliga kirish'},
  ru:{reg:'Регистрация', login:'Вход учителя', regTitle:'Зарегистрируйтесь для входа на сайт', loginTitle:'Вход в панель учителя', regSub:'Введите имя, фамилию, телефон и email. После регистрации вы войдёте как ученик.', loginSub:'Учитель или админ входит по логину и паролю.', name:'Имя', last:'Фамилия', phone:'Телефон: 881649969 или +998881649969', email:'Email', regBtn:'Зарегистрироваться', loginPh:'Логин учителя или админа', pass:'Пароль', loginBtn:'Войти в панель учителя'},
  en:{reg:'Registration', login:'Teacher login', regTitle:'Register to enter the platform', loginTitle:'Teacher panel login', regSub:'Enter your first name, last name, phone and email. After registration you will enter as a student.', loginSub:'Teacher or admin can log in here with username and password.', name:'First name', last:'Last name', phone:'Phone: 881649969 or +998881649969', email:'Email', regBtn:'Register', loginPh:'Teacher or admin login', pass:'Password', loginBtn:'Enter teacher panel'}
}
function tr(k){return dict[lang.value]?.[k] || dict.uz[k] || k}
function setLang(next){
  lang.value = next
  localStorage.setItem('edulive_lang_auth', lang.value)
  langMenuOpen.value = false
  window.dispatchEvent(new CustomEvent('edulive-lang-change',{detail:lang.value}))
}
function cycleLang(){ langMenuOpen.value = !langMenuOpen.value }
function cycleNextLang(){
  const list = ['uz','ru','en']
  const next = list[(list.indexOf(lang.value)+1)%list.length]
  setLang(next)
}
const currentLang = computed(() => langOptions.find(i => i.code === lang.value) || langOptions[0])


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
</script>

<template>
  <div class="center-box auth-page-wrap">
    <div class="card glass form-card auth-card-wide auth-card-tall elegant-auth-card">
      <div class="auth-topline auth-topline-language">
        <span class="pill">{{ activeTab === 'register' ? tr('reg') : tr('login') }}</span>
        <div class="lang-picker auth-lang-picker">
          <button class="lang-toggle lang-sticker flag-style-toggle" type="button" @click="cycleLang" @dblclick.stop.prevent="cycleNextLang">
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

      <h1 v-if="activeTab === 'register'">{{ tr('regTitle') }}</h1>
      <h1 v-else>{{ tr('loginTitle') }}</h1>
      <p class="muted auth-subtitle" v-if="activeTab === 'register'">{{ tr('regSub') }}</p>
      <p class="muted auth-subtitle" v-else>{{ tr('loginSub') }}</p>

      <div class="track-switcher auth-switch">
        <button class="track-btn" :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">{{ tr('reg') }}</button>
        <button class="track-btn" :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">{{ tr('login') }}</button>
      </div>

      <div v-if="activeTab === 'register'" class="stack" autocomplete="off">
        <input v-model="reg.first_name" :placeholder="tr('name')" autocomplete="off" name="student_first_name_new" />
        <input v-model="reg.last_name" :placeholder="tr('last')" autocomplete="off" name="student_last_name_new" />
        <input v-model="reg.phone" :placeholder="tr('phone')" autocomplete="off" name="student_phone_new" />
        <input v-model="reg.email" :placeholder="tr('email')" autocomplete="off" name="student_email_new" />
        <button class="btn" @click="submitRegister">{{ tr('regBtn') }}</button>
      </div>

      <div v-else class="stack" autocomplete="off">
        <input v-model="login.username" :placeholder="tr('loginPh')" autocomplete="off" autocapitalize="none" spellcheck="false" name="edu_login_user_empty" />
        <input v-model="login.password" type="password" :placeholder="tr('pass')" autocomplete="new-password" autocapitalize="none" spellcheck="false" name="edu_login_pass_empty" />
        <button class="btn btn-secondary" @click="submitTeacherLogin">{{ tr('loginBtn') }}</button>
      </div>

      <div v-if="error" class="flash error">{{ error }}</div>
      <div v-if="success" class="flash success">{{ success }}</div>
    </div>
  </div>
</template>
