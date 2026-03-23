function safeText(value) {
	return String(value || '').trim()
}

function isBrowser() {
	return typeof window !== 'undefined' && typeof document !== 'undefined'
}

export function resolveFilename(disposition, fallback = 'download.bin') {
	const source = safeText(disposition)
	if (!source) {
		return fallback
	}
	const utf8Match = source.match(/filename\*=UTF-8''([^;]+)/i)
	if (utf8Match && utf8Match[1]) {
		try {
			return decodeURIComponent(utf8Match[1])
		} catch (error) {
			return utf8Match[1]
		}
	}
	const basicMatch = source.match(/filename="?([^"]+)"?/i)
	return basicMatch && basicMatch[1] ? basicMatch[1] : fallback
}

export function downloadBinaryInBrowser(data, filename, mimeType = 'application/octet-stream') {
	if (!isBrowser()) {
		return false
	}
	const blob = new Blob([data], { type: mimeType })
	const link = document.createElement('a')
	const url = window.URL.createObjectURL(blob)
	link.href = url
	link.download = filename
	document.body.appendChild(link)
	link.click()
	document.body.removeChild(link)
	setTimeout(() => window.URL.revokeObjectURL(url), 0)
	return true
}

export function downloadTextInBrowser(content, filename, mimeType = 'text/plain;charset=utf-8') {
	if (!isBrowser()) {
		return false
	}
	const blob = new Blob([content], { type: mimeType })
	const link = document.createElement('a')
	const url = window.URL.createObjectURL(blob)
	link.href = url
	link.download = filename
	document.body.appendChild(link)
	link.click()
	document.body.removeChild(link)
	setTimeout(() => window.URL.revokeObjectURL(url), 0)
	return true
}

