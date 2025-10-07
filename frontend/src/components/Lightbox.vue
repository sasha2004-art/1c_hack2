<!-- frontend/src/components/Lightbox.vue -->
<template>
  <div v-if="visible" class="lightbox-overlay" @click.self="close">
    <div class="lightbox-content">
      <img :src="imageUrl" alt="Full size view">
      <button @click="close" class="close-button">&times;</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  imageUrl: String,
  visible: Boolean
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.lightbox-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-content img {
  max-width: 100%;
  max-height: 100%;
  border-radius: 4px;
}

.close-button {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: black;
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(255, 255, 255, 1);
}
</style>