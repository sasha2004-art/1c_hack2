import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '../router'

const API_URL = 'http://localhost:8000';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('user-token') || null)
  const user = ref(null)
  const error = ref(null)

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('user-token', newToken)
    } else {
      localStorage.removeItem('user-token')
    }
  }

  async function register(credentials) {
    try {
      error.value = null
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
      router.push({ name: 'Login' })
    } catch (e) {
      error.value = e.message
    }
  }

  async function login(credentials) {
    try {
      error.value = null
      const response = await fetch(`${API_URL}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: credentials.email,
          password: credentials.password
        })
      })

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json()
      setToken(data.access_token)
      await fetchUser()
      router.push({ name: 'Home' })
    } catch (e) {
      error.value = e.message
    }
  }

  async function fetchUser() {
    if (!token.value) return;
    try {
      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch user');
      user.value = await response.json();
    } catch (e) {
      console.error(e);
      logout();
    }
  }

  function logout() {
    setToken(null)
    user.value = null
    router.push({ name: 'Login' })
  }

  return { token, user, error, register, login, logout, fetchUser, setToken }
})
