<template>
	<view class="studio-page">
		<LoadingProgress :visible="progress.visible" :value="progress.value" :label="progress.label" />
		<view class="studio-page__bg"></view>

		<view class="app-page studio-shell">
			<view class="section-card page-head">
				<text class="section-title">个人中心</text>
				<text class="section-subtitle">查看工作空间概况、维护模型配置，并管理当前登录账户。</text>
			</view>

			<view class="section-card">
				<view class="section-head">
					<text class="section-title">账户与空间</text>
				</view>
				<view class="summary-grid">
					<view class="summary-card tone-soft">
						<text class="meta-label">工作空间概况</text>
						<text class="meta-value">{{ projects.length }} 个项目</text>
						<text class="meta-hint">资产 {{ workspaceAssetTotal }} · 镜头 {{ workspaceShotTotal }}</text>
					</view>
				</view>
			</view>

			<view class="section-card">
				<view class="section-head">
					<text class="section-title">模型配置</text>
					<text class="info-chip">{{ selectedProcessLabel }}</text>
				</view>
				<view class="segment-row no-top-gap">
					<text v-for="item in processOptions" :key="item.value" class="segment-pill" :class="{ active: selectedProcess === item.value }" @click="changeProcess(item.value)">{{ item.label }}</text>
				</view>
				<view class="form-grid two-col top-gap">
					<view class="form-group">
						<text class="field-label">SDK 类型</text>
						<input v-model="llmConfig.sdk_type" class="field-input" type="text" placeholder="openai / dashscope" placeholder-class="field-placeholder" :adjust-position="false" />
					</view>
					<view class="form-group">
						<text class="field-label">模型名称</text>
						<input v-model="llmConfig.model" class="field-input" type="text" placeholder="请输入模型名称" placeholder-class="field-placeholder" :adjust-position="false" />
					</view>
				</view>
				<view class="form-group">
					<text class="field-label">API Key</text>
					<input v-model="llmConfig.api_key" class="field-input" type="text" placeholder="请输入 API Key" placeholder-class="field-placeholder" :adjust-position="false" />
				</view>
				<view class="form-group">
					<text class="field-label">Base URL</text>
					<input v-model="llmConfig.base_url" class="field-input" type="text" placeholder="可选，自定义模型网关地址" placeholder-class="field-placeholder" :adjust-position="false" />
				</view>
				<view class="form-grid two-col">
					<view class="form-group">
						<text class="field-label">Temperature</text>
						<input v-model="llmConfig.temperature" class="field-input" type="digit" placeholder="0.7" placeholder-class="field-placeholder" :adjust-position="false" />
					</view>
					<view class="form-group">
						<text class="field-label">Max Tokens</text>
						<input v-model="llmConfig.max_tokens" class="field-input" type="number" placeholder="1000" placeholder-class="field-placeholder" :adjust-position="false" />
					</view>
				</view>
				<view class="action-row compact-actions top-gap">
					<u-button class="secondary-btn" :loading="llmLoading" @click="loadConfig">{{ llmLoading ? '正在加载...' : '重新加载' }}</u-button>
					<u-button class="secondary-btn" :loading="llmSaving" @click="saveConfig">{{ llmSaving ? '正在保存...' : '保存配置' }}</u-button>
					<u-button class="primary-btn" type="primary" :loading="llmTesting" @click="testConfig">{{ llmTesting ? '正在测试...' : '测试连接' }}</u-button>
				</view>
				<view v-if="testResult.message" class="message-card top-gap" :class="testResult.status === 'success' ? 'message-card--success' : 'message-card--error'"><text>{{ testResult.message }}</text></view>
			</view>

			<view class="section-card">
				<text class="section-title">账户操作</text>
				<text class="section-subtitle">退出后会返回登录页，本地当前登录态会被清空。</text>
				<u-button class="danger-btn top-gap" type="error" @click="logoutUser">退出登录</u-button>
			</view>
		</view>
	</view>
</template>

