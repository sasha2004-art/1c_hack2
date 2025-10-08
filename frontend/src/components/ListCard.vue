<template>
  <div class="list-card" :style="cardStyle">
    <div class="card-content" @click="navigateToList">
      <h3 class="card-title">{{ list.title }}</h3>
      <p class="card-description">{{ list.description }}</p>
    </div>
    <div class="card-footer">
      <div class="card-tags">
        <span class="tag tag-type">{{ translatedType }}</span>
        <span class="tag tag-privacy">{{ translatedPrivacy }}</span>
      </div>
      <div class="card-actions">
        <button 
          v-if="list.privacy_level === 'public' || list.privacy_level === 'friends_only'" 
          @click.stop="$emit('share', list)"
          class="action-btn share-btn" 
          title="Скопировать ссылку для общего доступа">
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

defineEmits(['edit', 'delete', 'share']);

const router = useRouter();

const cardStyle = computed(() => {
  const theme = themes[props.list.theme_name] || themes.default;
  return theme.styles;
});

const typeTranslations = {
  wishlist: 'Желания',
  todo: 'Дела',
  books: 'Книги',
  movies: 'Фильмы'
};

const privacyTranslations = {
  private: 'Приватный',
  public: 'Публичный',
  friends_only: 'Для друзей'
};

const translatedType = computed(() => typeTranslations[props.list.list_type] || props.list.list_type);
const translatedPrivacy = computed(() => privacyTranslations[props.list.privacy_level] || props.list.privacy_level);

const navigateToList = () => {
  router.push({ name: 'ListView', params: { id: props.list.id } });
};
</script>

<style scoped>
.list-card {
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  box-shadow: var(--shadow-1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg-color);
  color: var(--text-color);
  min-height: 220px; /* Give it a minimum height */
}

.list-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-2);
  border-color: rgba(155, 135, 245, 0.3);
}

.card-content {
  padding: var(--space-lg);
  cursor: pointer;
  flex-grow: 1;
}

.card-title {
  margin: 0 0 var(--space-sm) 0;
  font-size: 18px;
  font-weight: 600;
}

.card-description {
  margin: 0;
  opacity: 0.75;
  font-size: 14px;
  line-height: 1.5;
  /* Truncate long descriptions */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) var(--space-lg);
  border-top: 1px solid var(--border-color);
  background-color: rgba(0,0,0,0.02);
}

.card-tags {
  display: flex;
  gap: var(--space-sm);
}

.tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background-color: rgba(155, 135, 245, 0.15);
  color: #7c64d4;
}

.tag-privacy {
  background-color: rgba(0, 0, 0, 0.05);
  color: rgba(0, 0, 0, 0.6);
}

.card-actions {
  display: flex;
  gap: var(--space-sm);
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 20px;
  opacity: 0.6;
  transition: opacity 0.2s, transform 0.2s;
  padding: 4px;
}

.action-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}
</style>