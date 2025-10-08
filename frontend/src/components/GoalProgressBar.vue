<template>
  <div class="goal-progress-bar-wrapper">
    <div class="progress-info">
      <span class="progress-label">{{ getLabel() }}</span>
      <span class="progress-values">{{ getProgressText() }}</span>
    </div>
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: getProgressPercentage() + '%' }"></div>
    </div>

    <!-- (ИЗМЕНЕНИЕ) Условные кнопки действий -->
    <div class="actions">
      <!-- Кнопки для Привычки (+1 / -1) -->
      <template v-if="tracker.goal_type === 'check_in'">
        <button
          @click="$emit('log-value-change', -1)"
          :disabled="tracker.current_value <= 0"
          class="log-button habit-button"
          title="Отменить отметку"
        >
          -
        </button>
        <button @click="$emit('log-value-change', 1)" class="log-button habit-button" title="Отметить выполнение">
          +
        </button>
      </template>

      <!-- Кнопка для Прогресса (открывает модал) -->
      <button v-else @click="$emit('open-log-modal')" class="log-button" title="Записать прогресс">
        +
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  tracker: {
    type: Object,
    required: true,
  },
});

// (ИЗМЕНЕНИЕ) Определяем новые события
defineEmits(['open-log-modal', 'log-value-change']);

const getLabel = () => {
  return props.tracker.goal_type === 'cumulative' ? 'Прогресс:' : 'Привычка:';
};

const getProgressPercentage = () => {
  const target = props.tracker.target_value || props.tracker.target_count || 1;
  if (target === 0) return 0;
  const percentage = (props.tracker.current_value / target) * 100;
  return Math.min(percentage, 100); // Не позволяем превышать 100%
};

const getProgressText = () => {
  const current = Math.round(props.tracker.current_value * 10) / 10; // Округляем до 1 знака после запятой
  if (props.tracker.goal_type === 'cumulative') {
    return `${current} / ${props.tracker.target_value} ${props.tracker.unit_name || ''}`;
  }
  return `${Math.floor(current)} / ${props.tracker.target_count} ${props.tracker.unit_name || 'раз'}`;
};
</script>

<style scoped>
.goal-progress-bar-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
}
.progress-info {
  flex-grow: 1;
  font-size: 0.8rem;
}
.progress-label {
  font-weight: bold;
  display: block;
  margin-bottom: 2px;
  color: var(--text-color);
  opacity: 0.9;
}
.progress-values {
  color: var(--text-color);
  opacity: 0.7;
}
.progress-bar-container {
  width: 100%;
  height: 8px;
  background-color: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  flex-basis: 50%;
}
.progress-bar {
  height: 100%;
  background-color: var(--primary-color);
  border-radius: 4px;
  transition: width 0.3s ease-in-out;
}
/* (ИЗМЕНЕНИЕ) Стили для контейнера кнопок */
.actions {
  display: flex;
  gap: 5px;
}
.log-button {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}
.log-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #6c757d;
}
.habit-button {
  padding-bottom: 3px;
}
</style>