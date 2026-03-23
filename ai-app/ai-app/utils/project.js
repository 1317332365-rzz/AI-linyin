export const EMPTY_SCRIPT = {
	input: '',
	duration: '3min',
	result: null
}

function deepCopy(value, fallback = null) {
	if (value === undefined) {
		return fallback
	}
	try {
		return JSON.parse(JSON.stringify(value))
	} catch (error) {
		return fallback
	}
}

function safeText(value) {
	return String(value || '').trim()
}

function summarize(text, length = 80) {
	const source = safeText(text).replace(/\s+/g, ' ')
	if (!source) {
		return ''
	}
	return source.length > length ? `${source.slice(0, length)}...` : source
}

export function normalizeEpisodeNo(value) {
	const parsed = Number(value)
	return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 1
}

export function normalizeVideoProvider(value) {
	const provider = safeText(value).toLowerCase()
	if (provider === 'jimeng') {
		return 'jimeng'
	}
	if (provider === 'grsai') {
		return 'grsai'
	}
	return 'openai'
}

export function hashText(text) {
	const source = String(text || '')
	let hash = 0
	for (let index = 0; index < source.length; index += 1) {
		hash = ((hash << 5) - hash + source.charCodeAt(index)) | 0
	}
	return Math.abs(hash).toString(36)
}

export function classifyAssetKind(asset) {
	const safeAsset = asset && typeof asset === 'object' ? asset : {}
	const typeText = [
		safeAsset.asset_kind,
		safeAsset.assetKind,
		safeAsset.type,
		safeAsset.asset_type,
		safeAsset.category
	]
		.map((item) => safeText(item).toLowerCase())
		.join(' ')
	const contentText = [safeAsset.name, safeAsset.prompt, safeAsset.source_description]
		.map((item) => safeText(item).toLowerCase())
		.join(' ')

	if (/character|角色/.test(typeText) || /角色/.test(contentText) || safeText(safeAsset.wardrobe)) {
		return 'character'
	}
	if (/scene|场景|环境/.test(typeText) || /场景|环境/.test(contentText)) {
		return 'scene'
	}
	return ''
}

export function normalizeAssetEntry(asset, index = 0) {
	const safeAsset = asset && typeof asset === 'object' ? { ...asset } : {}
	const assetKind = classifyAssetKind(safeAsset)
	if (assetKind) {
		safeAsset.asset_kind = assetKind
	}

	const explicitId = safeText(safeAsset.id || safeAsset.asset_id)
	if (explicitId) {
		safeAsset.id = explicitId
		return safeAsset
	}

	const seed = [
		safeText(safeAsset.type),
		safeText(safeAsset.name),
		safeText(safeAsset.image_url),
		safeText(safeAsset.prompt),
		String(index)
	].join('|')
	safeAsset.id = `asset_${hashText(seed)}`
	return safeAsset
}

export function normalizeAssetList(list) {
	if (!Array.isArray(list)) {
		return []
	}
	return list.map((item, index) => normalizeAssetEntry(item, index))
}

export function createEmptyShot(index = 1) {
	return {
		sceneNo: index,
		title: `场次 ${index}`,
		duration: '5s',
		sourceDescription: '',
		shotSummary: '',
		detailedShotDescription: '',
		detailedPlot: '',
		voiceoverText: '',
		dialogueDetails: '',
		actionDetails: '',
		shotDeployment: '',
		boundCharacterAssetIds: [],
		boundCharacterNames: [],
		boundSceneAssetIds: [],
		boundSceneNames: [],
		prompt: '',
		startFrame: {
			description: '',
			enhanced_prompt: '',
			image_url: ''
		},
		endFrame: {
			description: '',
			enhanced_prompt: '',
			image_url: ''
		},
		videoUrl: '',
		videoTask: {
			taskId: '',
			status: '',
			message: '',
			progress: 0,
			provider: '',
			reqKey: '',
			queryUrl: '',
			queryMethod: ''
		},
		includeInFinal: true,
		notes: ''
	}
}

