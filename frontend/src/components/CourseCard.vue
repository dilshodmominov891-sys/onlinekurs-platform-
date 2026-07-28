<script setup>
const props = defineProps({ course: Object })
</script>

<template>
  <div class="card course-card-premium">
    <div class="course-head">
      <div class="course-card-badges">
        <span v-if="course.is_live_class" class="badge live">🎥 Live dars</span>
        <span v-else class="badge">{{ course.technology }}</span>
        <span v-if="course.is_live_class" class="badge">{{ course.level || course.technology }}</span>
        <span v-if="course.is_live_class" class="badge">{{ course.live_participants_count || 0 }} ta online</span>
      </div>
      <div class="lock-icon">{{ course.is_unlocked ? '🔓' : '🔒' }}</div>
    </div>
    <template v-if="course.is_live_class">
      <div class="live-card-label">Live dars</div>
      <h3 class="live-level-title">{{ course.level || 'Live' }}</h3>
      <p><strong>{{ course.title }}</strong><br>{{ course.description }}</p>
    </template>
    <template v-else>
      <h3>{{ course.title }}</h3>
      <p>{{ course.description }}</p>
    </template>
    <div class="course-meta">
      <span>{{ course.level }}</span>
      <span>{{ course.duration }}</span>
    </div>
    <div class="price-row">
      <strong>{{ Number(course.price).toLocaleString() }} so‘m</strong>
      <RouterLink class="btn btn-sm" :to="`/course/${course.slug}`">{{ course.is_live_class ? (course.is_unlocked ? 'Live yozuvni ko‘rish' : 'Sotib olish') : (course.is_unlocked ? 'Kirish' : 'Sotib olish') }}</RouterLink>
    </div>
  </div>
</template>
