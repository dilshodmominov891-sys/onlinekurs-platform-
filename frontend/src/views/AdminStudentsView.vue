<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { api } from '../lib'

const students = ref([])
const courses = ref([])
const isAdmin = ref(false)
const loading = ref(false)
const error = ref('')
const message = ref('')
const editingId = ref(null)

const lang = ref(localStorage.getItem('edulive_lang_admin') || localStorage.getItem('edulive_lang_teacher') || 'uz')
const text = {
  uz: {
    title: 'O‘quvchilar', sub: 'Admin yoki ustoz o‘quvchiga login, parol va kerakli kurslarni beradi.',
    create: 'Yangi o‘quvchi yaratish', first: 'Ism', last: 'Familiya', phone: 'Telefon (ixtiyoriy)', email: 'Email (ixtiyoriy)',
    login: 'Login', password: 'Parol', courses: 'Kurslarni tanlang', save: 'O‘quvchi yaratish', list: 'O‘quvchilar ro‘yxati',
    noStudents: 'Hali o‘quvchi yaratilmagan.', edit: 'Tahrirlash', cancel: 'Bekor qilish', update: 'Saqlash', remove: 'O‘chirish',
    newPassword: 'Yangi parol (o‘zgartirmasangiz bo‘sh qoldiring)', noCourse: 'Kurs biriktirilmagan', created: 'O‘quvchi yaratildi.',
    confirmDelete: 'O‘quvchi o‘chirilsinmi?'
  },
  ru: {
    title: 'Ученики', sub: 'Администратор или учитель создаёт ученику логин, пароль и открывает нужные курсы.',
    create: 'Создать ученика', first: 'Имя', last: 'Фамилия', phone: 'Телефон (необязательно)', email: 'Email (необязательно)',
    login: 'Логин', password: 'Пароль', courses: 'Выберите курсы', save: 'Создать ученика', list: 'Список учеников',
    noStudents: 'Ученики ещё не созданы.', edit: 'Изменить', cancel: 'Отмена', update: 'Сохранить', remove: 'Удалить',
    newPassword: 'Новый пароль (оставьте пустым без изменения)', noCourse: 'Курсы не назначены', created: 'Ученик создан.',
    confirmDelete: 'Удалить ученика?'
  }
}
function tr(key) { return text[lang.value]?.[key] || text.uz[key] || key }

const emptyForm = () => ({ first_name: '', last_name: '', phone: '', email: '', username: '', password: '', course_ids: [] })
const form = reactive(emptyForm())
const editForm = reactive(emptyForm())
const sortedStudents = computed(() => [...students.value].sort((a, b) => String(a.first_name || '').localeCompare(String(b.first_name || ''))))

function handleLang(event) {
  lang.value = ['uz', 'ru'].includes(event.detail) ? event.detail : 'uz'
}
function resetForm(target) {
  Object.assign(target, emptyForm())
}
async function load() {
  loading.value = true
  error.value = ''
  try {
    const [sessionRes, studentsRes] = await Promise.all([
      api.get('/access/session'),
      api.get('/admin/students'),
    ])
    isAdmin.value = sessionRes.data.role === 'admin'
    students.value = studentsRes.data.students || []
    courses.value = studentsRes.data.courses || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Ma’lumot yuklanmadi.'
  } finally {
    loading.value = false
  }
}
async function createStudent() {
  error.value = ''
  message.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/admin/students', form)
    message.value = data.message || tr('created')
    resetForm(form)
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'O‘quvchi yaratilmadi.'
  } finally {
    loading.value = false
  }
}
function startEdit(student) {
  editingId.value = student.id
  Object.assign(editForm, {
    first_name: student.first_name || '',
    last_name: student.last_name || '',
    phone: student.phone || '',
    email: student.email || '',
    username: student.username || '',
    password: '',
    course_ids: (student.course_ids || []).map(Number),
  })
}
function cancelEdit() {
  editingId.value = null
  resetForm(editForm)
}
async function updateStudent(id) {
  error.value = ''
  message.value = ''
  loading.value = true
  try {
    const { data } = await api.put(`/admin/students/${id}`, editForm)
    message.value = data.message || tr('update')
    cancelEdit()
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'O‘quvchi saqlanmadi.'
  } finally {
    loading.value = false
  }
}
async function removeStudent(student) {
  if (!confirm(tr('confirmDelete'))) return
  error.value = ''
  message.value = ''
  try {
    const { data } = await api.delete(`/admin/students/${student.id}`)
    message.value = data.message || tr('remove')
    await load()
  } catch (err) {
    error.value = err.response?.data?.error || 'O‘quvchi o‘chirilmadi.'
  }
}

