import { http } from './http'

export function parseScript(payload) {
	return http.post('/api/parse-script', payload, { timeout: 600000 })
}