export function ensureEpisodeState(episodeScripts, episodeShots, episodeNo) {
	const key = String(normalizeEpisodeNo(episodeNo))
	if (!episodeScripts[key] || typeof episodeScripts[key] !== 'object') {
		episodeScripts[key] = {
			script: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
			history: []
		}
	}
	if (!episodeScripts[key].script || typeof episodeScripts[key].script !== 'object') {
		episodeScripts[key].script = deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT })
	}
	if (!Array.isArray(episodeScripts[key].history)) {
		episodeScripts[key].history = []
	}
	if (!Array.isArray(episodeShots[key])) {
		episodeShots[key] = []
	}
	return key
}

function formatDialogueBeatItem(item, index = 0) {
	if (!item || typeof item !== 'object') {
		return safeText(item)
	}
	const beatId = safeText(item.beat_id || item.id || index + 1)
	const speaker = safeText(item.speaker || item.role || `角色${index + 1}`)
	const line = safeText(item.line || item.dialogue)
	const tone = safeText(item.tone)
	const reaction = safeText(item.reaction)
	const parts = []
	if (speaker || line) {
		parts.push(`${speaker}${line ? `：${line}` : ''}`)
	}
	if (tone) {
		parts.push(`语气:${tone}`)
	}
	if (reaction) {
		parts.push(`反应:${reaction}`)
	}
	const content = parts.join(' | ').trim()
	return content ? `${beatId}. ${content}` : ''
}

function findSceneDialogueBeat(scene, beatId = '', beatIndex = 0) {
	const beats = Array.isArray(scene && scene.dialogue_beats) ? scene.dialogue_beats : []
	if (!beats.length) {
		return null
	}
	const normalizedBeatId = safeText(beatId)
	if (normalizedBeatId) {
		const matched = beats.find((item) => safeText(item && (item.beat_id || item.id)) === normalizedBeatId)
		if (matched) {
			return matched
		}
	}
	return beats[beatIndex] || null
}

function formatShotPlanItem(item, index = 0) {
	if (!item || typeof item !== 'object') {
		return safeText(item)
	}
	const beatId = safeText(item.beat_id || item.id || index + 1)
	const shotType = safeText(item.shot_type || item.lens || item.framing)
	const cameraAngle = safeText(item.camera_angle || item.angle)
	const cameraMovement = safeText(item.camera_movement || item.movement)
	const blocking = safeText(item.blocking || item.beat || item.description || item.action || item)
	const dialogue = safeText(item.dialogue || item.line)
	const duration = safeText(item.duration)
	const lensPart = [shotType, cameraAngle, cameraMovement].filter(Boolean).join(' / ')
	let line = `${beatId}. ${lensPart ? `${lensPart}：` : ''}${blocking || '镜头推进'}`
	if (dialogue) {
		line += ` | 台词:${dialogue}`
	}
	if (duration) {
		line += ` | ${duration}`
	}
	return line
}

function buildSceneStagingNotes(scene) {
	const explicit = safeText(scene && scene.staging_notes)
	if (explicit) {
		return explicit
	}
	const plan = Array.isArray(scene && scene.shot_plan) ? scene.shot_plan : []
	return plan
		.slice(0, 6)
		.map((item, index) => formatShotPlanItem(item, index))
		.filter(Boolean)
		.join('\n')
}

function buildSceneActionDetails(scene) {
	const explicit = safeText(scene && scene.action_details)
	if (explicit) {
		return explicit
	}
	const actions = Array.isArray(scene && scene.character_actions) ? scene.character_actions : []
	return actions.map((item) => safeText(item)).filter(Boolean).join('\n')
}

function buildSceneDialogueBeatDetails(scene) {
	const explicit = safeText(scene && scene.dialogue_beat_details)
	if (explicit) {
		return explicit
	}
	const beats = Array.isArray(scene && scene.dialogue_beats) ? scene.dialogue_beats : []
	return beats
		.slice(0, 6)
		.map((item, index) => formatDialogueBeatItem(item, index))
		.filter(Boolean)
		.join('\n')
}

function buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex = 0) {
	const safeBeat = beat && typeof beat === 'object' ? beat : {}
	const beatId = safeText(safeBeat.beat_id || safeBeat.id || beatIndex + 1) || String(beatIndex + 1)
	const shotType = safeText(safeBeat.shot_type || safeBeat.lens || safeBeat.framing)
	const cameraAngle = safeText(safeBeat.camera_angle || safeBeat.angle)
	const cameraMovement = safeText(safeBeat.camera_movement || safeBeat.movement)
	const blocking = safeText(safeBeat.blocking || safeBeat.beat || safeBeat.description || safeBeat.action || beat)
	const dialogue = safeText(safeBeat.dialogue || safeBeat.line)
	const transition = safeText(safeBeat.transition)
	const duration = safeText(safeBeat.duration)
	const sourceDescription = safeText(scene && scene.description)
	const sceneShotSummary = safeText(scene && scene.shot_description)
	const lensSummary = [shotType, cameraAngle, cameraMovement].filter(Boolean).join(' / ')
	const dialogueBeat = findSceneDialogueBeat(scene, beatId, beatIndex)
	const dialogueBeatLine = dialogueBeat
		? formatDialogueBeatItem(dialogueBeat, beatIndex).replace(/^\d+\.\s*/, '').trim()
		: ''
	const sceneActionLine = Array.isArray(scene && scene.character_actions)
		? safeText(scene.character_actions[beatIndex])
		: ''
	const shotDeployment = formatShotPlanItem(safeBeat, beatIndex) || [lensSummary, blocking].filter(Boolean).join('：')
	const actionDetails = [blocking, sceneActionLine].filter(Boolean).join('\n')
	const dialogueDetails = [dialogue, dialogueBeatLine].filter(Boolean).join('；')
	const dialogueBeatDetails = dialogueBeat
		? formatDialogueBeatItem(dialogueBeat, beatIndex)
		: dialogue
			? `${beatId}. ${dialogue}`
			: ''
	const shotSummary = lensSummary || sceneShotSummary || `镜头 ${beatId}`
	const detailedShotDescription =
		[
			shotSummary && `镜头设计：${shotSummary}`,
			blocking && `当前动作：${blocking}`,
			dialogue && `对白重点：${dialogue}`,
			transition && `镜头衔接：${transition}`
		]
			.filter(Boolean)
			.join('，') || blocking || shotSummary || sourceDescription
	const detailedPlot = [
		shotDeployment ? `分镜调度：\n${shotDeployment}` : '',
		actionDetails ? `动作细节：\n${actionDetails}` : '',
		dialogueDetails ? `对白细节：\n${dialogueDetails}` : '',
		dialogueBeatDetails ? `对白节拍：\n${dialogueBeatDetails}` : ''
	]
		.filter(Boolean)
		.join('\n\n')

	return {
		...createEmptyShot(sceneNo),
		sceneNo,
		title: `场次 ${sceneNo} · 镜头 ${beatId}`,
		duration: duration || safeText(scene && scene.duration) || '5s',
		sourceDescription,
		shotSummary,
		detailedShotDescription,
		detailedPlot,
		dialogueDetails,
		actionDetails,
		shotDeployment,
		startFrame: {
			description: [shotSummary, blocking].filter(Boolean).join('，') || detailedShotDescription,
			enhanced_prompt: '',
			image_url: ''
		},
		endFrame: {
			description: '',
			enhanced_prompt: '',
			image_url: ''
		}
	}
}

