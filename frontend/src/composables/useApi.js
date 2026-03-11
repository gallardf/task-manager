import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

const analyticsApi = axios.create({
  baseURL: import.meta.env.VITE_ANALYTICS_URL
})

function attachInterceptors(instance) {
  instance.interceptors.request.use(
    (config) => {
      const auth = useAuthStore()
      if (auth.accessToken) {
        config.headers.Authorization = `Bearer ${auth.accessToken}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const auth = useAuthStore()
      const originalRequest = error.config

      if (error.response?.status === 401 && !originalRequest._retry && auth.refreshToken) {
        originalRequest._retry = true

        try {
          const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/auth/refresh/`, {
            refresh: auth.refreshToken
          })

          const { access } = response.data
          auth.setTokens(access, auth.refreshToken)
          originalRequest.headers.Authorization = `Bearer ${access}`
          return instance(originalRequest)
        } catch (refreshError) {
          auth.logout()
          router.push('/login')
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )
}

attachInterceptors(api)
attachInterceptors(analyticsApi)

// Backward-compatible aliases
const authApi = api
const taskApi = api

export { api, analyticsApi, authApi, taskApi }
