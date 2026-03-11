<template>
  <div class="profile-view">
    <div class="form-card">
      <h1>Mon profil</h1>
      <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="form-info">
          <span class="info-label">Nom d'utilisateur :</span> {{ username }}
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" />
        </div>
        <div class="form-group">
          <label for="first_name">Pr&eacute;nom</label>
          <input id="first_name" v-model="form.first_name" type="text" />
        </div>
        <div class="form-group">
          <label for="last_name">Nom</label>
          <input id="last_name" v-model="form.last_name" type="text" />
        </div>
        <div class="form-info">
          <span class="info-label">R&ocirc;le :</span> {{ role }}
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/composables/useApi'

const form = ref({ email: '', first_name: '', last_name: '' })
const username = ref('')
const role = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/api/users/me/')
    username.value = data.username
    form.value = {
      email: data.email || '',
      first_name: data.first_name || '',
      last_name: data.last_name || '',
    }
    role.value = data.role_name || '-'
  } catch {
    errorMessage.value = 'Erreur lors du chargement du profil.'
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true
  try {
    await api.patch('/api/users/me/', form.value)
    successMessage.value = 'Profil mis à jour.'
  } catch (error) {
    const data = error.response?.data
    if (data && typeof data === 'object') {
      errorMessage.value = Object.values(data).flat().join(' ')
    } else {
      errorMessage.value = 'Erreur lors de la mise à jour.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-view {
  display: flex;
  justify-content: center;
  padding-top: 40px;
}

.form-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 480px;
}

.form-card h1 {
  margin-bottom: 24px;
  font-size: 1.5rem;
  text-align: center;
  color: #1e293b;
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

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-info {
  margin-bottom: 16px;
  color: #64748b;
  font-size: 0.9rem;
}

.info-label {
  font-weight: 600;
  color: #475569;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  margin-top: 8px;
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

.success-message {
  background: #f0fdf4;
  color: #16a34a;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}
</style>
