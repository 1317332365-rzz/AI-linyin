import { getAuthToken, getCurrentProjectId } from './storage'

export function redirectTo(url) {
	uni.redirectTo({ url })
}

export function relaunchTo(url) {
	uni.reLaunch({ url })
}

export function ensureAuth() {
	if (getAuthToken()) {
		return true
	}
	relaunchTo('/views/account/index')
	return false
}

export function ensureProjectSelected() {
	if (getCurrentProjectId()) {
		return true
	}
	uni.showToast({
		title: '请先选择项目',
		icon: 'none'
	})
	setTimeout(() => {
		redirectTo('/views/projects/index')
	}, 300)
	return false
}
