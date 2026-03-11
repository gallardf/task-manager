import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import TaskListView from '@/views/TaskListView.vue'
import TaskFormView from '@/views/TaskFormView.vue'
import AdminUsersView from '@/views/AdminUsersView.vue'
import ProfileView from '@/views/ProfileView.vue'

const routes = [
  {
    path: '/',
    redirect: '/tasks'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, requiredPermission: 'analytics:read' }
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: TaskListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/new',
    name: 'TaskCreate',
    component: TaskFormView,
    meta: { requiresAuth: true, requiredPermission: 'task:create' }
  },
  {
    path: '/tasks/:id/edit',
    name: 'TaskEdit',
    component: TaskFormView,
    meta: { requiresAuth: true, requiredPermission: 'task:update' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsersView,
    meta: { requiresAuth: true, adminOnly: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.adminOnly && (!auth.user || auth.user.role !== 'admin')) {
    return next('/tasks')
  }

  if (to.meta.requiredPermission && !auth.hasPermission(to.meta.requiredPermission)) {
    return next('/tasks')
  }

  next()
})

export default router
