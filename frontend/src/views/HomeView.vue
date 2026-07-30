<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../lib'
import CourseCard from '../components/CourseCard.vue'

const props = defineProps({ section: { type: String, default: 'home' } })
const courses = ref([])
const classes = ref([])
const sessionRole = ref(null)
const student = ref(null)
const teacher = ref(null)
const liveStats = ref({ week_count: 0, month_count: 0, total_count: 0, recent: [], by_room: [] })
const teacherError = ref('')
const telegramLink = 'https://t.me/mominov9969'

let loadPromise = null
let lastLoadedAt = 0
const CACHE_MS = 30000

const fallbackCourses = [
  { id: 'f1', slug: 'frontend-html-css', title: 'HTML & CSS Boshlang‘ich', track: 'frontend', technology: 'HTML & CSS', description: 'Frontend asoslari, layout, responsive dizayn va amaliy mashqlar.', duration: '4 hafta', level: '1-bosqich', price: 199000, is_unlocked: 0, is_live_class: 0 },
  { id: 'f2', slug: 'frontend-js', title: 'JavaScript Praktikum', track: 'frontend', technology: 'JavaScript', description: 'DOM, event, fetch, mini loyiha va real amaliyot.', duration: '6 hafta', level: '2-bosqich', price: 239000, is_unlocked: 0, is_live_class: 0 },
  { id: 'f3', slug: 'frontend-vue', title: 'Vue 3 Pro Kurs', track: 'frontend', technology: 'Vue', description: 'Composition API, router, component va dashboardlar.', duration: '8 hafta', level: '3-bosqich', price: 279000, is_unlocked: 0, is_live_class: 0 },
  { id: 'b1', slug: 'backend-python', title: 'Python Backend Start', track: 'backend', technology: 'Python', description: 'API, auth, CRUD va backend asoslari.', duration: '6 hafta', level: '1-bosqich', price: 219000, is_unlocked: 0, is_live_class: 0 },
  { id: 'b2', slug: 'backend-django', title: 'Django Full Backend', track: 'backend', technology: 'Django', description: 'Model, view, auth, postgres va productionga tayyorlash.', duration: '10 hafta', level: '2-bosqich', price: 289000, is_unlocked: 0, is_live_class: 0 },
  { id: 'b3', slug: 'backend-api', title: 'REST API & Security', track: 'backend', technology: 'REST API', description: 'Token, permission, test va xavfsizlik qoidalari.', duration: '5 hafta', level: '3-bosqich', price: 259000, is_unlocked: 0, is_live_class: 0 },
]

function normalizeCourse(item) {
  return {
    ...item,
    track: (item.track || '').toString().trim().toLowerCase(),
    is_live_class: Number(item.is_live_class || 0) === 1 || item.is_live_class === true,
  }
}

async function load(force = false) {
  if (loadPromise) return loadPromise
  if (!force && courses.value.length && Date.now() - lastLoadedAt < CACHE_MS) return

  loadPromise = (async () => {
  teacherError.value = ''
  try {
    const sessionRes = await api.get('/student/session')
    sessionRole.value = sessionRes.data.role || null
    student.value = sessionRes.data.student || null
    teacher.value = sessionRes.data.teacher || null
  } catch {
    sessionRole.value = null
    student.value = null
    teacher.value = null
  }

  try {
    const [classesRes, coursesRes] = await Promise.all([api.get('/classes'), api.get('/courses')])
    classes.value = classesRes.data.classes || []
    const apiCourses = (coursesRes.data.courses || []).map(normalizeCourse)
    courses.value = apiCourses.length ? apiCourses : fallbackCourses.map(normalizeCourse)
  } catch {
    classes.value = []
    courses.value = fallbackCourses.map(normalizeCourse)
  }

  if (sessionRole.value === 'teacher' || sessionRole.value === 'admin') {
    try {
      const { data } = await api.get('/admin/live-stats')
      liveStats.value = data.stats || liveStats.value
    } catch (err) {
      teacherError.value = err.response?.data?.error || 'Statistika yuklanmadi.'
    }
  }
    lastLoadedAt = Date.now()
  })()

  try {
    await loadPromise
  } finally {
    loadPromise = null
  }
}

