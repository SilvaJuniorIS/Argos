import axios from 'axios'

const fallbackBaseURL = import.meta.env.DEV ? 'http://localhost:8000' : ''
export const apiBaseURL = import.meta.env.VITE_API_URL || fallbackBaseURL
export const apiDocsURL = apiBaseURL ? `${apiBaseURL.replace(/\/$/, '')}/docs` : '/docs'

const api = axios.create({
  baseURL: apiBaseURL,
})

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (!axios.isAxiosError(error)) return fallback
  const status = error.response?.status
  const detail = error.response?.data?.detail

  if (status === 0 || error.code === 'ERR_NETWORK') {
    return 'Nao foi possivel conectar ao backend. Verifique se a API esta ativa.'
  }
  if (status === 422) {
    return 'Revise os dados informados. Alguns campos estao ausentes ou fora do formato esperado.'
  }
  if (status === 503) {
    return typeof detail === 'string'
      ? detail
      : 'Servico temporariamente indisponivel. Verifique a configuracao do backend.'
  }
  if (status === 504) {
    return 'A geracao demorou mais que o esperado. Tente novamente em instantes.'
  }
  if (typeof detail === 'string' && detail.trim()) return detail
  return fallback
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('argos_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('argos_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