function buildShotFromScene(scene, fallbackIndex = 1) {
	const sceneNo = safeText(scene && scene.scene_id) || String(fallbackIndex)
	const sourceDescription = safeText(scene && scene.description)
	const shotSummary = safeText(scene && scene.shot_description)
	const detailedShotDescription = safeText(scene && (scene.detailed_shot_description || shotSummary || sourceDescription))
	const dialogueDetails = safeText(
		(scene &&
			(scene.dialogue_details ||
				(Array.isArray(scene.dialogue)
					? scene.dialogue.map((item) => safeText(item)).filter(Boolean).join('；')
					: ''))) ||
			''
	)
	const shotDeployment = buildSceneStagingNotes(scene)
	const actionDetails = buildSceneActionDetails(scene)
	const dialogueBeatDetails = buildSceneDialogueBeatDetails(scene)
	const detailedPlot = [
		shotDeployment ? `分镜调度：\n${shotDeployment}` : '',
		actionDetails ? `动作细节：\n${actionDetails}` : '',
		dialogueDetails ? `对白细节：\n${dialogueDetails}` : '',
		dialogueBeatDetails ? `对白节拍：\n${dialogueBeatDetails}` : ''
	]
		.filter(Boolean)
		.join('\n\n')

	return {
		...createEmptyShot(Number(sceneNo) || fallbackIndex),
		sceneNo,
		title: `场次 ${sceneNo}`,
		duration: safeText(scene && scene.duration) || '5s',
		sourceDescription,
		shotSummary,
		detailedShotDescription,
		detailedPlot,
		dialogueDetails,
		actionDetails,
		shotDeployment,
		startFrame: {
			description: detailedShotDescription,
			enhanced_prompt: '',
			image_url: ''
		},
		endFrame: {
			description: '',
			enhanced_prompt: '',
			image_url: ''
		}
	}
}

export function buildShotsFromScene(scene, fallbackIndex = 1) {
	const plan = Array.isArray(scene && scene.shot_plan) ? scene.shot_plan.filter(Boolean) : []
	const sceneNo = safeText(scene && scene.scene_id) || String(fallbackIndex)
	if (plan.length) {
		return plan.map((beat, beatIndex) => buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex))
	}
	return [buildShotFromScene(scene, fallbackIndex)]
}

export function buildShotsFromScenes(scenes) {
	if (!Array.isArray(scenes)) {
		return []
	}
	return scenes.reduce((result, scene, index) => result.concat(buildShotsFromScene(scene, index + 1)), [])
}

export function createDefaultProjectState() {
	return {
		currentProjectId: '',
		currentProjectName: '',
		currentScriptTitle: '',
		currentEpisodeNo: 1,
		videoProvider: 'openai',
		assets: [],
		shots: [],
		generatedData: [],
		lastScript: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
		scriptHistory: [],
		episodeScripts: {
			'1': {
				script: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
				history: []
			}
		},
		episodeShots: {
			'1': []
		}
	}
}

