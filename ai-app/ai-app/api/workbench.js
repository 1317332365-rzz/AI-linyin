import { http } from './http'

export function generateVideo(payload) {
	return http.post('/api/generate-video', payload, { timeout: 600000 })
}

export function queryVideoTask(taskId, params = {}) {
	return http.get(`/api/generate-video/tasks/${encodeURIComponent(taskId)}`, params)
}

