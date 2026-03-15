<template>
  <div class="task-form-view">
    <h1>{{ isEditMode ? 'Modifier la tâche' : 'Nouvelle tâche' }}</h1>

    <div v-if="loadingTask" class="loading">Chargement...</div>

    <div v-else class="form-card">
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">Titre</label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            required
            placeholder="Titre de la tâche"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            rows="4"
            placeholder="Description de la tâche"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="status">Statut</label>
            <select id="status" v-model="form.status">
              <option value="todo">À faire</option>
              <option value="in_progress">En cours</option>
              <option value="done">Terminé</option>
              <option value="cancelled">Annulé</option>
            </select>
          </div>

          <div class="form-group">
            <label for="priority">Priorité</label>
            <select id="priority" v-model="form.priority">
              <option value="low">Basse</option>
              <option value="medium">Moyenne</option>
              <option value="high">Haute</option>
              <option value="urgent">Urgente</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="assigned_to">Assigné à</label>
            <select id="assigned_to" v-model="form.assigned_to" required>
              <option :value="null" disabled>-- Sélectionner un utilisateur --</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.username }} ({{ u.first_name }} {{ u.last_name }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="due_date">Date d'échéance</label>
            <input
              id="due_date"
              v-model="form.due_date"
              type="date"
            />
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="$router.push('/tasks')">
            Annuler
          </button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/composables/useApi'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => !!route.params.id)
const loadingTask = ref(false)
const saving = ref(false)
const errorMessage = ref('')

const users = ref([])

const form = reactive({
  title: '',
  description: '',
  status: 'todo',
  priority: 'medium',
  assigned_to: null,
  due_date: ''
})

onMounted(async () => {
  try {
    const usersRes = await api.get('/api/users/')
    users.value = Array.isArray(usersRes.data) ? usersRes.data : usersRes.data.results || []
  } catch (err) {
    console.warn('Could not load users list:', err.response?.status, err.message)
  }

  if (isEditMode.value) {
    loadingTask.value = true
    try {
      const response = await api.get(`/api/tasks/${route.params.id}/`)
      const task = response.data
      form.title = task.title || ''
      form.description = task.description || ''
      form.status = task.status || 'todo'
      form.priority = task.priority || 'medium'
      form.assigned_to = task.assigned_to || null
      form.due_date = task.due_date || ''
    } catch (error) {
      errorMessage.value = 'Erreur lors du chargement de la tâche'
    } finally {
      loadingTask.value = false
    }
  }
})

async function handleSubmit() {
  errorMessage.value = ''

  if (!form.assigned_to) {
    errorMessage.value = 'Veuillez sélectionner un utilisateur à assigner.'
    return
  }

  saving.value = true

  const payload = { ...form }
  if (!payload.due_date) delete payload.due_date

  try {
    if (isEditMode.value) {
      await api.put(`/api/tasks/${route.params.id}/`, payload)
    } else {
      await api.post('/api/tasks/', payload)
    }
    router.push('/tasks')
  } catch (error) {
    const data = error.response?.data
    if (data && typeof data === 'object') {
      const messages = []
      for (const key in data) {
        const val = Array.isArray(data[key]) ? data[key].join(', ') : data[key]
        messages.push(`${key}: ${val}`)
      }
      errorMessage.value = messages.join(' | ')
    } else {
      errorMessage.value = "Erreur lors de l'enregistrement"
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.task-form-view h1 {
  font-size: 1.75rem;
  color: #1e293b;
  margin-bottom: 24px;
}

.form-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 32px;
  max-width: 700px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #475569;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #e2e8f0;
  color: #334155;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}
</style>
