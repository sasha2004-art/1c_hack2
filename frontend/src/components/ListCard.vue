<template>
  <div class="list-card" :style="cardStyle">
    <div class="card-content" @click="navigateToList">
      <h3 class="card-title">{{ list.title }}</h3>
      <p class="card-description">{{ list.description }}</p>
    </div>
    <div class="card-footer">
      <div class="card-tags">
        <!-- ИЗМЕНЕНИЕ: Отображаем переведенные теги -->
        <span class="tag tag-type">{{ translatedType }}</span>
        <span class="tag tag-privacy">{{ translatedPrivacy }}</span>
      </div>
      <!-- ИЗМЕНЕНИЕ: Добавлены кнопки, которые вызывают события -->
      <div class="card-actions">
        <!-- НОВАЯ КНОПКА "ПОДЕЛИТЬСЯ" -->
        <button 
          v-if="list.privacy_level === 'public'" 
          @click.stop="copyPublicLink" 
          class="action-btn share-btn" 
          title="Скопировать публичную ссылку">
          🔗
        </button>
        <button @click.stop="$emit('edit', list)" class="action-btn" title="Редактировать">✏️</button>
        <button @click.stop="$emit('delete', list.id)" class="action-btn" title="Удалить">🗑️</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { themes } from '../themes.js';

const props = defineProps({
  list: {
    type: Object,
    required: true
  }
});

// ИЗМЕНЕНИЕ: Определяем события, которые компонент может отправлять
defineEmits(['edit', 'delete']);

const router = useRouter();

// Применяем стили из темы к карточке
const cardStyle = computed(() => {
  const theme = themes[props.list.theme_name] || themes.default;
  return theme.styles;
});

// --- ИЗМЕНЕНИЕ: Логика перевода тегов ---
const typeTranslations = {
  wishlist: 'Желания',
  todo: 'Дела',
  books: 'Книги',
  movies: 'Фильмы'
};

const privacyTranslations = {
  private: 'Приватный',
  public: 'Публичный'
};

const translatedType = computed(() => typeTranslations[props.list.list_type] || props.list.list_type);
const translatedPrivacy = computed(() => privacyTranslations[props.list.privacy_level] || props.list.privacy_level);
// --- Конец логики перевода ---

const navigateToList = () => {
  router.push({ name: 'ListView', params: { id: props.list.id } });
};

// НОВАЯ ФУНКЦИЯ ДЛЯ КОПИРОВАНИЯ ССЫЛКИ
const copyPublicLink = () => {
  const publicKey = props.list.public_url_key;
  // window.location.origin дает нам "http://localhost" или домен сайта в продакшене
  const publicUrl = `${window.location.origin}/public/lists/${publicKey}`;
  
  navigator.clipboard.writeText(publicUrl).then(() => {
    alert('Публичная ссылка скопирована в буфер обмена!');
  }).catch(err => {
    console.error('Не удалось скопировать ссылку: ', err);
    alert('Не удалось скопировать ссылку.');
  });
};
</script>

<style scoped>
.list-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg-color);
  color: var(--text-color);
}

.list-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.card-content {
  padding: 1.5rem;
  cursor: pointer;
  flex-grow: 1;
}

.card-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}

.card-description {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid var(--border-color);
  background-color: rgba(0,0,0,0.02);
}

.card-tags {
  display: flex;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  opacity: 0.9;
}

.tag-type {
  background-color: var(--edit-color);
  color: var(--edit-text-color);
}

.tag-privacy {
  background-color: #e9ecef;
  color: #495057;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 1;
}

.share-btn {
  font-size: 1.1rem; /* Можно настроить размер иконки */
}
</style>