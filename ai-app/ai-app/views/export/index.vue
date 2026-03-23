<template>
	<view class="studio-page">
		<LoadingProgress :visible="progress.visible" :value="progress.value" :label="progress.label" />
		<view class="studio-page__bg"></view>

		<view class="app-page studio-shell">
			<view class="section-card page-head">
				<text class="section-title">视频导出管理</text>
				<text class="section-subtitle">整理入片镜头、补充剪辑说明，并导出 JSON、TXT 或 MP4。</text>
			</view>

			<view v-if="!hasProject" class="section-card empty-block">
				<text>先在动漫生成里打开一个项目，再来整理导出内容。</text>
				<u-button class="primary-btn top-gap" type="primary" @click="goCreatePage">去动漫生成</u-button>
			</view>

			<template v-else>
				<view class="section-card">
					<view class="section-head">
						<text class="section-title">导出概览</text>
						<u-button class="secondary-btn mini-btn" :loading="saving" @click="saveProject">{{ saving ? '正在保存...' : '保存草稿' }}</u-button>
					</view>
					<view class="summary-grid">
						<view class="summary-card">
							<text class="meta-label">当前项目</text>
							<text class="meta-value">{{ currentProjectName || '未命名项目' }}</text>
							<text class="meta-hint">第 {{ currentEpisodeNo }} 集</text>
						</view>
						<view class="summary-card tone-soft">
							<text class="meta-label">导出统计</text>
							<text class="meta-value">{{ selectedShots.length }} 个入片镜头</text>
							<text class="meta-hint">可导出 {{ activeShots.length }} · 预计 {{ estimatedDurationSec }} 秒</text>
						</view>
					</view>
				</view>

				<view class="section-card">
					<view class="section-head">
						<text class="section-title">镜头导出清单</text>
						<u-button class="secondary-btn mini-btn" @click="loadProject(true)">重新同步</u-button>
					</view>
					<view v-if="!shots.length" class="empty-block">
						<text>当前项目还没有镜头，先去导演模块生成内容。</text>
					</view>
					<view v-else class="list-stack">
						<view v-for="(shot, index) in shots" :key="`export-${index}`" class="list-card list-card--stack" @click="selectedShotIndex = index">
							<view class="export-head">
								<view>
									<text class="list-card__title">{{ shot.title || `镜头 ${index + 1}` }}</text>
									<text class="list-card__desc">{{ shot.duration || '5s' }} · {{ taskStatusText(shot) }}</text>
								</view>
								<switch :checked="shot.includeInFinal !== false" color="#7a9677" @change="handleIncludeChange($event, index)" />
							</view>
							<view class="form-group">
								<text class="field-label">视频链接</text>
								<input v-model="shot.videoUrl" class="field-input" type="text" placeholder="https://..." placeholder-class="field-placeholder" :adjust-position="false" />
							</view>
							<view class="form-group no-gap">
								<text class="field-label">剪辑备注</text>
								<input v-model="shot.notes" class="field-input" type="text" placeholder="例如：结尾快切、字幕加重" placeholder-class="field-placeholder" :adjust-position="false" />
							</view>
						</view>
					</view>
				</view>

				<view v-if="selectedShot" class="section-card">
					<text class="section-title">镜头预览</text>
					<video v-if="selectedShot.videoUrl" class="preview-video top-gap" :src="selectedShot.videoUrl" controls playsinline></video>
					<image v-else-if="selectedShot.startFrame && selectedShot.startFrame.image_url" class="preview-video top-gap" :src="selectedShot.startFrame.image_url" mode="aspectFill"></image>
					<view v-else class="empty-block small-empty">
						<text>当前镜头还没有可预览内容。</text>
					</view>
				</view>

				<view class="section-card">
					<view class="section-head">
						<text class="section-title">最终成片文案</text>
						<u-button class="ghost-btn mini-btn" @click="syncFinalEditText">根据镜头自动整理</u-button>
					</view>
					<textarea v-model="finalEditText" class="field-textarea json-textarea top-gap" placeholder="补充字幕、配乐、节奏和串联说明" placeholder-class="field-placeholder"></textarea>
					<view class="action-row compact-actions top-gap">
						<u-button class="secondary-btn" @click="downloadJson">导出 JSON</u-button>
						<u-button class="secondary-btn" @click="downloadTxt">导出 TXT</u-button>
						<u-button class="primary-btn" type="primary" :loading="exporting" @click="exportFinalVideo">{{ exporting ? '正在导出...' : '导出 MP4' }}</u-button>
					</view>
				</view>
			</template>
		</view>
	</view>
