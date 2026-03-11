<template>
  <div class="admin-users-view">
    <div class="header">
      <h1>Gestion des utilisateurs</h1>
      <button class="btn btn-primary" @click="showCreateForm = !showCreateForm">
        {{ showCreateForm ? 'Annuler' : 'Nouvel utilisateur' }}
      </button>
    </div>

    <div v-if="showCreateForm" class="create-form">
      <h2>Créer un utilisateur</h2>
      <div v-if="createError" class="error-message">{{ createError }}</div>
      <form @submit.prevent="createUser">
        <div class="form-row">
          <div class="form-group">
            <label for="new-username">Nom d'utilisateur</label>
            <input id="new-username" v-model="newUser.username" type="text" required placeholder="Nom d'utilisateur" />
          </div>
          <div class="form-group">
            <label for="new-password">Mot de passe</label>
            <input id="new-password" v-model="newUser.password" type="password" required placeholder="Mot de passe" minlength="6" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="new-first-name">Prénom</label>
            <input id="new-first-name" v-model="newUser.first_name" type="text" placeholder="Prénom" />
          </div>
          <div class="form-group">
            <label for="new-last-name">Nom</label>
            <input id="new-last-name" v-model="newUser.last_name" type="text" placeholder="Nom" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="new-email">Email (optionnel)</label>
            <input id="new-email" v-model="newUser.email" type="email" placeholder="email@example.com" />
          </div>
          <div class="form-group">
            <label for="new-role">Rôle</label>
            <select id="new-role" v-model="newUser.role" required>
              <option :value="null" disabled>-- Sélectionner --</option>
              <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="creating">
          {{ creating ? 'Création...' : 'Créer' }}
        </button>
      </form>
    </div>

    <div v-if="loading" class="loading">Chargement...</div>

    <div v-else-if="users.length === 0" class="empty-state">
      Aucun utilisateur trouvé
    </div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Utilisateur</th>
          <th>Prénom</th>
          <th>Nom</th>
          <th>Rôle</th>
          <th>Actif</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.first_name }}</td>
          <td>{{ user.last_name }}</td>
          <td>
            <select
              :value="user.role"
              class="role-select"
              :disabled="user.role_name === 'admin'"
              @change="updateRole(user, Number($event.target.value))"
            >
              <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </td>
          <td>
            <button
              class="btn-toggle"
              :class="user.is_active ? 'active' : 'inactive'"
              :disabled="user.role_name === 'admin'"
              @click="toggleActive(user)"
            >
              {{ user.is_active ? 'Actif' : 'Inactif' }}
            </button>
          </td>
          <td>
            <span v-if="user._saving" class="saving-indicator">...</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { authApi } from '@/composables/useApi'

const users = ref([])
const roles = ref([])
const loading = ref(true)
const showCreateForm = ref(false)
const creating = ref(false)
const createError = ref('')

const newUser = reactive({
  username: '',
  password: '',
  first_name: '',
  last_name: '',
  email: '',
  role: null
})

onMounted(async () => {
  try {
    const [usersRes, rolesRes] = await Promise.all([
      authApi.get('/api/users/'),
      authApi.get('/api/roles/')
    ])
    users.value = (Array.isArray(usersRes.data) ? usersRes.data : usersRes.data.results || []).map(u => ({
      ...u,
      _saving: false
    }))
    roles.value = Array.isArray(rolesRes.data) ? rolesRes.data : rolesRes.data.results || []
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
})

async function createUser() {
  createError.value = ''
  creating.value = true
  try {
    const res = await authApi.post('/api/users/', newUser)
    users.value.push({ ...res.data, _saving: false })
    showCreateForm.value = false
    newUser.username = ''
    newUser.password = ''
    newUser.first_name = ''
    newUser.last_name = ''
    newUser.email = ''
    newUser.role = null
  } catch (error) {
    const data = error.response?.data
    if (data && typeof data === 'object') {
      const messages = []
      for (const key in data) {
        const val = Array.isArray(data[key]) ? data[key].join(', ') : data[key]
        messages.push(`${key}: ${val}`)
      }
      createError.value = messages.join(' | ')
    } else {
      createError.value = "Erreur lors de la création"
    }
  } finally {
    creating.value = false
  }
}

async function updateRole(user, newRole) {
  user._saving = true
  try {
    await authApi.patch(`/api/users/${user.id}/`, { role: newRole })
    user.role = newRole
    user.role_name = roles.value.find(r => r.id === newRole)?.name
  } catch (error) {
    console.error('Failed to update role:', error)
    alert('Erreur lors de la mise à jour du rôle')
  } finally {
    user._saving = false
  }
}

async function toggleActive(user) {
  user._saving = true
  try {
    const newStatus = !user.is_active
    await authApi.patch(`/api/users/${user.id}/`, { is_active: newStatus })
    user.is_active = newStatus
  } catch (error) {
    console.error('Failed to toggle active status:', error)
    alert("Erreur lors de la mise à jour du statut")
  } finally {
    user._saving = false
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 1.75rem;
  color: #1e293b;
  margin: 0;
}

.create-form {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.create-form h2 {
  font-size: 1.2rem;
  color: #1e293b;
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #475569;
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 0.9rem;
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

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tbody tr:hover {
  background: #f8fafc;
}

.role-select {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.85rem;
  background: #fff;
}

.btn-toggle {
  padding: 4px 12px;
  border: none;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-toggle.active {
  background: #dcfce7;
  color: #16a34a;
}

.btn-toggle.inactive {
  background: #fef2f2;
  color: #dc2626;
}

.saving-indicator {
  color: #94a3b8;
}
</style>