onMounted(() => {
  window.addEventListener('edulive-lang-change', handleLang)
  load()
})
onBeforeUnmount(() => window.removeEventListener('edulive-lang-change', handleLang))
</script>

<template>
  <section class="section simple-page-head">
    <h1>{{ tr('title') }}</h1>
    <p class="muted">{{ tr('sub') }}</p>
  </section>

  <section class="section card simple-card">
    <h2>{{ tr('create') }}</h2>
    <form class="simple-form" @submit.prevent="createStudent">
      <div class="form-grid-2">
        <label><span>{{ tr('first') }}</span><input v-model.trim="form.first_name" required /></label>
        <label><span>{{ tr('last') }}</span><input v-model.trim="form.last_name" required /></label>
        <label><span>{{ tr('phone') }}</span><input v-model.trim="form.phone" inputmode="tel" /></label>
        <label><span>{{ tr('email') }}</span><input v-model.trim="form.email" type="email" /></label>
        <label><span>{{ tr('login') }}</span><input v-model.trim="form.username" autocomplete="off" required /></label>
        <label><span>{{ tr('password') }}</span><input v-model="form.password" type="password" autocomplete="new-password" minlength="6" required /></label>
      </div>
      <fieldset class="course-check-list">
        <legend>{{ tr('courses') }}</legend>
        <label v-for="course in courses" :key="course.id" class="check-row">
          <input v-model="form.course_ids" type="checkbox" :value="course.id" />
          <span>{{ course.title }}</span>
        </label>
      </fieldset>
      <button class="btn" :disabled="loading">{{ tr('save') }}</button>
    </form>
  </section>

  <section class="section card simple-card">
    <div class="section-head simple-section-head">
      <div><h2>{{ tr('list') }}</h2></div>
      <span class="plain-count">{{ students.length }}</span>
    </div>

    <div v-if="loading && !students.length" class="muted">...</div>
    <div v-else class="simple-list">
      <article v-for="student in sortedStudents" :key="student.id" class="simple-list-item">
        <template v-if="editingId !== student.id">
          <div class="student-main-info">
            <strong>{{ student.first_name }} {{ student.last_name }}</strong>
            <span class="muted">{{ tr('login') }}: {{ student.username }}</span>
            <span class="muted">{{ student.phone || student.email || '—' }}</span>
          </div>
          <div class="student-course-text">
            {{ student.courses?.length ? student.courses.map(item => item.title).join(', ') : tr('noCourse') }}
          </div>
          <div v-if="isAdmin" class="row gap-sm simple-actions">
            <button class="btn btn-sm btn-light" type="button" @click="startEdit(student)">{{ tr('edit') }}</button>
            <button class="btn btn-sm btn-danger-simple" type="button" @click="removeStudent(student)">{{ tr('remove') }}</button>
          </div>
        </template>

        <form v-else class="simple-form edit-student-form" @submit.prevent="updateStudent(student.id)">
          <div class="form-grid-2">
            <label><span>{{ tr('first') }}</span><input v-model.trim="editForm.first_name" required /></label>
            <label><span>{{ tr('last') }}</span><input v-model.trim="editForm.last_name" required /></label>
            <label><span>{{ tr('phone') }}</span><input v-model.trim="editForm.phone" /></label>
            <label><span>{{ tr('email') }}</span><input v-model.trim="editForm.email" type="email" /></label>
            <label><span>{{ tr('login') }}</span><input v-model.trim="editForm.username" required /></label>
            <label><span>{{ tr('newPassword') }}</span><input v-model="editForm.password" type="password" minlength="6" /></label>
          </div>
          <fieldset class="course-check-list">
            <legend>{{ tr('courses') }}</legend>
            <label v-for="course in courses" :key="course.id" class="check-row">
              <input v-model="editForm.course_ids" type="checkbox" :value="course.id" />
              <span>{{ course.title }}</span>
            </label>
          </fieldset>
          <div class="row gap-sm simple-actions">
            <button class="btn btn-sm">{{ tr('update') }}</button>
            <button class="btn btn-sm btn-light" type="button" @click="cancelEdit">{{ tr('cancel') }}</button>
          </div>
        </form>
      </article>
      <p v-if="!students.length" class="muted">{{ tr('noStudents') }}</p>
    </div>
  </section>

  <div v-if="message" class="flash success">{{ message }}</div>
  <div v-if="error" class="flash error">{{ error }}</div>
</template>
