<template>
  <div class="user-profile-page">
    <h1>Профиль пользователя</h1>
    <form @submit.prevent="saveProfile" class="profile-form">
      <div class="form-group">
        <label for="nickname">Никнейм:</label>
        <input type="text" id="nickname" v-model="profile.nickname" maxlength="25" />
      </div>

      <div class="form-group">
        <label for="first_name">Имя:</label>
        <input type="text" id="first_name" v-model="profile.first_name" />
      </div>

      <div class="form-group">
        <label for="last_name">Фамилия:</label>
        <input type="text" id="last_name" v-model="profile.last_name" />
      </div>

      <div class="form-group">
        <label for="email">Почта:</label>
        <input type="email" id="email" v-model="profile.email" disabled /> <!-- Почту пока не меняем через профиль -->
      </div>

      <button type="submit" class="btn btn-primary">Сохранить изменения</button>
      <p v-if="authStore.error" class="error-message">{{ authStore.error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();

const profile = ref({
  nickname: '',
  first_name: '',
  last_name: '',
  email: '',
});

const successMessage = ref('');

// Инициализация полей формы данными пользователя при загрузке компонента
const loadUserProfile = () => {
  if (authStore.user) {
    profile.value.nickname = authStore.user.nickname || '';
    profile.value.first_name = authStore.user.first_name || '';
    profile.value.last_name = authStore.user.last_name || '';
    profile.value.email = authStore.user.email || '';
  }
};

onMounted(() => {
  if (!authStore.user) {
    // Если пользователь еще не загружен, пытаемся его получить
    authStore.fetchUser().then(() => {
      loadUserProfile();
    });
  } else {
    loadUserProfile();
  }
});

// Отслеживаем изменения в authStore.user, чтобы обновить форму
watch(() => authStore.user, (newUser) => {
  if (newUser) {
    loadUserProfile();
  }
}, { deep: true });

const saveProfile = async () => {
  successMessage.value = '';
  const updateData = {
    nickname: profile.value.nickname,
    first_name: profile.value.first_name,
    last_name: profile.value.last_name,
    // Email не отправляем, так как его нельзя менять через этот UI
  };
  const success = await authStore.updateUser(updateData);
  if (success) {
    successMessage.value = 'Профиль успешно обновлен!';
  }
};
</script>

<style scoped>
.user-profile-page {
  padding: 30px;
  max-width: 600px;
  margin: 40px auto;
  background-color: var(--card-bg-color);
  border-radius: 12px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  color: var(--text-color);
  text-align: center;
  margin-bottom: 30px;
  font-size: 2.2rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-color);
  font-size: 1.1rem;
}

.form-group input[type="text"],
.form-group input[type="email"] {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--text-color);
  background-color: var(--bg-color);
  box-sizing: border-box; /* Включаем padding и border в общую ширину */
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input[type="text"]:focus,
.form-group input[type="email"]:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.2);
  outline: none;
}

.form-group input[disabled] {
  background-color: var(--bg-color-disabled, #e9ecef);
  cursor: not-allowed;
  opacity: 0.7;
}

.profile-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  font-size: 1.1rem;
  border-radius: 8px;
  margin-top: 25px;
}

.error-message,
.success-message {
  margin-top: 10px;
  font-size: 0.95rem;
}
</style>
