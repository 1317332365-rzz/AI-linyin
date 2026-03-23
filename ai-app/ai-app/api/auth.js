import { http } from './http'

export function login(payload) {
	return http.post('/api/auth/login', payload, { withAuth: false })
}

export function register(payload) {
	return http.post('/api/auth/register', payload, { withAuth: false })
}

export function logout() {
	return http.post('/api/auth/logout', {})
}

export function authStatus() {
	return http.get('/api/auth/status')
}
