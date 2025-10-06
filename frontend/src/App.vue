<template>
  <div id="app-layout">
    <header>
      <nav>
        <router-link to="/">Plotix_blog</router-link>
        <div class="nav-links">
          <template v-if="authStore.token">
            <button @click="authStore.logout()">Выйти</button>
          </template>
          <template v-else>
            <router-link to="/login">Вход</router-link>
            <router-link to="/register">Регистрация</router-link>
          </template>
        </div>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from './store/auth'
const authStore = useAuthStore()
</script>

<style>
/* Глобальные стили для простоты */
body { font-family: sans-serif; margin: 0; }
#app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
header {
  background-color: #f8f9fa;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 960px;
  margin: 0 auto;
}
nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}
nav a.router-link-exact-active {
  color: #42b983;
}
nav button {
  background: none;
  border: 1px solid #42b983;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  color: #42b983;
}
main {
  flex-grow: 1;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}
</style>