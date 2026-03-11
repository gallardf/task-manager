<template>
  <nav class="navbar" v-if="auth.isAuthenticated">
    <div class="navbar-inner">
      <div class="navbar-brand">
        <router-link to="/tasks" class="brand-link">Task Manager</router-link>
      </div>

      <div class="navbar-links">
        <router-link to="/tasks" class="nav-link">Tâches</router-link>
        <router-link
          v-if="auth.hasPermission('analytics:read')"
          to="/dashboard"
          class="nav-link"
        >
          Tableau de bord
        </router-link>
        <router-link
          v-if="auth.user?.role === 'admin'"
          to="/admin/users"
          class="nav-link"
        >
          Utilisateurs
        </router-link>
      </div>

      <div class="navbar-user">
        <span class="user-email">{{ auth.user?.username }}</span>
        <button class="btn-logout" @click="handleLogout">Déconnexion</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  background: #1e293b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 56px;
}

.brand-link {
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
}

.brand-link:hover {
  text-decoration: none;
  color: #e2e8f0;
}

.navbar-links {
  display: flex;
  gap: 4px;
  margin-left: 32px;
  flex: 1;
}

.nav-link {
  color: #cbd5e1;
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s, color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #334155;
  color: #fff;
  text-decoration: none;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-email {
  color: #94a3b8;
  font-size: 0.85rem;
}

.btn-logout {
  padding: 6px 14px;
  background: transparent;
  color: #f87171;
  border: 1px solid #f87171;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-logout:hover {
  background: rgba(248, 113, 113, 0.1);
}
</style>
