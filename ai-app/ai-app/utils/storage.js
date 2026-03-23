import { APP_CONFIG } from '../config/app'

const STORAGE_KEYS = {
	authToken: 'cinegen_mobile_auth_token',
	authUser: 'cinegen_mobile_auth_user',
	currentProjectId: 'cinegen_mobile_current_project_id',
	projectCache: 'cinegen_mobile_current_project_cache',
	studioView: 'cinegen_mobile_studio_view'
}

const DEFAULT_BASE_URL = APP_CONFIG.apiBaseUrl

function safeGet(key) {
	try {
		return uni.getStorageSync(key)
	} catch (error) {
		return ''
	}
}

function safeSet(key, value) {
	try {
		uni.setStorageSync(key, value)
	} catch (error) {
		// ignore storage write failures
	}
}

function safeRemove(key) {
	try {
		uni.removeStorageSync(key)
	} catch (error) {
		// ignore storage remove failures
	}
}

function toTrimmedString(value) {
	return String(value || '').trim()
}

function resolveUserScope(username = '') {
	return toTrimmedString(username) || toTrimmedString(safeGet(STORAGE_KEYS.authUser)) || 'guest'
}

function scopedKey(baseKey, username = '') {
	return `${baseKey}:${resolveUserScope(username)}`
}

export function normalizeBaseUrl(value) {
	let url = toTrimmedString(value)
	if (!url) {
		return DEFAULT_BASE_URL
	}
	if (!/^https?:\/\//i.test(url)) {
		url = `http://${url}`
	}
	return url.replace(/\/+$/, '')
}

export function getBaseUrl() {
	return normalizeBaseUrl(DEFAULT_BASE_URL)
}

export function setBaseUrl(value) {
	return normalizeBaseUrl(value || DEFAULT_BASE_URL)
}

export function getAuthToken() {
	return toTrimmedString(safeGet(STORAGE_KEYS.authToken))
}

export function getCurrentUser() {
	return toTrimmedString(safeGet(STORAGE_KEYS.authUser))
}

export function saveAuthSession(payload = {}) {
	const token = toTrimmedString(payload.token)
	const username = toTrimmedString(payload.email || payload.username)
	safeSet(STORAGE_KEYS.authToken, token)
	safeSet(STORAGE_KEYS.authUser, username)
}

export function clearProjectSelection(username = '') {
	safeRemove(scopedKey(STORAGE_KEYS.currentProjectId, username))
	safeRemove(scopedKey(STORAGE_KEYS.projectCache, username))
}

export function clearAuthSession() {
	safeRemove(STORAGE_KEYS.authToken)
	safeRemove(STORAGE_KEYS.authUser)
}

export function getCurrentProjectId(username = '') {
	return toTrimmedString(safeGet(scopedKey(STORAGE_KEYS.currentProjectId, username)))
}

export function setCurrentProjectId(projectId, username = '') {
	const normalized = toTrimmedString(projectId)
	const key = scopedKey(STORAGE_KEYS.currentProjectId, username)
	if (!normalized) {
		safeRemove(key)
		return ''
	}
	safeSet(key, normalized)
	return normalized
}

export function saveProjectCache(project, username = '') {
	const key = scopedKey(STORAGE_KEYS.projectCache, username)
	if (!project || typeof project !== 'object') {
		safeRemove(key)
		return null
	}
	const normalized = JSON.parse(JSON.stringify(project))
	safeSet(key, JSON.stringify(normalized))
	if (normalized.id) {
		setCurrentProjectId(normalized.id, username)
	}
	return normalized
}

export function getProjectCache(username = '') {
	const raw = toTrimmedString(safeGet(scopedKey(STORAGE_KEYS.projectCache, username)))
	if (!raw) {
		return null
	}
	try {
		const parsed = JSON.parse(raw)
		return parsed && typeof parsed === 'object' ? parsed : null
	} catch (error) {
		return null
	}
}

export function hasAuthSession() {
	return Boolean(getAuthToken())
}

export function saveStudioView(payload = {}, username = '') {
	const key = scopedKey(STORAGE_KEYS.studioView, username)
	const mainTab = toTrimmedString(payload.mainTab)
	const createTab = toTrimmedString(payload.createTab)
	if (!mainTab && !createTab) {
		safeRemove(key)
		return null
	}
	const value = {
		mainTab: mainTab || 'create',
		createTab: createTab || 'project'
	}
	safeSet(key, JSON.stringify(value))
	return value
}

export function getStudioView(username = '') {
	const raw = toTrimmedString(safeGet(scopedKey(STORAGE_KEYS.studioView, username)))
	if (!raw) {
		return null
	}
	try {
		const parsed = JSON.parse(raw)
		return parsed && typeof parsed === 'object' ? parsed : null
	} catch (error) {
		return null
	}
}
