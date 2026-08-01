<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../lib'

const teachers = ref([])
const message = ref('')
const error = ref('')
const form = reactive({ full_name: '', username: '', password: '' })

async function load(){
  error.value = ''
  try{
    const { data } = await api.get('/admin/teachers')
    teachers.value = data.teachers || []
  }catch(err){
    error.value = err.response?.data?.error || 'Ustozlar ro‘yxati yuklanmadi.'
  }
}
async function createTeacher(){
  message.value=''; error.value=''
  try{
    const { data } = await api.post('/admin/teachers', form)
    message.value = data.message || 'Ustoz yaratildi.'
    form.full_name=''; form.username=''; form.password=''
    await load()
  }catch(err){ error.value = err.response?.data?.error || 'Ustoz yaratilmadi.' }
}
async function deleteTeacher(item){
  if(!confirm(`${item.full_name || item.username} o‘chirilsinmi?`)) return
  message.value=''; error.value=''
  try{
    const { data } = await api.delete(`/admin/teachers/${item.id}`)
    message.value = data.message || 'Ustoz o‘chirildi.'
    await load()
  }catch(err){ error.value = err.response?.data?.error || 'Ustoz o‘chirilmadi.' }
}
onMounted(load)
</script>

<template>
  <section class="section admin-subpage-grid">
    <div class="card glass animated-card admin-create-teacher-card">
      <div class="section-head">
        <div>
          <span class="pill">Admin only</span>
          <h1>Ustoz yaratish</h1>
          <p class="muted">Bu bo‘lim faqat admin panelida ko‘rinadi. Yangi ustoz login va parol shu yerdan ochiladi.</p>
        </div>
      </div>
      <div class="stack teacher-create-form">
        <input v-model="form.full_name" placeholder="Ustoz ism familiya" autocomplete="off" />
        <input v-model="form.username" placeholder="Ustoz login" autocomplete="off" />
        <input v-model="form.password" type="password" placeholder="Ustoz parol" autocomplete="new-password" />
        <button class="btn" @click="createTeacher">Ustozni saqlash</button>
      </div>
      <div v-if="message" class="flash success">{{ message }}</div>
      <div v-if="error" class="flash error">{{ error }}</div>
    </div>

    <div class="card glass animated-card">
      <div class="section-head"><div><h2>Yaratilgan ustozlar</h2><p class="muted">Admin yaratgan ustozlarni shu yerdan o‘chiradi.</p></div><span class="pill">{{ teachers.length }} ta</span></div>
      <div class="results-list">
        <div v-for="item in teachers" :key="item.id" class="result-item teacher-row hover-card">
          <div>
            <strong>{{ item.full_name }}</strong>
            <span>Login: {{ item.username }}</span>
          </div>
          <button class="btn btn-danger btn-sm" @click="deleteTeacher(item)">O‘chirish</button>
        </div>
        <p v-if="!teachers.length" class="muted">Hali ustoz yaratilmagan.</p>
      </div>
    </div>
  </section>
</template>
