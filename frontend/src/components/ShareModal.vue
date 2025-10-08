<template>
  <div v-if="isOpen && list" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">&times;</button>
      <h3>Поделиться списком "{{ list.title }}"</h3>

      <div class="share-options">
        <a :href="vkLink" target="_blank" class="share-button vk">ВКонтакте</a>
        <a :href="telegramLink" target="_blank" class="share-button telegram">Telegram</a>
        <a :href="odnoklassnikiLink" target="_blank" class="share-button ok">Одноклассники</a>
        <a :href="whatsappLink" target="_blank" class="share-button whatsapp">WhatsApp</a>
        <a :href="emailLink" class="share-button email">Email</a>
      </div>

      <div class="copy-link-section">
        <input type="text" :value="publicUrl" readonly ref="linkInput" />
        <button @click="copyLink" class="btn-primary">{{ copyButtonText }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  list: Object,
});

defineEmits(['close']);

const copyButtonText = ref('Копировать');
const linkInput = ref(null);

const publicUrl = computed(() => {
  if (!props.list) return '';
  return `${window.location.origin}/public/lists/${props.list.public_url_key}`;
});

const encodedUrl = computed(() => encodeURIComponent(publicUrl.value));
const encodedTitle = computed(() => encodeURIComponent(props.list?.title || 'Мой список'));

const vkLink = computed(() => `https://vk.com/share.php?url=${encodedUrl.value}&title=${encodedTitle.value}`);
const telegramLink = computed(() => `https://t.me/share/url?url=${encodedUrl.value}&text=${encodedTitle.value}`);
const odnoklassnikiLink = computed(() => `https://connect.ok.ru/offer?url=${encodedUrl.value}&title=${encodedTitle.value}`);
const whatsappLink = computed(() => `https://api.whatsapp.com/send?text=${encodedTitle.value}%20${encodedUrl.value}`);
const emailLink = computed(() => `mailto:?subject=${encodedTitle.value}&body=Посмотрите мой список: ${encodedUrl.value}`);

const copyLink = () => {
  if (linkInput.value) {
    linkInput.value.select();
    navigator.clipboard.writeText(publicUrl.value).then(() => {
      copyButtonText.value = 'Скопировано!';
      setTimeout(() => {
        copyButtonText.value = 'Копировать';
      }, 2000);
    });
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: #fff;
  color: #333;
  padding: 1.5rem 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #aaa;
}
h3 {
  text-align: center;
  margin-top: 0;
  margin-bottom: 1.5rem;
}
.share-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.share-button {
  display: block;
  padding: 12px;
  border-radius: 5px;
  color: #fff;
  text-align: center;
  text-decoration: none;
  font-weight: bold;
  transition: opacity 0.2s;
}
.share-button:hover {
  opacity: 0.9;
}
.vk { background-color: #4a76a8; }
.telegram { background-color: #0088cc; }
.ok { background-color: #f58220; }
.whatsapp { background-color: #25d366; }
.email { background-color: #767676; }

.copy-link-section {
  display: flex;
  gap: 0.5rem;
}
.copy-link-section input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f0f0f0;
  font-size: 0.9rem;
}
.copy-link-section button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>