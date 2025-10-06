<template>
  <div class="public-list-container">
    <div v-if="isLoading">Загрузка...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="list">
      <header class="list-header">
        <h1>{{ list.title }}</h1>
        <p>{{ list.description }}</p>
      </header>

      <div v-if="list.items && list.items.length">
        <ul class="items">
          <li v-for="item in list.items" :key="item.id" class="item">
            <h3>{{ item.title }}</h3>
            <p v-if="item.description">{{ item.description }}</p>
            <small v-if="item.details">{{ item.details }}</small>
          </li>
        </ul>
      </div>
      <div v-else class="no-items">В этом списке нет элементов.</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { apiClient } from '../store/auth'
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id

const list = ref(null)
const isLoading = ref(false)
const error = ref(null)

onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
  const resp = await apiClient.get(`/public/lists/${id}`)
    list.value = resp.data
  } catch (e) {
    // If backend hides private lists as 404, present friendly message
    if (e.response?.status === 404) {
      error.value = 'Список не найден или он приватный.'
    } else {
      error.value = 'Не удалось загрузить список.'
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.public-list-container { max-width: 900px; margin: 2rem auto; padding: 1rem; }
.list-header { text-align: center; margin-bottom: 1.5rem }
.items { list-style: none; padding: 0; }
.item { padding: 1rem; border-bottom: 1px solid #eee }
.error { color: red; text-align: center }
.no-items { text-align: center; color: #666 }
</style>
