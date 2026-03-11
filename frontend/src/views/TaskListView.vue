<template>
  <div class="task-list-view">
    <div class="header">
      <h1>Tâches</h1>
      <router-link
        v-if="auth.hasPermission('task:create')"
        to="/tasks/new"
        class="btn btn-primary"
      >
        + Nouvelle tâche
      </router-link>
    </div>

    <TaskFilters @filter-change="handleFilterChange" />

    <div v-if="loading" class="loading">Chargement...</div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      Aucune tâche trouvée
    </div>

    <div v-else class="task-grid">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @edit="editTask"
        @delete="deleteTask"
      />
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button
        :disabled="currentPage <= 1"
        class="btn btn-sm"
        @click="goToPage(currentPage - 1)"
      >
        Précédent
      </button>
      <span class="page-info">Page {{ currentPage }} / {{ totalPages }}</span>
      <button
        :disabled="currentPage >= totalPages"
        class="btn btn-sm"
        @click="goToPage(currentPage + 1)"
      >
        Suivant
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { taskApi } from '@/composables/useApi'
import TaskCard from '@/components/TaskCard.vue'
import TaskFilters from '@/components/TaskFilters.vue'

const router = useRouter()
const auth = useAuthStore()

const tasks = ref([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const filters = ref({})

async function fetchTasks() {
  loading.value = true
  try {
    const params = { page: currentPage.value, ...filters.value }
    // Remove empty params
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })
    const response = await taskApi.get('/api/tasks/', { params })
    if (Array.isArray(response.data)) {
      tasks.value = response.data
      totalPages.value = 1
    } else {
      tasks.value = response.data.results || []
      const count = response.data.count || 0
      const pageSize = response.data.page_size || 10
      totalPages.value = Math.ceil(count / pageSize) || 1
    }
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    loading.value = false
  }
}

function handleFilterChange(newFilters) {
  filters.value = newFilters
  currentPage.value = 1
  fetchTasks()
}

function goToPage(page) {
  currentPage.value = page
  fetchTasks()
}

function editTask(task) {
  router.push(`/tasks/${task.id}/edit`)
}

async function deleteTask(task) {
  if (!confirm(`Supprimer la tâche "${task.title}" ?`)) return
  try {
    await taskApi.delete(`/api/tasks/${task.id}/`)
    fetchTasks()
  } catch (error) {
    console.error('Failed to delete task:', error)
    alert('Erreur lors de la suppression')
  }
}

onMounted(fetchTasks)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 1.75rem;
  color: #1e293b;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
}

.btn-primary:hover {
  background: #2563eb;
  text-decoration: none;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 0.85rem;
  background: #e2e8f0;
  color: #334155;
}

.btn-sm:hover:not(:disabled) {
  background: #cbd5e1;
}

.btn-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
  background: #fff;
  border-radius: 8px;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px;
}

.page-info {
  color: #64748b;
  font-size: 0.9rem;
}
</style>
