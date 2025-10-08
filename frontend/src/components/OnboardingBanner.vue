<template>
  <div class="onboarding-banner">
    <div class="banner-content">
      <span class="emoji">👋</span>
      <p>Добро пожаловать в Plotix! Создавайте списки, добавляйте желания и делитесь ими с друзьями.</p>
    </div>
    <button @click="$emit('dismiss')" class="dismiss-btn">Понятно</button>
  </div>
</template>

<script setup>
defineEmits(['dismiss']);
</script>

<style scoped>
.onboarding-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e3dffd;
  color: #3d375e;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.banner-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.emoji {
  font-size: 1.5rem;
}
p {
  margin: 0;
  font-weight: 500;
}
.dismiss-btn {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
</style>