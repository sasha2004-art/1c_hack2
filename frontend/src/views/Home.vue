<template>
  <div class="home-page">
    <h1>Добро пожаловать!</h1>
    <p v-if="authStore.user">Вы вошли как: <strong>{{ authStore.user.email }}</strong></p>
    <p>Это ваша защищенная домашняя страница.</p>
  </div>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import { onMounted } from 'vue';

const authStore = useAuthStore()

onMounted(() => {
  if (!authStore.user && authStore.token) {
    authStore.fetchUser();
  }
})
</script>

<style scoped>
.home-page { text-align: center; margin-top: 50px; }
</style>
