import { getProject, updateProject } from '../api/projects'
import { buildProjectPayload } from './project'
import { getCurrentProjectId, getProjectCache, saveProjectCache } from './storage'

export async function loadCurrentProject(options = {}) {
	const projectId = options.projectId || getCurrentProjectId()
	if (!projectId) {
		return null
	}
	if (!options.forceRemote) {
		const cache = getProjectCache()
		if (cache && cache.id === projectId) {
			return cache
		}
	}
	const project = await getProject(projectId)
	saveProjectCache(project)
	return project
}

export async function saveCurrentProjectState(state) {
	const projectId = state.currentProjectId || getCurrentProjectId()
	if (!projectId) {
		throw new Error('请先选择项目')
	}
	const payload = buildProjectPayload(state)
	const updated = await updateProject(projectId, payload)
	const merged = {
		...payload,
		...updated,
		id: projectId
	}
	saveProjectCache(merged)
	return merged
}

