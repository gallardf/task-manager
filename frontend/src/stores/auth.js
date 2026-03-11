import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { jwtDecode } from 'jwt-decode'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))

  const user = computed(() => {
    if (!accessToken.value) return null
    try {
      return jwtDecode(accessToken.value)
    } catch {
      return null
    }
  })

  const permissions = computed(() => user.value?.permissions ?? [])
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  function hasPermission(perm) {
    return permissions.value.includes(perm)
  }

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  return { accessToken, refreshToken, user, permissions, isAuthenticated, hasPermission, setTokens, logout }
})
