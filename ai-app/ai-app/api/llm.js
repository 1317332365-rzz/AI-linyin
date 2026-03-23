import { http } from './http'

export function getLLMConfig(process = 'general') {
	return http.get('/api/llm-config', { process })
}

export function updateLLMConfig(payload) {
	return http.post('/api/llm-config', payload)
}

export function testLLM(payload) {
	return http.post('/api/test-llm', payload, { timeout: 120000 })
}

