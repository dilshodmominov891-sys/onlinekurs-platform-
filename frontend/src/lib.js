import axios from 'axios'

const trimSlash = (value = '') => value.replace(/\/+$/, '')

export const apiOrigin = trimSlash(import.meta.env.VITE_API_URL || '')
export const socketURL = trimSlash(import.meta.env.VITE_SOCKET_URL || apiOrigin || window.location.origin)
export const apiBaseURL = `${apiOrigin}/api`

export const apiUrl = (path = '') => {
  const cleanPath = String(path).startsWith('/') ? path : `/${path}`
  return `${apiBaseURL}${cleanPath}`
}

export const resolveAssetUrl = (url = '') => {
  const value = String(url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  if (value.includes('/uploads/')) {
    const relative = `/uploads/${value.split('/uploads/', 2)[1]}`
    return `${apiOrigin}${relative}`
  }
  return apiOrigin ? `${apiOrigin}/${value.replace(/^\/+/, '')}` : value
}

export const api = axios.create({
  baseURL: apiBaseURL,
  withCredentials: true,
  timeout: 15000,
})
