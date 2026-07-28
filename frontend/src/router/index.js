import { createRouter, createWebHistory } from 'vue-router'
import { hydrateSession } from '../sessionStore'
import HomeView from '../views/HomeView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import AdminClassView from '../views/AdminClassView.vue'
import StudentRoomView from '../views/StudentRoomView.vue'
import TakeTestView from '../views/TakeTestView.vue'
import StudentAuthView from '../views/StudentAuthView.vue'
import CourseDetailView from '../views/CourseDetailView.vue'
import LessonPlayerView from '../views/LessonPlayerView.vue'
import PracticeTestsView from '../views/PracticeTestsView.vue'
import ResultsBoardView from '../views/ResultsBoardView.vue'
import TeacherTestsView from '../views/TeacherTestsView.vue'
import LiveCoursesView from '../views/LiveCoursesView.vue'
import TeacherCoursesView from '../views/TeacherCoursesView.vue'
import TeacherTeachersView from '../views/TeacherTeachersView.vue'
import TeacherLiveStudioView from '../views/TeacherLiveStudioView.vue'
import AdminTeacherCreateView from '../views/AdminTeacherCreateView.vue'
import AdminInfoView from '../views/AdminInfoView.vue'
import StudentQuestionsView from '../views/StudentQuestionsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/auth' },
    { path: '/home', name: 'home', component: HomeView, props: { section: 'home' } },
    { path: '/teacher', name: 'teacher', component: HomeView, props: { section: 'teacher' } },
    { path: '/teacher/courses', name: 'teacher-courses', component: TeacherCoursesView },
    { path: '/teacher/teachers', name: 'teacher-teachers', component: TeacherTeachersView },
    { path: '/teacher/tests', name: 'teacher-tests', component: TeacherTestsView },
    { path: '/courses', name: 'courses', component: HomeView, props: { section: 'courses' } },
    { path: '/telegram', name: 'telegram', component: HomeView, props: { section: 'telegram' } },
    { path: '/live', name: 'live', component: TeacherLiveStudioView },
    { path: '/live-courses', name: 'live-courses', component: LiveCoursesView },
    { path: '/results-board', name: 'results-board', component: ResultsBoardView },
    { path: '/practice-tests', name: 'practice-tests', component: PracticeTestsView },
    { path: '/questions', name: 'questions', component: StudentQuestionsView },
    { path: '/auth', name: 'student-auth', component: StudentAuthView },
    { path: '/course/:slug', name: 'course-detail', component: CourseDetailView, props: true },
    { path: '/course/:slug/lesson/:lessonId', name: 'lesson-player', component: LessonPlayerView, props: true },
    { path: '/admin/login', name: 'admin-login', component: AdminLoginView },
    { path: '/admin', name: 'admin-dashboard', component: AdminDashboardView },
    { path: '/admin/teachers', name: 'admin-teachers-create', component: AdminTeacherCreateView },
    { path: '/admin/info', name: 'admin-info', component: AdminInfoView },
    { path: '/admin/class/:id', name: 'admin-class', component: AdminClassView, props: true },
    { path: '/room/:roomCode', name: 'student-room', component: StudentRoomView, props: true },
    { path: '/test/:testId', name: 'test', component: TakeTestView, props: true },
  ],
  scrollBehavior() { return { top: 0 } }
})

// Tez route guard: bo‘limdan bo‘limga o‘tganda backend javobini kutib qotib qolmasin.
// Session App.vue ichida fon rejimida yangilanadi, bu yerda esa faqat localStorage dagi oxirgi rol bilan tez tekshiriladi.
router.beforeEach((to) => {
  const publicNames = new Set(['student-auth', 'admin-login'])
  if (publicNames.has(to.name)) return true

  const saved = hydrateSession()
  const role = saved?.role || ''
  if (!role) return '/auth'

  const adminOnly = new Set(['admin-dashboard', 'admin-class', 'admin-teachers-create', 'admin-info'])
  if (adminOnly.has(to.name) || String(to.path).startsWith('/admin')) {
    return role === 'admin' ? true : '/teacher'
  }
  const teacherOnly = new Set(['teacher', 'teacher-courses', 'teacher-teachers', 'teacher-tests', 'live', 'results-board'])
  if (teacherOnly.has(to.name)) {
    return (role === 'teacher' || role === 'admin') ? true : '/home'
  }
  if (to.name === 'teacher-teachers' && role !== 'admin') return '/teacher'
  return true
})

export default router