</template>

<script>
	import LoadingProgress from '../../components/LoadingProgress.vue'
	import UButton from '../../uni_modules/uview-ui/components/u-button/u-button.vue'
	import { exportVideo } from '../../api/export'
	import { downloadBinaryInBrowser, downloadTextInBrowser, resolveFilename } from '../../utils/download'
	import { ensureAuth } from '../../utils/navigation'
	import { applyProject, createDefaultProjectState, createEmptyShot, ensureEpisodeState } from '../../utils/project'
	import { loadCurrentProject, saveCurrentProjectState } from '../../utils/project-session'
	import { getCurrentProjectId, getProjectCache, saveProjectCache } from '../../utils/storage'

	function clone(value, fallback) { try { return JSON.parse(JSON.stringify(value)) } catch (error) { return fallback } }
	function safeText(value) { return String(value || '').trim() }

	export default {
		components: { LoadingProgress, UButton },
		data() {
			return {
				...createDefaultProjectState(),
				initialized: false,
				progress: { visible: false, value: 0, label: '' },
				progressTimer: null,
				progressHideTimer: null,
				activeProjectCache: null,
				saving: false,
				exporting: false,
				selectedShotIndex: -1,
				finalEditText: ''
			}
		},
		computed: {
			hasProject() { return Boolean(this.currentProjectId) },
			selectedShot() { return this.selectedShotIndex >= 0 && this.selectedShotIndex < this.shots.length ? this.shots[this.selectedShotIndex] : null },
			selectedShots() { return this.shots.filter((shot) => shot.includeInFinal !== false) },
			activeShots() { return this.selectedShots.filter((shot) => safeText(shot.videoUrl)) },
			estimatedDurationSec() { return this.selectedShots.reduce((total, shot) => total + this.parseDurationToSeconds(shot.duration), 0) }
		},
		onShow() {
			if (!ensureAuth()) { return }
			if (!this.initialized) {
				this.initializePage()
				return
			}
			this.activeProjectCache = getProjectCache()
			if (this.hasProject || getCurrentProjectId()) {
				this.loadProject(true, true)
			}
		},
		onPullDownRefresh() {
			if (!ensureAuth()) {
				uni.stopPullDownRefresh()
				return
			}
			this.refreshCurrentView()
		},
		onUnload() {
			this.clearProgressTimer()
		},
		methods: {
			showToast(message) { uni.showToast({ title: safeText(message) || '操作失败', icon: 'none' }) },
			clearProgressTimer() { if (this.progressTimer) { clearInterval(this.progressTimer); this.progressTimer = null } if (this.progressHideTimer) { clearTimeout(this.progressHideTimer); this.progressHideTimer = null } },
			startProgress(label) { this.clearProgressTimer(); this.progress = { visible: true, value: 16, label: safeText(label) || '正在处理' }; this.progressTimer = setInterval(() => { const currentValue = Number(this.progress.value || 0); const delta = currentValue < 60 ? 9 : currentValue < 84 ? 4 : 0; this.progress.value = Math.min(currentValue + delta, 90) }, 220) },
			finishProgress(label) { this.clearProgressTimer(); this.progress.label = safeText(label) || this.progress.label || '已完成'; this.progress.value = 100; this.progressHideTimer = setTimeout(() => { this.progress.visible = false; this.progress.value = 0 }, 320) },
			async runTask(label, handler, options = {}) { this.startProgress(label); try { const result = await handler(); this.finishProgress(options.successText || '已完成'); return result } catch (error) { this.finishProgress(safeText(error && error.message) || options.failureText || '操作失败'); throw error } },
			normalizeShot(shot, index = 0) { const safeShot = shot && typeof shot === 'object' ? clone(shot, {}) : {}; const defaults = createEmptyShot(index + 1); return { ...defaults, ...safeShot, title: safeText(safeShot.title) || `镜头 ${index + 1}`, duration: safeText(safeShot.duration) || '5s', startFrame: { ...defaults.startFrame, ...(safeShot.startFrame || {}) }, endFrame: { ...defaults.endFrame, ...(safeShot.endFrame || {}) }, videoTask: { ...defaults.videoTask, ...(safeShot.videoTask || {}) } } },
			hydrateProject(project) {
				const next = applyProject(project)
				next.shots = (next.shots || []).map((shot, index) => this.normalizeShot(shot, index))
				Object.assign(this, next)
				this.selectedShotIndex = next.shots.length ? 0 : -1
				this.finalEditText = this.readStoredFinalEditText() || this.buildFinalEditText()
				this.activeProjectCache = clone(project, {})
			},
			async fetchCurrentProject(forceRemote = false) {
				const project = await loadCurrentProject({ forceRemote })
				if (project) {
					this.hydrateProject(project)
				}
				return project
			},
			async initializePage() {
				try {
					await this.runTask('正在同步导出内容', async () => {
						this.activeProjectCache = getProjectCache()
						if (getCurrentProjectId()) {
							await this.fetchCurrentProject(true)
						}
					}, { successText: '导出页已就绪' })
					this.initialized = true
				} catch (error) {
					this.showToast(error.message || '初始化失败')
				} finally {
					uni.stopPullDownRefresh()
				}
			},
			async refreshCurrentView() {
				try {
					await this.runTask('正在刷新导出页', async () => {
						if (getCurrentProjectId()) {
							await this.fetchCurrentProject(true)
						}
					}, { successText: '导出页已刷新' })
				} catch (error) {
					this.showToast(error.message || '刷新失败')
				} finally {
					uni.stopPullDownRefresh()
				}
			},
			async loadProject(forceRemote = false, silent = false) {
				if (!this.hasProject && !getCurrentProjectId()) { return }
				try {
					if (silent) {
						await this.fetchCurrentProject(forceRemote)
					} else {
						await this.runTask('正在同步当前项目', () => this.fetchCurrentProject(forceRemote), { successText: '项目数据已更新' })
					}
				} catch (error) {
					this.showToast(error.message || '加载项目失败')
				} finally {
					uni.stopPullDownRefresh()
				}
			},
			persistCurrentEpisodeState() {
				const key = ensureEpisodeState(this.episodeScripts, this.episodeShots, this.currentEpisodeNo)
				this.episodeShots[key] = clone(this.shots, [])
			},
			persistFinalEditText() {
				const filtered = (this.generatedData || []).filter((item) => item && item.type !== 'final_edit_text')
				const text = safeText(this.finalEditText)
				if (text) {
					filtered.unshift({ id: `g_${Date.now()}`, type: 'final_edit_text', createdAt: new Date().toISOString(), payload: { text } })
				}
				this.generatedData = filtered
			},
			readStoredFinalEditText() {
				const target = (this.generatedData || []).find((item) => item && item.type === 'final_edit_text')
				return target && target.payload ? safeText(target.payload.text) : ''
			},
			async persistProjectState(silent = false) {
				const saveAction = async () => {
					this.persistCurrentEpisodeState()
					this.persistFinalEditText()
					const updated = await saveCurrentProjectState(this)
					const merged = { ...(this.activeProjectCache || {}), ...updated, id: updated.id || this.currentProjectId }
					saveProjectCache(merged)
					this.activeProjectCache = merged
					return merged
				}
				if (silent) {
					return saveAction()
				}
				this.saving = true
				try {
					return await this.runTask('正在保存导出草稿', saveAction, { successText: '导出草稿已保存' })
				} finally {
					this.saving = false
				}
			},
			async saveProject() {
				try {
					await this.persistProjectState(false)
				} catch (error) {
					this.showToast(error.message || '保存失败')
				}
			},
			taskState(shot) { const status = safeText(shot && shot.videoTask && shot.videoTask.status).toLowerCase(); if (safeText(shot && shot.videoUrl) || status === 'succeeded') { return 'succeeded' } if (['submitting', 'submitted', 'processing', 'running', 'pending'].includes(status)) { return 'processing' } if (['failed', 'error'].includes(status)) { return 'failed' } return 'idle' },
			taskStatusText(shot) { const state = this.taskState(shot); return state === 'succeeded' ? '视频已就绪' : state === 'processing' ? '视频生成中' : state === 'failed' ? '视频生成失败' : '待生成' },
			parseDurationToSeconds(duration) { const text = safeText(duration).toLowerCase(); if (!text) { return 0 } if (/^\d+$/.test(text)) { return Number(text) } const minuteMatch = text.match(/(\d+(?:\.\d+)?)\s*(min|分钟|m)/); if (minuteMatch) { return Math.round(Number(minuteMatch[1]) * 60) } const secondMatch = text.match(/(\d+(?:\.\d+)?)\s*(s|sec|秒)/); return secondMatch ? Math.round(Number(secondMatch[1])) : 0 },
			handleIncludeChange(event, index) { this.shots[index].includeInFinal = Boolean(event.detail.value) },
			buildFinalEditText() { return this.selectedShots.map((shot, index) => [`${index + 1}. ${safeText(shot.title) || `镜头 ${index + 1}`}`, safeText(shot.duration) ? `时长：${safeText(shot.duration)}` : '', safeText(shot.notes) ? `剪辑备注：${safeText(shot.notes)}` : '', safeText(shot.videoUrl) ? `视频：${safeText(shot.videoUrl)}` : '视频：待补齐'].filter(Boolean).join('\n')).join('\n\n') },
			syncFinalEditText() { this.finalEditText = this.buildFinalEditText() },
			downloadJson() {
				const payload = JSON.stringify({ project_name: this.currentProjectName, episode_no: this.currentEpisodeNo, final_edit_text: this.finalEditText, shots: this.selectedShots }, null, 2)
				const filename = `episode-${this.currentEpisodeNo}-final.json`
				if (downloadTextInBrowser(payload, filename, 'application/json;charset=utf-8')) { return }
				uni.setClipboardData({ data: payload })
			},
			downloadTxt() {
				const payload = safeText(this.finalEditText) || this.buildFinalEditText()
				const filename = `episode-${this.currentEpisodeNo}-final.txt`
				if (downloadTextInBrowser(payload, filename, 'text/plain;charset=utf-8')) { return }
				uni.setClipboardData({ data: payload })
			},
			async exportFinalVideo() {
				if (!this.activeShots.length) {
					this.showToast('没有可导出的镜头')
					return
				}
				this.exporting = true
				try {
					const response = await this.runTask('正在导出成片', async () => {
						await this.persistProjectState(true)
						return exportVideo({ shots: this.activeShots, episode_no: this.currentEpisodeNo })
					}, { successText: '导出文件已准备' })
					const headers = response.header || {}
					const disposition = headers['content-disposition'] || headers['Content-Disposition'] || ''
					const contentType = headers['content-type'] || headers['Content-Type'] || 'video/mp4'
					const filename = resolveFilename(disposition, `episode-${this.currentEpisodeNo}-final.mp4`)
					if (!downloadBinaryInBrowser(response.data, filename, contentType)) {
						this.showToast('当前平台请在 H5 环境下载 MP4')
					}
				} catch (error) {
					this.showToast(error.message || '导出失败')
				} finally {
					this.exporting = false
				}
			},
			goCreatePage() {
				uni.switchTab({ url: '/views/projects/index' })
			}
		}
	}
