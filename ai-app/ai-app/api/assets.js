import { http } from './http'

export function enhancePrompt(payload) {
	return http.post('/api/enhance-prompt', payload)
}

export function generateCharacter(payload) {
	return http.post('/api/generate-character', payload, { timeout: 600000 })
}

export function generateScene(payload) {
	return http.post('/api/generate-scene', payload, { timeout: 600000 })
}

