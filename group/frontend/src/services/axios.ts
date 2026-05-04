import axios from 'axios'

const baseURL =
  (window as any).APP_URL || import.meta.env.VITE_APP_URL || ''

export const apiClient = axios.create({
  baseURL: String(baseURL).replace(/\/$/, ''),
  headers: {
    Accept: 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
})

// Optional: global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.response?.data?.error ||
      error.message

    return Promise.reject(new Error(message))
  }
)
