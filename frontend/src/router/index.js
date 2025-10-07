import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
// Импортируем новый компонент страницы
import ListView from '../views/ListView.vue'
// Импортируем новый компонент публичной страницы
import PublicListView from '../views/PublicListView.vue'
// (Задача 7.1) Импортируем новый компонент
import FriendsView from '../views/FriendsView.vue'
// (Задача 8.1) Импортируем новый компонент
import UserProfileView from '../views/UserProfileView.vue'
// (Этап 11) Импортируем новый компонент ленты
import FeedView from '../views/FeedView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  // (Этап 11) Новый маршрут для ленты
  {
    path: '/feed',
    name: 'Feed',
    component: FeedView,
    meta: { requiresAuth: true }
  },
  // (Задача 7.2) Новый маршрут для страницы друзей
  {
    path: '/friends',
    name: 'Friends',
    component: FriendsView,
    meta: { requiresAuth: true }
  },
  // (Задача 8.2) Новый маршрут для профиля
  {
    path: '/users/:userId',
    name: 'UserProfile',
    component: UserProfileView,
    props: true,
    meta: { requiresAuth: true }
  },
  // Новый маршрут для просмотра конкретного списка
  {
    path: '/lists/:id',
    name: 'ListView',
    component: ListView,
    props: true, // Позволяет передавать :id как пропс в компонент
    meta: { requiresAuth: true }
  },
  // Новый маршрут для публичного просмотра
  {
    path: '/public/lists/:publicKey',
    name: 'PublicListView',
    component: PublicListView,
    props: true // Передаем :publicKey как пропс
    // Этот роут не требует аутентификации (нет meta: { requiresAuth: true })
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (!authStore.token && localStorage.getItem('user-token')) {
    authStore.setToken(localStorage.getItem('user-token'))
  }

  const isAuthenticated = !!authStore.token

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