<script>
	import LoadingProgress from '../../components/LoadingProgress.vue'
	import UButton from '../../uni_modules/uview-ui/components/u-button/u-button.vue'
	import { logout } from '../../api/auth'
	import { getLLMConfig, testLLM, updateLLMConfig } from '../../api/llm'
	import { listProjects } from '../../api/projects'
	import { ensureAuth, relaunchTo } from '../../utils/navigation'
	import { clearAuthSession, getCurrentUser } from '../../utils/storage'

	const DEFAULT_CONFIG = { model: '', api_key: '', base_url: '', temperature: 0.7, max_tokens: 1000, sdk_type: 'openai' }
	function safeText(value) { return String(value || '').trim() }

	export default {
		components: { LoadingProgress, UButton },
		data() {
			return {
				initialized: false,
				progress: { visible: false, value: 0, label: '' },
				progressTimer: null,
				progressHideTimer: null,
				loading: false,
				currentUser: '',
				projects: [],
				selectedProcess: 'general',
				processOptions: [{ value: 'general', label: '通用' }, { value: 'script', label: '剧本' }, { value: 'character', label: '角色' }, { value: 'scene', label: '场景' }, { value: 'video', label: '视频' }],
				llmConfig: { ...DEFAULT_CONFIG },
				llmLoading: false,
				llmSaving: false,
				llmTesting: false,
				testResult: { status: '', message: '' }
			}
		},
		computed: {
			workspaceAssetTotal() { return this.projects.reduce((total, project) => total + this.assetCount(project), 0) },
			workspaceShotTotal() { return this.projects.reduce((total, project) => total + this.shotCount(project), 0) },
			selectedProcessLabel() { const options = Array.isArray(this.processOptions) ? this.processOptions : []; const target = options.find((item) => item.value === this.selectedProcess); return target ? target.label : '通用' }
		},
		onShow() {
			if (!ensureAuth()) { return }
			this.currentUser = getCurrentUser()
			if (!this.initialized) {
				this.initializePage()
				return
			}
			this.refreshProfile(true)
		},
		onPullDownRefresh() {
			if (!ensureAuth()) {
				uni.stopPullDownRefresh()
				return
			}
			this.refreshProfile()
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
			assetCount(project) { return Array.isArray(project && project.assets) ? project.assets.length : 0 },
			shotCount(project) { return Array.isArray(project && project.shots) ? project.shots.length : 0 },
			buildConfigPayload() { return { ...this.llmConfig, process: this.selectedProcess, temperature: Number(this.llmConfig.temperature || DEFAULT_CONFIG.temperature), max_tokens: Number(this.llmConfig.max_tokens || DEFAULT_CONFIG.max_tokens) } },
			async fetchProjects() {
				const response = await listProjects()
				this.projects = Array.isArray(response) ? response : []
				return this.projects
			},
			async fetchConfig() {
				const response = await getLLMConfig(this.selectedProcess)
				this.llmConfig = { ...DEFAULT_CONFIG, ...(response || {}) }
				this.testResult = { status: '', message: '' }
				return this.llmConfig
			},
			async initializePage() {
				try {
					await this.runTask('正在同步个人中心', async () => {
						await this.fetchProjects()
						await this.fetchConfig()
					}, { successText: '个人中心已就绪' })
					this.initialized = true
				} catch (error) {
					this.showToast(error.message || '初始化失败')
				} finally {
					uni.stopPullDownRefresh()
				}
			},
			async refreshProfile(silent = false) {
				this.loading = true
				try {
					if (silent) {
						await this.fetchProjects()
						await this.fetchConfig()
					} else {
						await this.runTask('正在刷新个人中心', async () => {
							await this.fetchProjects()
							await this.fetchConfig()
						}, { successText: '个人中心已刷新' })
					}
				} catch (error) {
					this.showToast(error.message || '刷新失败')
				} finally {
					this.loading = false
					uni.stopPullDownRefresh()
				}
			},
			changeProcess(process) {
				if (!process || this.selectedProcess === process) {
					return
				}
				this.selectedProcess = process
				this.loadConfig(true)
			},
			async loadConfig(silent = false) {
				this.llmLoading = true
				try {
					if (silent) {
						await this.fetchConfig()
					} else {
						await this.runTask('正在加载模型配置', () => this.fetchConfig(), { successText: '模型配置已更新' })
					}
				} catch (error) {
					this.testResult = { status: 'error', message: error.message || '加载模型配置失败' }
				} finally {
					this.llmLoading = false
				}
			},
			async saveConfig() {
				this.llmSaving = true
				try {
					const response = await this.runTask('正在保存模型配置', () => updateLLMConfig(this.buildConfigPayload()), { successText: '模型配置已保存' })
					this.llmConfig = { ...DEFAULT_CONFIG, ...(response || {}) }
					this.testResult = { status: 'success', message: '模型配置已保存' }
				} catch (error) {
					this.testResult = { status: 'error', message: error.message || '保存模型配置失败' }
				} finally {
					this.llmSaving = false
				}
			},
			async testConfig() {
				this.llmTesting = true
				try {
					const response = await this.runTask('正在测试模型连接', () => testLLM(this.buildConfigPayload()), { successText: '模型连接测试完成' })
					this.testResult = { status: response.status || 'success', message: response.message || '连接测试成功' }
				} catch (error) {
					this.testResult = { status: 'error', message: error.message || '测试连接失败' }
				} finally {
					this.llmTesting = false
				}
			},
			async logoutUser() {
				try {
					await logout()
				} catch (error) {}
				clearAuthSession()
				relaunchTo('/views/account/index')
			}
		}
	}
