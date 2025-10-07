<template>
  <div class="auth-page">
    <h2>Регистрация</h2>
    <form @submit.prevent="handleSubmit">
      <!-- НОВОЕ ПОЛЕ "ИМЯ" -->
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
      <button type="submit">Зарегистрироваться</button>
      <p v-if="authStore.error" class="error">{{ authStore.error }}</p>
       <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const name = ref('') // <-- ДОБАВИТЬ
const email = ref('')
const password = ref('')

const handleSubmit = () => {
  // Передаем имя в экшен
  authStore.register({ 
    name: name.value, // <-- ДОБАВИТЬ
    email: email.value, 
    password: password.value 
  })
}
</script>

<style scoped>
.auth-page { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
.form-group { margin-bottom: 15px; }
label { display: block; margin-bottom: 5px; }
input { width: 100%; padding: 8px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background-color: #42b983; color: white; border: none; border-radius: 5px; cursor: pointer; }
.error { color: red; margin-top: 10px; }
</style>
