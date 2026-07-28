<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '../lib'

const dictionary = {
  uz: {
    pill: 'AI yordamchi',
    title: 'Savollar',
    desc: 'Sayt haqida istalgan savolni yozing. Enter yoki yuqoriga qaragan tugma orqali yuboriladi.',
    hello: 'Salom! EduLive Pro platformasi haqida savolingizni yozing. Kurslar, live dars, testlar yoki foydalanish tartibini tushuntirib beraman.',
    placeholder: 'Savolingizni yozing...',
    typing: 'Javob yozilmoqda...',
    empty: 'Javob topilmadi.',
    fallbackError: 'AI javob berishda vaqtinchalik muammo. Backendda OPENAI_API_KEY to‘g‘ri qo‘yilganini tekshiring.'
  },
  ru: {
    pill: 'AI помощник',
    title: 'Вопросы',
    desc: 'Напишите любой вопрос о сайте. Отправляйте через Enter или кнопку со стрелкой вверх.',
    hello: 'Здравствуйте! Напишите вопрос о платформе EduLive Pro. Я объясню курсы, live-уроки, тесты или порядок использования.',
    placeholder: 'Напишите вопрос...',
    typing: 'Ответ пишется...',
    empty: 'Ответ не найден.',
    fallbackError: 'Временная проблема с AI. Проверьте OPENAI_API_KEY в backend/.env.'
  },
  en: {
    pill: 'AI assistant',
    title: 'Questions',
    desc: 'Write any question about the site. Send with Enter or the up-arrow button.',
    hello: 'Hello! Ask a question about EduLive Pro. I can explain courses, live classes, tests, or how to use the platform.',
    placeholder: 'Write your question...',
    typing: 'Writing answer...',
    empty: 'No answer found.',
    fallbackError: 'Temporary AI problem. Check OPENAI_API_KEY in backend/.env.'
  }
}

function getCurrentLang(){ return localStorage.getItem('edulive_lang_student') || localStorage.getItem('edulive_lang_auth') || 'uz' }
const lang = ref(getCurrentLang())
const copy = computed(() => dictionary[lang.value] || dictionary.uz)
const messages = ref([{ role:'assistant', text: copy.value.hello }])
const question = ref('')
const loading = ref(false)
const box = ref(null)

function updateLang(event){
  lang.value = event?.detail || getCurrentLang()
  if (messages.value.length && messages.value[0].role === 'assistant') messages.value[0].text = copy.value.hello
}

async function send(){
  const text = question.value.trim()
  if(!text || loading.value) return
  messages.value.push({ role:'user', text })
  question.value=''
  loading.value = true
  await nextTick(); box.value?.scrollTo({ top: box.value.scrollHeight, behavior:'smooth' })
  try{
    const { data } = await api.post('/student/ask', { question: text, lang: lang.value, history: messages.value.slice(-6) })
    messages.value.push({ role:'assistant', text: data.answer || copy.value.empty })
  }catch(err){
    messages.value.push({ role:'assistant', text: err.response?.data?.error || copy.value.fallbackError })
  }finally{
    loading.value = false
    await nextTick(); box.value?.scrollTo({ top: box.value.scrollHeight, behavior:'smooth' })
  }
}

onMounted(() => window.addEventListener('edulive-lang-change', updateLang))
onBeforeUnmount(() => window.removeEventListener('edulive-lang-change', updateLang))
</script>

<template>
  <section class="section questions-page questions-fit-page">
    <div class="card glass ai-chat-card animated-card questions-fit-card">
      <div class="section-head questions-head">
        <div>
          <span class="pill">{{ copy.pill }}</span>
          <h1>{{ copy.title }}</h1>
          <p class="muted">{{ copy.desc }}</p>
        </div>
      </div>
      <div ref="box" class="chat-window questions-chat-window">
        <div v-for="(msg, i) in messages" :key="i" class="chat-row" :class="msg.role">
          <div class="chat-bubble">{{ msg.text }}</div>
        </div>
        <div v-if="loading" class="chat-row assistant"><div class="chat-bubble typing">{{ copy.typing }}</div></div>
      </div>
      <div class="chat-input-row questions-input-row">
        <input v-model="question" @keyup.enter="send" :placeholder="copy.placeholder" autocomplete="off" />
        <button class="send-btn" @click="send">↑</button>
      </div>
    </div>
  </section>
</template>
