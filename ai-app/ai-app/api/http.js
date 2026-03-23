import { clearAuthSession, getAuthToken, getBaseUrl } from '../utils/storage'

function isObject(value) {
	return value && typeof value === 'object' && !Array.isArray(value)
}

function encodeParams(params = {}) {
	const items = []
	Object.keys(params || {}).forEach((key) => {
		const value = params[key]
		if (value === undefined || value === null || value === '') {
			return
		}
		items.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
	})
	return items.join('&')
}

function buildHeaders(extraHeader = {}, method = 'GET', withAuth = true) {
	const header = { ...extraHeader }
	const token = withAuth ? getAuthToken() : ''
	if (token) {
		header.Authorization = `Bearer ${token}`
	}
	if (!header['Content-Type'] && method !== 'GET') {
		header['Content-Type'] = 'application/json'
	}
	return header
}

function buildRequestUrl(url = '') {
	const baseUrl = getBaseUrl().replace(/\/+$/, '')
	let requestPath = String(url || '').trim()
	if (!requestPath) {
		return baseUrl
	}
	if (!requestPath.startsWith('/')) {
		requestPath = `/${requestPath}`
	}
	if (baseUrl.endsWith('/api') && requestPath.startsWith('/api/')) {
		requestPath = requestPath.slice(4)
	}
	return `${baseUrl}${requestPath}`
}

function translateErrorMessage(message = '', statusCode = 0) {
	const text = String(message || '').trim()
	const translatedMap = {
		Unauthorized: '登录状态已失效，请重新登录',
		unauthorized: '登录状态已失效，请重新登录',
		'Invalid email or password': '邮箱或密码错误',
		'Email already exists': '该邮箱已注册',
		'Email is required': '请输入邮箱地址',
		'Please enter a valid email address': '请输入正确的邮箱地址',
		'Password is required': '请输入密码',
		'Password must be at least 6 characters': '密码至少 6 位',
		'Password must be 128 characters or fewer': '密码不能超过 128 位'
	}
	if (translatedMap[text]) {
		return translatedMap[text]
	}
	if (statusCode === 401 && !text) {
		return '登录状态已失效，请重新登录'
	}
	return text
}

function normalizeError({ statusCode = 0, data = null, message = '' } = {}) {
	const payloadMessage =
		(isObject(data) && (data.error || data.message || data.detail)) ||
		message ||
		(statusCode ? `请求失败 (${statusCode})` : '网络请求失败')
	return {
		statusCode,
		data,
		message: translateErrorMessage(payloadMessage, statusCode) || '请求失败'
	}
}

function shouldClearAuthBy401(statusCode = 0, data = null, withAuth = true) {
	if (!withAuth || Number(statusCode) !== 401) {
		return false
	}
	if (!isObject(data)) {
		return false
	}
	const code = String(data.code || '').trim().toUpperCase()
	if (code === 'AUTH_REQUIRED') {
		return true
	}
	const message = String(data.error || data.message || data.detail || '')
		.trim()
		.toLowerCase()
	if (!message) {
		return false
	}
	return ['unauthorized', 'invalid token', 'token expired'].includes(message)
}

export function requestRaw(options = {}) {
	const {
		url = '',
		method = 'GET',
		data = null,
		params = null,
		header = {},
		timeout = 60000,
		responseType = 'text',
		withAuth = true
	} = options

	const queryString = params ? encodeParams(params) : ''
	const fullUrl = `${buildRequestUrl(url)}${queryString ? `?${queryString}` : ''}`

	return new Promise((resolve, reject) => {
		uni.request({
			url: fullUrl,
			method,
			data,
			timeout,
			responseType,
			header: buildHeaders(header, method, withAuth),
			success: (response) => {
				const statusCode = Number(response.statusCode || 0)
				if (statusCode >= 200 && statusCode < 300) {
					resolve(response)
					return
				}
				if (shouldClearAuthBy401(statusCode, response.data, withAuth)) {
					clearAuthSession()
				}
				reject(normalizeError({ statusCode, data: response.data }))
			},
			fail: (error) => {
				reject(
					normalizeError({
						message: error && error.errMsg ? error.errMsg : '网络请求失败'
					})
				)
			}
		})
	})
}

export function request(options = {}) {
	return requestRaw(options).then((response) => response.data)
}

export const http = {
	get(url, params = null, options = {}) {
		return request({ ...options, url, method: 'GET', params })
	},
	post(url, data = {}, options = {}) {
		return request({ ...options, url, method: 'POST', data })
	},
	put(url, data = {}, options = {}) {
		return request({ ...options, url, method: 'PUT', data })
	}
}