const frontendCourses = computed(() => courses.value.filter((item) => item.track === 'frontend' && !item.is_live_class))
const backendCourses = computed(() => courses.value.filter((item) => item.track === 'backend' && !item.is_live_class))
const liveVideoCourses = computed(() => courses.value.filter((item) => item.is_live_class).slice(0, 3))
const activeLiveClasses = computed(() => classes.value.filter((item) => item.is_live).length)
const teacherName = computed(() => teacher.value?.full_name || 'Ustoz')
const isTeacher = computed(() => sessionRole.value === 'teacher' || sessionRole.value === 'admin')
const hasAnyCourses = computed(() => frontendCourses.value.length + backendCourses.value.length > 0)

watch(() => props.section, () => {
  // Bo‘limlar almashganda sahifani bo‘shatib yubormaymiz: eski ma’lumot turadi, yangisi fon rejimida keladi.
  // Shu sabab Home/Kurs/Ustoz bo‘limlari orasida oq ekran yoki qotish sezilmaydi.
  load()
}, { immediate: true })
</script>

<template>
  <section v-if="section === 'home'" class="section home-hero-stack">
    <div class="card glass home-card-single friendly-home-card hero-spotlight animated-card">
      <div class="home-hero-grid">
        <div class="stack">
          <span class="pill">Ishonchli online ta’lim</span>
          <h1 v-if="isTeacher">Xush kelibsiz, {{ teacherName }}</h1>
          <h1 v-else>EduLive Pro platformasiga xush kelibsiz</h1>
          <p class="lead" v-if="isTeacher">Birinchi bo‘lib home sahifa ochiladi. Shu yerdan kurs yaratish, test qo‘shish, ustoz yaratish va live statistikani boshqarasiz.</p>
          <p class="lead" v-else>Bu platformada o‘quvchilar registratsiya qiladi, pullik kurslarga kiradi, live dars yozuvlarini ko‘radi va frontend yoki backend bo‘yicha test yechadi.</p>
          <div class="row wrap gap-sm" v-if="isTeacher">
            <RouterLink class="btn" to="/teacher/courses">Kurs yaratish</RouterLink>
            <RouterLink class="btn btn-secondary" to="/teacher/tests">Test qo‘shish</RouterLink>
            <RouterLink v-if="sessionRole === 'admin'" class="btn" to="/admin">Admin qismi</RouterLink>
          </div>
          <div class="row wrap gap-sm" v-else>
            <RouterLink class="btn" to="/courses">Kurslarni ko‘rish</RouterLink>
            <RouterLink class="btn btn-secondary" to="/practice-tests">Test yechish</RouterLink>
          </div>
        </div>

        <div class="hero-illustration-card">
          <div class="hero-orbit"></div>
          <div class="hero-logo-ring">EL</div>
          <div class="floating-chip chip-one">Frontend</div>
          <div class="floating-chip chip-two">Backend</div>
          <div class="floating-chip chip-three">Live</div>
        </div>
      </div>

      <div class="feature-grid single-column-grid compact-feature-grid photo-like-grid" v-if="isTeacher">
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">📚</div><strong>Kurs yaratish</strong><span class="muted">Yangi frontend yoki backend kurs qo‘shish</span></div>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">🧪</div><strong>Test boshqaruvi</strong><span class="muted">Daraja bo‘yicha Excel testlarni saqlash</span></div>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">🔴</div><strong>Live statistika</strong><span class="muted">7 kun va 30 kun davomida kirganlar soni</span></div>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">🛡️</div><strong>Admin nazorati</strong><span class="muted">Tushum, o‘quvchi, kurs va ustoz faoliyati</span></div>
      </div>
      <div class="feature-grid single-column-grid compact-feature-grid photo-like-grid" v-else>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">🎓</div><strong>Kurslar</strong><span class="muted">Frontend va backend bo‘yicha pullik yo‘nalishlar</span></div>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">🧪</div><strong>Test tizimi</strong><span class="muted">Daraja va yo‘nalish bo‘yicha testlarni ishlash</span></div>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">🎥</div><strong>Live darslar</strong><span class="muted">Live yozuv kurslari alohida bo‘limda saqlanadi</span></div>
        <div class="mini-card feature-visual hover-lift"><div class="emoji-big">📈</div><strong>Natijalar</strong><span class="muted">Ustoz natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi</span></div>
      </div>
    </div>

    <div class="grid-2 gap-lg section" v-if="isTeacher">
      <div class="card glass animated-card">
        <h2>Tezkor ko‘rsatkichlar</h2>
        <div class="stats-grid">
          <div class="mini-card"><strong>7 kun</strong><div class="big-stat">{{ liveStats.week_count }}</div><span class="muted">Jonli darsga kirishlar</span></div>
          <div class="mini-card"><strong>30 kun</strong><div class="big-stat">{{ liveStats.month_count }}</div><span class="muted">Jonli darsga kirishlar</span></div>
          <div class="mini-card"><strong>Jami</strong><div class="big-stat">{{ liveStats.total_count }}</div><span class="muted">Barcha kirishlar</span></div>
          <div class="mini-card"><strong>Aktiv live</strong><div class="big-stat">{{ activeLiveClasses }}</div><span class="muted">Hozir ochiq darslar</span></div>
        </div>
      </div>
      <div class="card glass animated-card">
        <h2>Platforma haqida</h2>
        <p class="muted">Bu home sahifadan ustoz ham, o‘quvchi ham chiroyli ko‘rinishda ish boshlaydi. Har bir bo‘lim hover animatsiya va yumshoq loading bilan ishlaydi.</p>
        <div class="promo-photo-grid">
          <div class="promo-photo photo-blue">Kurs</div>
          <div class="promo-photo photo-purple">Test</div>
          <div class="promo-photo photo-green">Live</div>
        </div>
      </div>
    </div>

    <div class="grid-2 gap-lg section" v-else>
      <div class="card glass animated-card info-photo-card">
        <h2>Platforma haqida</h2>
        <p class="muted">EduLive Pro — o‘quv markaz va kurs tizimiga mos zamonaviy platforma. Har bir bo‘lim hover animatsiya, yumshoq o‘tish va chiroyli bloklar bilan tayyorlangan.</p>
        <div class="promo-photo-grid">
          <div class="promo-photo photo-blue">Kodlash</div>
          <div class="promo-photo photo-purple">Live dars</div>
          <div class="promo-photo photo-green">Natija</div>
        </div>
      </div>
      <div class="card glass animated-card">
        <h2>Qisqacha ishlash tartibi</h2>
        <div class="info-list">
          <div><strong>1.</strong> O‘quvchi registratsiya qiladi va tizimga kiradi.</div>
          <div><strong>2.</strong> Ustoz testlarni o‘z bo‘limidan frontend yoki backend yo‘nalishiga qo‘shadi.</div>
          <div><strong>3.</strong> O‘quvchi testni yechadi, natijalar ustoz bo‘limiga tushadi.</div>
          <div><strong>4.</strong> Live yozuvlar alohida pullik bo‘limga saqlanadi.</div>
        </div>
      </div>
    </div>

    <section class="section" v-if="liveVideoCourses.length && !isTeacher">
      <div class="section-head"><div><h2>Yangi live yozuv kurslari</h2><p class="muted">Live olib qo‘yilgan va pullik tarzda ochiladigan kurslar</p></div><RouterLink class="btn btn-sm" to="/live-courses">Hammasini ko‘rish</RouterLink></div>
      <div class="class-grid">
        <CourseCard v-for="course in liveVideoCourses" :key="course.id" :course="course" />
      </div>
    </section>
  </section>

  <section v-else-if="section === 'teacher'" class="section teacher-section-wrap">
    <div class="card glass animated-card">
      <div class="section-head centered-head">
        <div>
          <h2>Ustoz boshqaruv markazi</h2>
          <p class="muted">Kurs yarating, test qo‘shing, natijalarni ko‘ring va live kirish statistikani tahlil qiling.</p>
        </div>
        <span class="pill">Faqat ustozlar</span>
      </div>
      <div class="stats-grid teacher-menu-grid">
        <RouterLink class="mini-card hover-lift" to="/teacher/courses"><strong>Kurs yaratish</strong><span class="muted">Frontend/backend kurslarini qo‘shish</span></RouterLink>
        <RouterLink class="mini-card hover-lift" to="/teacher/tests"><strong>Test qo‘shish</strong><span class="muted">Excel testni yo‘nalish va darajaga biriktirish</span></RouterLink>
        <RouterLink class="mini-card hover-lift" to="/results-board"><strong>Natijalar</strong><span class="muted">Ism, familiya, to‘g‘ri soni va foizi</span></RouterLink>
        <RouterLink class="mini-card hover-lift" to="/live"><strong>Live statistika</strong><span class="muted">Bir hafta va bir oy bo‘yicha kirishlar</span></RouterLink>
        <RouterLink v-if="sessionRole === 'admin'" class="mini-card hover-lift" to="/admin"><strong>Admin qismi</strong><span class="muted">Ustoz yaratish va barcha nazorat shu yerda</span></RouterLink>
      </div>
      <div v-if="teacherError" class="flash error">{{ teacherError }}</div>
    </div>
  </section>

  <template v-else-if="section === 'courses'">
    <section class="section">
      <div class="section-head">
        <div>
          <h2>Kurslar bo‘limi</h2>
          <p class="muted">Sotuvdagi barcha kurslar quyida joylashgan</p>
        </div>
        <span class="pill">Barcha kurslar</span>
      </div>
      <div class="section section-nested">
        <div class="section-head"><div><h2>Frontend yo‘nalishlari</h2><p class="muted">HTML, CSS, JavaScript, Vue, React</p></div><span class="pill">Frontend</span></div>
        <div class="class-grid">
          <CourseCard v-for="course in frontendCourses" :key="course.id" :course="course" />
        </div>
      </div>
    </section>
    <section class="section">
      <div class="section-head"><div><h2>Backend yo‘nalishlari</h2><p class="muted">Python, Django, PostgreSQL, REST API</p></div><span class="pill">Backend</span></div>
      <div class="class-grid">
        <CourseCard v-for="course in backendCourses" :key="course.id" :course="course" />
      </div>
    </section>
    <section v-if="!hasAnyCourses" class="section">
      <div class="card glass empty-state-card">Kurslar vaqtincha backenddan kelmadi. Shu sabab ko‘rinish buzilmasligi uchun tayyor demo kurslar chiqarildi.</div>
    </section>
  </template>

  <section v-else-if="section === 'telegram'" class="section">
    <div class="card glass sidebar-info-card">
      <div class="section-head">
        <div><h2>Telegram bo‘limi</h2><p class="muted">Faqat Telegram lichkaga yozasiz</p></div>
        <a class="btn btn-secondary" :href="telegramLink" target="_blank" rel="noreferrer">Telegramga yozish</a>
      </div>
      <p class="lead small-lead">Savollar, kirish bo‘yicha yordam va qo‘shimcha ma’lumot shu bo‘lim orqali olinadi.</p>
    </div>
  </section>

  <template v-else-if="section === 'live'">
    <section class="section">
      <div class="section-head">
        <div>
          <h2>Live dars statistikasi</h2>
          <p class="muted">Bu bo‘limda endi jonli darsga qo‘shilish formasi yo‘q. O‘rniga necha o‘quvchi kirgani ko‘rsatiladi.</p>
        </div>
        <span class="pill">Live analytics</span>
      </div>
      <div class="stats-grid">
        <div class="mini-card"><strong>So‘nggi 7 kun</strong><div class="big-stat">{{ liveStats.week_count }}</div><span class="muted">Jonli darsga kirganlar</span></div>
        <div class="mini-card"><strong>So‘nggi 30 kun</strong><div class="big-stat">{{ liveStats.month_count }}</div><span class="muted">Jonli darsga kirganlar</span></div>
        <div class="mini-card"><strong>Jami kirish</strong><div class="big-stat">{{ liveStats.total_count }}</div><span class="muted">Barcha yozilgan kirishlar</span></div>
        <div class="mini-card"><strong>Hozir active</strong><div class="big-stat">{{ activeLiveClasses }}</div><span class="muted">Yoqilgan live darslar</span></div>
      </div>
    </section>

    <section class="grid-2 gap-lg">
      <div class="card glass animated-card">
        <h3>Eng ko‘p kirilgan live xonalar</h3>
        <div class="results-list">
          <div v-for="item in liveStats.by_room" :key="item.room_code" class="result-item">
            <div>
              <strong>{{ item.room_code }}</strong>
              <div class="muted small-text">Oxirgi kirish: {{ item.latest_join?.replace('T', ' ')?.slice(0, 16) }}</div>
            </div>
            <div class="pill">{{ item.join_count }} ta kirish</div>
          </div>
          <p v-if="!liveStats.by_room.length" class="muted">Hali statistik ma’lumot yo‘q.</p>
        </div>
      </div>

      <div class="card glass animated-card">
        <h3>So‘nggi kirgan o‘quvchilar</h3>
        <div class="results-list">
          <div v-for="item in liveStats.recent" :key="item.id" class="result-item">
            <div>
              <strong>{{ item.student_name }}</strong>
              <div class="muted small-text">{{ item.room_code }} · {{ item.joined_at?.replace('T', ' ')?.slice(0, 16) }}</div>
            </div>
            <div class="pill">Kirdi</div>
          </div>
          <p v-if="!liveStats.recent.length" class="muted">Hali o‘quvchi kirmagan.</p>
        </div>
      </div>
    </section>
  </template>
</template>
