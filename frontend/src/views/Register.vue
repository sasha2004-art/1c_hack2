<template>
  <div class="auth-page">
    <h2>Регистрация</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">Имя</label>
        <input type="text" id="name" v-model="name" required placeholder="Введите ваше имя">
      </div>
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" v-model="email" id="email" required />
      </div>
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <button type="submit" class="btn btn-primary">Зарегистрироваться</button>
      <p v-if="authStore.error" class="error">{{ authStore.error }}</p>
       <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const name = ref('')
const email = ref('')
const password = ref('')

const handleSubmit = () => {
  authStore.register({ 
    name: name.value,
    email: email.value, 
    password: password.value 
  })
}
</script>

<style scoped>
/* Scoped styles are removed as they are now in main.css */
</style>