</script>

<style scoped lang="scss">
	.studio-page { position: relative; min-height: 100vh; background: linear-gradient(180deg, #f6f1e8 0%, #f5f4ed 38%, #edf1ea 100%); color: #2a342f; }
	.studio-page__bg { position: fixed; inset: 0; background: radial-gradient(circle at top left, rgba(222, 226, 204, 0.88), transparent 38%), radial-gradient(circle at top right, rgba(210, 223, 211, 0.7), transparent 34%), radial-gradient(circle at bottom, rgba(233, 238, 226, 0.92), transparent 46%); pointer-events: none; }
	.studio-shell { position: relative; z-index: 1; padding-bottom: 48rpx; }
	.section-card, .summary-card, .message-card { background: rgba(255, 251, 246, 0.92); border: 1rpx solid rgba(117, 131, 112, 0.12); border-radius: 30rpx; box-shadow: 0 24rpx 80rpx rgba(106, 110, 89, 0.08); }
	.page-head, .summary-card, .section-card { padding: 24rpx; }
	.summary-grid, .form-grid { display: grid; gap: 16rpx; }
	.summary-grid, .two-col { grid-template-columns: repeat(2, minmax(0, 1fr)); }
	.section-head { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
	.section-title, .meta-value { display: block; color: #2b3631; font-weight: 700; }
	.section-title { font-size: 32rpx; }
	.section-subtitle, .meta-hint { display: block; font-size: 24rpx; line-height: 1.7; color: #6d766d; }
	.meta-label { display: block; font-size: 22rpx; color: #7b8579; }
	.meta-value { margin-top: 8rpx; font-size: 34rpx; }
	.tone-soft { background: linear-gradient(135deg, #edf3e7, #e1ebde); }
	.info-chip, .segment-pill { display: inline-flex; align-items: center; justify-content: center; min-height: 60rpx; padding: 0 22rpx; border-radius: 999rpx; font-size: 23rpx; color: #657062; background: rgba(242, 245, 237, 0.94); border: 1rpx solid rgba(117, 131, 112, 0.1); }
	.segment-row, .action-row { display: flex; flex-wrap: wrap; gap: 14rpx; }
	.no-top-gap { margin-top: 0; }
	.segment-pill.active { background: linear-gradient(135deg, #edf3e7, #e1ebde); }
	.field-label { display: block; margin-bottom: 10rpx; font-size: 24rpx; font-weight: 600; color: #49554b; }
	.field-input { width: 100%; height: 92rpx; padding: 0 24rpx; border-radius: 24rpx; background: #f8f6f1; border: 1rpx solid rgba(117, 131, 112, 0.12); color: #2c3530; font-size: 28rpx; }
	.field-placeholder { color: #9ba39c; }
	.primary-btn, .secondary-btn, .danger-btn, .mini-btn { min-height: 84rpx; font-size: 28rpx; font-weight: 700; }
	.secondary-btn { background: rgba(236, 241, 232, 0.96) !important; color: #425041 !important; }
	.danger-btn { background: linear-gradient(135deg, #cb8c81, #b97469) !important; color: #fffaf7 !important; }
	.mini-btn { min-height: 68rpx; padding: 0 22rpx; font-size: 24rpx; border-radius: 20rpx; }
	.message-card { padding: 18rpx 20rpx; font-size: 24rpx; line-height: 1.7; }
	.message-card--error { background: rgba(213, 159, 150, 0.16); border: 1rpx solid rgba(192, 118, 104, 0.22); color: #8a4f45; }
	.message-card--success { background: rgba(166, 192, 154, 0.16); border: 1rpx solid rgba(115, 145, 102, 0.2); color: #53644e; }
	.top-gap { margin-top: 16rpx; }
</style>
