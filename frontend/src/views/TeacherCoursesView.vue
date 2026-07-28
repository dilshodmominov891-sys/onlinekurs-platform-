<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../lib'

const form = reactive({ title: '', track: 'frontend', technology: '', description: '', duration: '', level: '1-bosqich', price: '' })
const courses = ref([])
const error = ref('')
const success = ref('')

async function load() {
  try {
    const { data } = await api.get('/admin/courses')
    courses.value = data.courses || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Kurslar yuklanmadi.'
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/admin/courses/create', form)
    success.value = data.message || 'Kurs yaratildi.'
    form.title = ''
    form.track = 'frontend'
    form.technology = ''
    form.description = ''
    form.duration = ''
    form.level = '1-bosqich'
    form.price = ''
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'Kurs yaratilmadi.'
  }
}

onMounted(load)
</script>

<template>
  <section class="section grid-2 gap-lg">
    <div class="card glass">
      <div class="section-head"><div><h2>Kurs yaratish</h2><p class="muted">Ustoz shu bo‘limdan yangi kurs qo‘shadi.</p></div><span class="pill">Teacher panel</span></div>
      <div class="stack">
        <input v-model="form.title" placeholder="Kurs nomi" />
        <div class="grid-2">
          <select v-model="form.track"><option value="frontend">Frontend</option><option value="backend">Backend</option></select>
          <select v-model="form.level"><option>1-bosqich</option><option>2-bosqich</option><option>3-bosqich</option></select>
        </div>
        <input v-model="form.technology" placeholder="Texnologiya (masalan HTML & CSS yoki Django)" />
        <input v-model="form.duration" placeholder="Davomiyligi (masalan 6 hafta)" />
        <input v-model="form.price" placeholder="Narxi" />
        <textarea v-model="form.description" placeholder="Kurs haqida qisqacha ma’lumot"></textarea>
        <button class="btn" @click="submit">Kursni saqlash</button>
      </div>
      <div v-if="error" class="flash error">{{ error }}</div>
      <div v-if="success" class="flash success">{{ success }}</div>
    </div>

    <div class="card glass">
      <div class="section-head"><div><h2>Mavjud kurslar</h2><p class="muted">Yaratilgan kurslar ro‘yxati</p></div><span class="pill">{{ courses.length }} ta</span></div>
      <div class="results-list">
        <div v-for="course in courses" :key="course.id" class="result-item">
          <div>
            <strong>{{ course.title }}</strong>
            <div class="muted small-text">{{ course.track }} · {{ course.level }} · {{ course.technology }}</div>
          </div>
          <div class="pill">{{ course.price || 0 }} so‘m</div>
        </div>
      </div>
    </div>
  </section>
</template>
