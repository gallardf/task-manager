<template>
  <div class="task-filters">
    <div class="filter-group">
      <label for="filter-status">Statut</label>
      <select id="filter-status" v-model="status" @change="emitFilters">
        <option value="">Tous</option>
        <option value="todo">À faire</option>
        <option value="in_progress">En cours</option>
        <option value="done">Terminé</option>
        <option value="cancelled">Annulé</option>
      </select>
    </div>

    <div class="filter-group">
      <label for="filter-priority">Priorité</label>
      <select id="filter-priority" v-model="priority" @change="emitFilters">
        <option value="">Toutes</option>
        <option value="low">Basse</option>
        <option value="medium">Moyenne</option>
        <option value="high">Haute</option>
        <option value="urgent">Urgente</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['filter-change'])

const status = ref('')
const priority = ref('')

function emitFilters() {
  emit('filter-change', {
    status: status.value || undefined,
    priority: priority.value || undefined
  })
}
</script>

<style scoped>
.task-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #475569;
  white-space: nowrap;
}

.filter-group select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.85rem;
  background: #fff;
  color: #334155;
  min-width: 120px;
}

.filter-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>
