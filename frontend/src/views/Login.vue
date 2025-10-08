<template>
  <div class="auth-page">
    <h2>Вход</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="email">Email или Имя</label>
        <input type="text" id="email" v-model="email" required placeholder="Введите email или имя">
      </div>
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <button type="submit" class="btn btn-primary">Войти</button>
      <p v-if="authStore.error" class="error">{{ authStore.error }}</p>
      <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'
import { useNotificationStore } from '../store/notifications'

const email = ref('')
const password = ref('')
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const handleSubmit = () => {
  notificationStore.unlockAudioContext();
  authStore.login({ email: email.value, password: password.value })
}
</script>

<style scoped>
/* Scoped styles are removed as they are now in main.css */
</style>
