<script setup>
defineProps({ course: Object })
</script>

<template>
  <article class="card simple-course-card">
    <div class="simple-course-card-top">
      <span class="plain-label">{{ course.technology || course.track }}</span>
      <span class="plain-count">{{ course.is_unlocked ? 'Ochiq' : 'Yopiq' }}</span>
    </div>
    <h3>{{ course.title }}</h3>
    <p class="muted">{{ course.description }}</p>
    <div class="simple-info-row">
      <span>{{ course.level || '—' }}</span>
      <span>{{ course.duration || '—' }}</span>
    </div>
    <RouterLink class="btn btn-sm" :to="`/course/${course.slug}`">Ko‘rish</RouterLink>
  </article>
</template>
