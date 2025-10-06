<template>
    <div class="list-card">
        <div class="card-header">
            <h3>{{ list.title }}</h3>
            <div class="tags">
                <span class="tag type-tag">{{ list.list_type }}</span>
                <span class="tag privacy-tag">{{ list.privacy_level }}</span>
            </div>
        </div>
        <p class="card-description">{{ list.description || 'Нет описания' }}</p>
        <div class="card-footer">
            <small>Создан: {{ new Date(list.created_at).toLocaleDateString() }}</small>
            <div class="card-actions">
                <button class="secondary" @click="$emit('edit', list)">Редактировать</button>
                <button class="danger" @click="$emit('delete', list.id)">Удалить</button>
            </div>
        </div>
    </div>
</template>

<script setup>
defineProps({
    list: {
        type: Object,
        required: true
    }
});
defineEmits(['edit', 'delete']);
</script>

<style scoped>
.list-card {
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.card-header h3 {
    margin-top: 0;
}
.card-description {
    flex-grow: 1;
    color: #666;
}
.card-footer {
    border-top: 1px solid #f0f0f0;
    padding-top: 1rem;
    margin-top: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #999;
}
.card-actions {
    display: flex;
    gap: 0.5rem;
}
.tags {
    display: flex;
    gap: 0.5rem;
    margin: 0.5rem 0;
}
.tag {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 12px;
    color: white;
}
.type-tag { background-color: #3498db; }
.privacy-tag { background-color: #f39c12; }
</style>