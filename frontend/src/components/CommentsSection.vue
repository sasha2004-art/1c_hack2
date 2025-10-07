<template>
  <div class="comments-section">
    <div v-if="!isGuest" class="comment-form">
      <textarea
        v-model="newCommentText"
        placeholder="Оставить комментарий..."
        rows="2"
      ></textarea>
      <button @click="submitComment" :disabled="!newCommentText.trim()">
        Отправить
      </button>
    </div>

    <div class="comments-list">
      <div v-if="comments.length === 0" class="no-comments">
        Комментариев пока нет.
      </div>
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-header">
          <span class="comment-author">{{ comment.owner.email }}</span>
          <span class="comment-date">{{
            new Date(comment.created_at).toLocaleString()
          }}</span>
        </div>
        <p class="comment-text">{{ comment.text }}</p>
        <button
          v-if="currentUser && currentUser.id === comment.owner.id"
          @click="handleDeleteComment(comment.id)"
          class="delete-comment-btn"
        >
          Удалить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useListsStore } from '@/store/lists';
import { storeToRefs } from 'pinia';

const props = defineProps({
  itemId: {
    type: Number,
    required: true,
  },
  comments: {
    type: Array,
    required: true,
  },
  isGuest: {
    type: Boolean,
    default: false,
  },
});

const newCommentText = ref('');
const listsStore = useListsStore();
const authStore = useAuthStore();
const { user: currentUser } = storeToRefs(authStore);

const submitComment = async () => {
  if (!newCommentText.value.trim()) return;
  try {
    await listsStore.addComment(props.itemId, newCommentText.value);
    newCommentText.value = '';
  } catch (error) {
    console.error('Failed to add comment:', error);
  }
};

const handleDeleteComment = async (commentId) => {
  if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
    try {
      await listsStore.deleteComment(commentId, props.itemId);
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  }
};
</script>

<style scoped>
.comments-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.comment-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}
.comment-form button {
  align-self: flex-end;
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.comment-form button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
.no-comments {
  color: #888;
  font-style: italic;
}
.comment-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}
.comment-item:last-child {
  border-bottom: none;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}
.comment-author {
  font-weight: bold;
  font-size: 0.9em;
}
.comment-date {
  font-size: 0.8em;
  color: #888;
}
.comment-text {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.delete-comment-btn {
    background: none;
    border: none;
    color: var(--secondary-color);
    cursor: pointer;
    font-size: 0.8em;
    padding: 0.2rem 0;
    margin-top: 0.25rem;
}
</style>