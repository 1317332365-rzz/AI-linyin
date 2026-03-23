import { http } from './http'

export function listProjects() {
	return http.get('/api/projects')
}

export function createProject(payload) {
	return http.post('/api/projects', payload)
}

export function getProject(projectId) {
	return http.get(`/api/projects/${encodeURIComponent(projectId)}`)
}

export function updateProject(projectId, payload) {
	return http.put(`/api/projects/${encodeURIComponent(projectId)}`, payload)
}