export function applyProject(project) {
	const state = createDefaultProjectState()
	const safeProject = project && typeof project === 'object' ? project : {}
	state.currentProjectId = safeText(safeProject.id)
	state.currentProjectName = safeText(safeProject.name)
	state.currentScriptTitle = safeText(safeProject.script_title)
	state.currentEpisodeNo = normalizeEpisodeNo(safeProject.episode_no)
	state.videoProvider = normalizeVideoProvider(safeProject.video_provider)
	state.assets = normalizeAssetList(safeProject.assets)
	state.generatedData = Array.isArray(safeProject.generated_data) ? deepCopy(safeProject.generated_data, []) : []

	const incomingEpisodeScripts =
		safeProject.episode_scripts && typeof safeProject.episode_scripts === 'object'
			? safeProject.episode_scripts
			: {}
	const incomingEpisodeShots =
		safeProject.episode_shots && typeof safeProject.episode_shots === 'object'
			? safeProject.episode_shots
			: {}

	state.episodeScripts = {}
	Object.keys(incomingEpisodeScripts).forEach((key) => {
		const entry = incomingEpisodeScripts[key] || {}
		state.episodeScripts[String(key)] = {
			script:
				entry.script && typeof entry.script === 'object'
					? {
							input: safeText(entry.script.input),
							duration: safeText(entry.script.duration) || '3min',
							result: deepCopy(entry.script.result, null)
					  }
					: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
			history: Array.isArray(entry.history) ? deepCopy(entry.history, []) : []
		}
	})

	state.episodeShots = {}
	Object.keys(incomingEpisodeShots).forEach((key) => {
		state.episodeShots[String(key)] = Array.isArray(incomingEpisodeShots[key]) ? deepCopy(incomingEpisodeShots[key], []) : []
	})

	if (!Object.keys(state.episodeScripts).length) {
		const fallbackKey = String(state.currentEpisodeNo)
		state.episodeScripts[fallbackKey] = {
			script: {
				input: safeText(safeProject.script && safeProject.script.input),
				duration: safeText(safeProject.script && safeProject.script.duration) || '3min',
				result: deepCopy(safeProject.script && safeProject.script.result, null)
			},
			history: Array.isArray(safeProject.history) ? deepCopy(safeProject.history, []) : []
		}
	}

	if (!Object.keys(state.episodeShots).length) {
		state.episodeShots[String(state.currentEpisodeNo)] = Array.isArray(safeProject.shots)
			? deepCopy(safeProject.shots, [])
			: []
	}

	const key = ensureEpisodeState(state.episodeScripts, state.episodeShots, state.currentEpisodeNo)
	const episodeState = state.episodeScripts[key]
	state.lastScript = {
		input: safeText(episodeState.script && episodeState.script.input),
		duration: safeText(episodeState.script && episodeState.script.duration) || '3min',
		result: deepCopy(episodeState.script && episodeState.script.result, null)
	}
	state.scriptHistory = Array.isArray(episodeState.history) ? deepCopy(episodeState.history, []) : []
	state.shots = Array.isArray(state.episodeShots[key]) ? deepCopy(state.episodeShots[key], []) : []
	return state
}

export function buildProjectPayload(state) {
	const episodeScripts = deepCopy(state.episodeScripts, {}) || {}
	const episodeShots = deepCopy(state.episodeShots, {}) || {}
	const key = ensureEpisodeState(episodeScripts, episodeShots, state.currentEpisodeNo)

	episodeScripts[key] = {
		script: {
			input: safeText(state.lastScript && state.lastScript.input),
			duration: safeText(state.lastScript && state.lastScript.duration) || '3min',
			result: deepCopy(state.lastScript && state.lastScript.result, null)
		},
		history: Array.isArray(state.scriptHistory) ? deepCopy(state.scriptHistory, []) : []
	}
	episodeShots[key] = Array.isArray(state.shots) ? deepCopy(state.shots, []) : []

	return {
		name: safeText(state.currentProjectName) || '未命名项目',
		script_title: safeText(state.currentScriptTitle),
		episode_no: normalizeEpisodeNo(state.currentEpisodeNo),
		video_provider: normalizeVideoProvider(state.videoProvider),
		assets: normalizeAssetList(state.assets),
		shots: episodeShots[key] || [],
		history: episodeScripts[key].history || [],
		generated_data: Array.isArray(state.generatedData) ? deepCopy(state.generatedData, []) : [],
		script: episodeScripts[key].script || deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
		episode_scripts: episodeScripts,
		episode_shots: episodeShots
	}
}

export function listEpisodeOptions(state) {
	const set = new Set()
	Object.keys((state && state.episodeScripts) || {}).forEach((key) => {
		set.add(normalizeEpisodeNo(key))
	})
	Object.keys((state && state.episodeShots) || {}).forEach((key) => {
		set.add(normalizeEpisodeNo(key))
	})
	set.add(normalizeEpisodeNo(state && state.currentEpisodeNo))
	if (!set.size) {
		set.add(1)
	}
	return [...set].sort((left, right) => left - right)
}

export function describeShot(shot) {
	if (!shot || typeof shot !== 'object') {
		return ''
	}
	return summarize(
		[
			safeText(shot.title),
			safeText(shot.shotSummary),
			safeText(shot.detailedShotDescription),
			safeText(shot.videoTask && shot.videoTask.message)
		]
			.filter(Boolean)
			.join(' | '),
		96
	)
}
