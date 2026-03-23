import { requestRaw } from './http'

export function exportVideo(payload) {
	return requestRaw({
		url: '/api/export-video',
		method: 'POST',
		data: payload,
		timeout: 600000,
		responseType: 'arraybuffer',
		header: {
			'Content-Type': 'application/json'
		}
	})
}

