<template>
  <div class="task-card">
    <div class="task-header">
      <h3 class="task-title">{{ task.title }}</h3>
      <div class="task-badges">
        <span class="badge" :class="`badge-${task.status}`">{{ statusLabel }}</span>
        <span class="badge" :class="`badge-priority-${task.priority}`">{{ priorityLabel }}</span>
      </div>
    </div>

    <p v-if="task.description" class="task-description">{{ task.description }}</p>

    <div class="task-meta">
      <div v-if="task.assigned_to" class="meta-item">
        <span class="meta-label">Assigné à :</span> {{ task.assigned_to }}
      </div>
      <div v-if="task.due_date" class="meta-item">
        <span class="meta-label">Échéance :</span> {{ task.due_date }}
      </div>
      <div v-if="task.created_at" class="meta-item">
        <span class="meta-label">Créé le :</span> {{ formatDate(task.created_at) }}
      </div>
    </div>

    <div class="task-actions">
      <button
        v-if="auth.hasPermission('task:update')"
        class="btn btn-sm btn-edit"
        @click="$emit('edit', task)"
      >
        Modifier
      </button>
      <button
        v-if="auth.hasPermission('task:delete')"
        class="btn btn-sm btn-delete"
        @click="$emit('delete', task)"
      >
        Supprimer
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

defineEmits(['edit', 'delete'])

const statusLabels = {
  todo: 'À faire',
  in_progress: 'En cours',
  done: 'Terminé',
  cancelled: 'Annulé'
}

const priorityLabels = {
  low: 'Basse',
  medium: 'Moyenne',
  high: 'Haute',
  urgent: 'Urgente'
}

const statusLabel = computed(() => statusLabels[props.task.status] || props.task.status)
const priorityLabel = computed(() => priorityLabels[props.task.priority] || props.task.priority)

function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString('fr-FR')
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.task-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.2s;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.task-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.task-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-todo { background: #f1f5f9; color: #64748b; }
.badge-in_progress { background: #dbeafe; color: #2563eb; }
.badge-done { background: #dcfce7; color: #16a34a; }
.badge-cancelled { background: #fef2f2; color: #dc2626; }

.badge-priority-low { background: #f0fdf4; color: #22c55e; }
.badge-priority-medium { background: #fefce8; color: #ca8a04; }
.badge-priority-high { background: #fff7ed; color: #ea580c; }
.badge-priority-urgent { background: #fef2f2; color: #dc2626; }

.task-description {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.82rem;
  color: #64748b;
}

.meta-label {
  font-weight: 500;
  color: #475569;
}

.task-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.btn {
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}

.btn-sm {
  padding: 5px 12px;
  font-size: 0.8rem;
}

.btn-edit {
  background: #e2e8f0;
  color: #334155;
}

.btn-edit:hover {
  background: #cbd5e1;
}

.btn-delete {
  background: #fef2f2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #fee2e2;
}
</style>
