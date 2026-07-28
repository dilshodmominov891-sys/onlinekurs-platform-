<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib'
import { saveSession } from '../sessionStore'

const form = reactive({ username: '', password: '' })
const error = ref('')
const router = useRouter()

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
</script>

<template>
  <div class="center-box">
    <div class="card glass form-card">
      <h1>Admin paneliga kirish</h1>
      <p class="muted">Admin login va parol bilan kiriladi.</p>
      <div class="stack" autocomplete="off">
        <input v-model="form.username" placeholder="Login" autocomplete="off" autocapitalize="none" spellcheck="false" name="admin_login_empty" @keyup.enter="login" />
        <input v-model="form.password" type="password" placeholder="Parol" autocomplete="new-password" autocapitalize="none" spellcheck="false" name="admin_pass_empty" @keyup.enter="login" />
        <button class="btn" @click="login">Admin paneliga kirish</button>
        <div v-if="error" class="flash error">{{ error }}</div>
      </div>
    </div>
  </div>
</template>