</script>

<style scoped lang="scss">
	.studio-page { position: relative; min-height: 100vh; background: linear-gradient(180deg, #f6f1e8 0%, #f5f4ed 38%, #edf1ea 100%); color: #2a342f; }
	.studio-page__bg { position: fixed; inset: 0; background: radial-gradient(circle at top left, rgba(222, 226, 204, 0.88), transparent 38%), radial-gradient(circle at top right, rgba(210, 223, 211, 0.7), transparent 34%), radial-gradient(circle at bottom, rgba(233, 238, 226, 0.92), transparent 46%); pointer-events: none; }
	.studio-shell { position: relative; z-index: 1; padding-bottom: 48rpx; }
	.section-card, .summary-card, .list-card { background: rgba(255, 251, 246, 0.92); border: 1rpx solid rgba(117, 131, 112, 0.12); border-radius: 30rpx; box-shadow: 0 24rpx 80rpx rgba(106, 110, 89, 0.08); }
	.page-head, .summary-card, .section-card { padding: 24rpx; }
	.summary-grid { display: grid; gap: 16rpx; grid-template-columns: repeat(2, minmax(0, 1fr)); }
	.section-head, .export-head { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
	.section-title, .list-card__title, .meta-value { display: block; color: #2b3631; font-weight: 700; }
	.section-title { font-size: 32rpx; }
	.section-subtitle, .meta-hint, .list-card__desc { display: block; font-size: 24rpx; line-height: 1.7; color: #6d766d; }
	.meta-label { display: block; font-size: 22rpx; color: #7b8579; }
	.meta-value { margin-top: 8rpx; font-size: 34rpx; }
	.tone-soft { background: linear-gradient(135deg, #edf3e7, #e1ebde); }
	.list-stack > view + view { margin-top: 18rpx; }
	.field-label { display: block; margin-bottom: 10rpx; font-size: 24rpx; font-weight: 600; color: #49554b; }
	.field-input, .field-textarea { width: 100%; border-radius: 24rpx; background: #f8f6f1; border: 1rpx solid rgba(117, 131, 112, 0.12); color: #2c3530; font-size: 28rpx; }
	.field-input { height: 92rpx; padding: 0 24rpx; }
	.field-textarea { min-height: 220rpx; padding: 22rpx 24rpx; }
	.json-textarea { min-height: 300rpx; }
	.field-placeholder { color: #9ba39c; }
	.action-row { display: flex; flex-wrap: wrap; gap: 14rpx; }
	.primary-btn, .secondary-btn, .ghost-btn, .mini-btn { min-height: 84rpx; font-size: 28rpx; font-weight: 700; }
	.secondary-btn { background: rgba(236, 241, 232, 0.96) !important; color: #425041 !important; }
	.ghost-btn { background: transparent !important; border: 1rpx solid rgba(117, 131, 112, 0.16) !important; color: #5a6758 !important; }
	.mini-btn { min-height: 68rpx; padding: 0 22rpx; font-size: 24rpx; border-radius: 20rpx; }
	.empty-block { padding: 44rpx 24rpx; text-align: center; color: #6d766d; }
	.small-empty { padding: 24rpx; }
	.list-card { display: block; padding: 22rpx; }
	.preview-video { width: 100%; height: 420rpx; border-radius: 24rpx; background: #eff1ea; }
	.top-gap { margin-top: 16rpx; }
	.no-gap { margin-top: 0; }
</style>
