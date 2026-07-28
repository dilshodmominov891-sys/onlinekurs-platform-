<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../lib'

const form = reactive({ full_name: '', username: '', password: '' })
const teachers = ref([])
const error = ref('')
const success = ref('')

async function load() {
  try {
    const { data } = await api.get('/admin/teachers')
    teachers.value = data.teachers || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Ustozlar yuklanmadi.'
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/admin/teachers', form)
    success.value = data.message || 'Ustoz yaratildi.'
    form.full_name = ''
    form.username = ''
    form.password = ''
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'Ustoz yaratilmadi.'
  }
}

onMounted(load)
</script>

<template>
  <section class="section grid-2 gap-lg">
    <div class="card glass">
      <div class="section-head"><div><h2>Ustoz yaratish</h2><p class="muted">Bir nechta o‘qituvchi login yaratish mumkin.</p></div><span class="pill">Faqat bosh ustoz</span></div>
      <div class="stack">
        <input v-model="form.full_name" placeholder="Ustoz ismi va familiyasi" />
        <input v-model="form.username" placeholder="Login" />
        <input v-model="form.password" type="password" placeholder="Parol" />
        <button class="btn" @click="submit">Ustozni saqlash</button>
      </div>
      <div v-if="error" class="flash error">{{ error }}</div>
      <div v-if="success" class="flash success">{{ success }}</div>
    </div>

    <div class="card glass">
      <div class="section-head"><div><h2>Ustozlar ro‘yxati</h2><p class="muted">Saytdagi yaratilgan o‘qituvchilar</p></div><span class="pill">{{ teachers.length }} ta</span></div>
      <div class="results-list">
        <div v-for="item in teachers" :key="item.id" class="result-item">
          <div>
            <strong>{{ item.full_name }}</strong>
            <div class="muted small-text">login: {{ item.username }}</div>
          </div>
          <div class="pill">Ustoz</div>
        </div>
      </div>
    </div>
  </section>
</template>
