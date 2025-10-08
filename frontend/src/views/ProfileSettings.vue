<template>
  <div class="settings-container">
    <h1>Настройки профиля</h1>

    <div class="settings-grid">
      <!-- Блок смены пароля -->
      <div class="settings-card">
        <h3>Смена пароля</h3>
        <form @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label for="current-password">Текущий пароль</label>
            <input type="password" id="current-password" v-model="passwordForm.current_password" required>
          </div>
          <div class="form-group">
            <label for="new-password">Новый пароль</label>
            <input type="password" id="new-password" v-model="passwordForm.new_password" required>
          </div>
          <button type="submit" class="btn btn-primary">Сохранить</button>
        </form>
      </div>

      <!-- Блок смены Email -->
      <div class="settings-card">
        <h3>Смена Email</h3>
        <form @submit.prevent="handleChangeEmail">
          <div class="form-group">
            <label for="new-email">Новый Email</label>
            <input type="email" id="new-email" v-model="emailForm.new_email" required>
          </div>
          <div class="form-group">
            <label for="email-password">Пароль для подтверждения</label>
            <input type="password" id="email-password" v-model="emailForm.current_password" required>
          </div>
          <button type="submit" class="btn btn-primary">Сохранить</button>
        </form>
      </div>

      <!-- Блок удаления аккаунта -->
      <div class="settings-card danger-zone">
        <h3>Опасная зона</h3>
        <p>Это действие нельзя отменить. Все ваши списки и данные будут удалены навсегда.</p>
        <form @submit.prevent="handleDeleteAccount">
          <div class="form-group">
            <label for="delete-password">Пароль для подтверждения</label>
            <input type="password" id="delete-password" v-model="deletePassword" required>
          </div>
          <button type="submit" class="btn btn-danger">Удалить аккаунт</button>
        </form>
      </div>
    </div>
    
    <!-- Сообщения об успехе или ошибке -->
    <div v-if="authStore.error" class="message error-message">{{ authStore.error }}</div>
    <div v-if="authStore.successMessage" class="message success-message">{{ authStore.successMessage }}</div>

  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();

const passwordForm = ref({
  current_password: '',
  new_password: '',
});

const emailForm = ref({
  new_email: '',
  current_password: '',
});

const deletePassword = ref('');

const handleChangePassword = async () => {
  try {
    await authStore.updatePassword(passwordForm.value);
    passwordForm.value.current_password = '';
    passwordForm.value.new_password = '';
  } catch (e) {
    // Ошибка обработается в сторе
  }
};

const handleChangeEmail = async () => {
  try {
    await authStore.updateEmail(emailForm.value);
    emailForm.value.new_email = '';
    emailForm.value.current_password = '';
  } catch (e) {
    // Ошибка обработается в сторе
  }
};

const handleDeleteAccount = async () => {
  if (confirm('Вы АБСОЛЮТНО уверены? Это действие необратимо.')) {
    try {
      await authStore.deleteAccount(deletePassword.value);
      // Редирект произойдет в сторе
    } catch (e) {
      deletePassword.value = '';
    }
  }
};

// Очищаем сообщения при уходе со страницы
onUnmounted(() => {
  authStore.clearMessages();
});

</script>

<style scoped>
.settings-container {
  max-width: 900px;
  margin: 0 auto;
}
h1 {
  text-align: center;
  margin-bottom: 2rem;
}
.settings-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}
@media (min-width: 768px) {
  .settings-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .danger-zone {
    grid-column: 1 / -1; /* Занимает всю ширину */
  }
}
.settings-card {
  background-color: var(--card-bg-color);
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}
.settings-card h3 {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}
.form-group input {
  width: 100%;
  box-sizing: border-box;
}
.danger-zone {
  border-color: var(--destructive-color);
}
.danger-zone h3 {
  color: var(--destructive-color);
}
.message {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 5px;
  text-align: center;
}
.error-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
.success-message {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
</style>