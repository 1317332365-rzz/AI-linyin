<template>
	<view class="auth-page">
		<view class="auth-page__bg"></view>
		<view class="auth-page__glow auth-page__glow--1"></view>
		<view class="auth-page__glow auth-page__glow--2"></view>

		<view class="auth-shell">
			<view class="auth-card">
				<view class="auth-brand">
					<view class="auth-brand__badge">AI</view>
					<view class="auth-brand__text">
						<text class="auth-brand__title">动漫创作平台</text>
						<text class="auth-brand__desc">从项目创建到视频导出的一站式工作流</text>
					</view>
				</view>

				<view class="auth-header">
					<text class="auth-title">{{ isRegisterMode ? '创建账号' : '欢迎回来' }}</text>
					<text class="auth-subtitle">
						{{ isRegisterMode ? '注册后即可开始创建项目、生成剧本与管理导出任务' : '登录你的账号，继续你的动漫创作工作台' }}
					</text>
				</view>

				<view class="mode-row">
					<view class="mode-chip" :class="{ active: !isRegisterMode }" @click="switchMode('login')">
						<text>登录</text>
					</view>
					<view class="mode-chip" :class="{ active: isRegisterMode }" @click="switchMode('register')">
						<text>注册</text>
					</view>
				</view>

				<view class="form-stack">
					<view class="form-group">
						<text class="form-label">邮箱地址</text>
						<view class="input-shell">
							<text class="input-icon">✉</text>
							<u--input
								v-model="email"
								placeholder="请输入邮箱地址"
								:maxlength="254"
								confirm-type="next"
								clearable
								border="none"
								inputAlign="left"
							/>
						</view>
					</view>

					<view class="form-group">
						<text class="form-label">密码</text>
						<view class="input-shell">
							<text class="input-icon">•</text>
							<u--input
								v-model="password"
								type="password"
								placeholder="请输入密码"
								:maxlength="128"
								confirm-type="done"
								clearable
								border="none"
								inputAlign="left"
								@confirm="submitAuth"
							/>
						</view>
					</view>

					<view v-if="isRegisterMode" class="form-group">
						<text class="form-label">确认密码</text>
						<view class="input-shell">
							<text class="input-icon">•</text>
							<u--input
								v-model="confirmPassword"
								type="password"
								placeholder="请再次输入密码"
								:maxlength="128"
								confirm-type="done"
								clearable
								border="none"
								inputAlign="left"
								@confirm="submitAuth"
							/>
						</view>
					</view>
				</view>

				<view v-if="errorMessage" class="notice-card notice-card--error">
					<text class="notice-icon">!</text>
					<text class="notice-text">{{ errorMessage }}</text>
				</view>

				<u-button class="auth-btn" type="primary" :loading="buttonLoading" @click="submitAuth">
					{{ buttonText }}
				</u-button>

				<view class="mode-hint">
					<text>{{ isRegisterMode ? '已有账号？' : '还没有账号？' }}</text>
					<text class="mode-link" @click="switchMode(isRegisterMode ? 'login' : 'register')">
						{{ isRegisterMode ? '立即登录' : '立即注册' }}
					</text>
				</view>

				
			</view>
		</view>
	</view>
</template>

<script>
	import { authStatus, login, register } from '../../api/auth'
	import { relaunchTo } from '../../utils/navigation'
	import { clearAuthSession, getAuthToken, saveAuthSession } from '../../utils/storage'
	import UInput from '../../uni_modules/uview-ui/components/u--input/u--input.vue'
	import UButton from '../../uni_modules/uview-ui/components/u-button/u-button.vue'

	const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/

	const AUTH_ERROR_MAP = {
		Unauthorized: '当前登录状态已失效，请重新登录',
		'Username is required': '请输入用户名',
		'Please enter a valid username': '请输入有效的用户名',
		'Username already exists': '用户名已存在',
		'Invalid email or password': '邮箱或密码错误',
		'Email already exists': '该邮箱已注册',
		'Email is required': '请输入邮箱地址',
		'Please enter a valid email address': '请输入有效的邮箱地址',
		'Password is required': '请输入密码',
		'Password must be at least 6 characters': '密码长度不能少于 6 位',
		'Password must be 128 characters or fewer': '密码长度不能超过 128 位'
	}

	export default {
		components: {
			'u--input': UInput,
			UButton
		},
		data() {
			return {
				mode: 'login',
				email: '',
				password: '',
				confirmPassword: '',
				loading: false,
				checking: false,
				errorMessage: ''
			}
		},
		computed: {
			isRegisterMode() {
				return this.mode === 'register'
			},
			buttonLoading() {
				return this.loading || this.checking
			},
			buttonText() {
				if (this.checking) {
					return '正在检测登录状态...'
				}
				if (this.loading) {
					return this.isRegisterMode ? '正在注册...' : '正在登录...'
				}
				return this.isRegisterMode ? '创建账号' : '立即登录'
			}
		},
		onLoad() {
			this.tryRestoreSession()
		},
		methods: {
			formatAuthError(error, fallback) {
				const message = String((error && error.message) || '').trim()
				return AUTH_ERROR_MAP[message] || message || fallback
			},
			switchMode(mode) {
				if (this.buttonLoading || this.mode === mode) {
					return
				}
				this.mode = mode
				this.errorMessage = ''
				this.confirmPassword = ''
			},
			normalizeEmail(value) {
				return String(value || '').trim()
			},
			async tryRestoreSession() {
				const token = getAuthToken()
				if (!token) {
					return
				}
				this.checking = true
				try {
					const response = await authStatus()
					saveAuthSession({
						token,
						email: response.email || response.username || ''
					})
					relaunchTo('/views/projects/index')
				} catch (error) {
					const statusCode = Number((error && error.statusCode) || 0)
					if (statusCode === 401) {
						clearAuthSession()
					}
				} finally {
					this.checking = false
				}
			},
			validateForm() {
				const email = this.normalizeEmail(this.email)
				const password = String(this.password || '')

				if (!email) {
					return '请输入邮箱地址'
				}
				if (!EMAIL_RE.test(email)) {
					return '请输入有效的邮箱地址'
				}
				if (!password) {
					return '请输入密码'
				}
				if (this.isRegisterMode) {
					if (password.length < 6) {
						return '密码长度不能少于 6 位'
					}
					if (password !== String(this.confirmPassword || '')) {
						return '两次输入的密码不一致'
					}
				}
				return ''
			},
			async submitAuth() {
				const validationError = this.validateForm()
				if (validationError) {
					this.errorMessage = validationError
					return
				}

				this.errorMessage = ''
				this.loading = true
				try {
					const payload = {
						email: this.normalizeEmail(this.email),
						password: String(this.password || '')
					}
					const response = this.isRegisterMode ? await register(payload) : await login(payload)
					saveAuthSession(response)
					relaunchTo('/views/projects/index')
				} catch (error) {
					this.errorMessage = this.formatAuthError(
						error,
						this.isRegisterMode ? '注册失败，请稍后重试' : '登录失败，请稍后重试'
					)
				} finally {
					this.loading = false
				}
			}
		}
	}
</script>

<style scoped lang="scss">
	.auth-page {
		position: relative;
		min-height: 100vh;
		overflow: hidden;
		background:
			radial-gradient(circle at top, rgba(38, 190, 171, 0.16), transparent 30%),
			linear-gradient(180deg, #061a1d 0%, #071416 40%, #031012 100%);
	}

	.auth-page__bg {
		position: fixed;
		inset: 0;
		background:
			linear-gradient(135deg, rgba(68, 255, 218, 0.04) 0%, transparent 35%),
			linear-gradient(315deg, rgba(88, 190, 255, 0.05) 0%, transparent 40%);
		pointer-events: none;
	}

	.auth-page__glow {
		position: fixed;
		border-radius: 999rpx;
		filter: blur(80rpx);
		opacity: 0.5;
		pointer-events: none;
	}

	.auth-page__glow--1 {
		top: 120rpx;
		left: -80rpx;
		width: 320rpx;
		height: 320rpx;
		background: rgba(54, 230, 198, 0.18);
	}

	.auth-page__glow--2 {
		right: -100rpx;
		bottom: 180rpx;
		width: 360rpx;
		height: 360rpx;
		background: rgba(66, 167, 255, 0.14);
	}

	.auth-shell {
		position: relative;
		z-index: 2;
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx 28rpx;
	}

	.auth-card {
		width: 100%;
		max-width: 690rpx;
		padding: 36rpx 30rpx 32rpx;
		border-radius: 36rpx;
		background: rgba(10, 26, 30, 0.78);
		backdrop-filter: blur(18rpx);
		border: 1rpx solid rgba(127, 255, 225, 0.14);
		box-shadow:
			0 24rpx 80rpx rgba(0, 0, 0, 0.35),
			inset 0 1rpx 0 rgba(255, 255, 255, 0.06);
	}

	.auth-brand {
		display: flex;
		align-items: center;
		gap: 18rpx;
		margin-bottom: 30rpx;
		padding: 18rpx 20rpx;
		border-radius: 24rpx;
		background: rgba(255, 255, 255, 0.03);
		border: 1rpx solid rgba(127, 255, 225, 0.1);
	}

	.auth-brand__badge {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 76rpx;
		height: 76rpx;
		border-radius: 20rpx;
		background: linear-gradient(135deg, #3be0c4 0%, #1e8f95 100%);
		color: #ffffff;
		font-size: 28rpx;
		font-weight: 800;
		box-shadow: 0 12rpx 28rpx rgba(33, 213, 180, 0.28);
	}

	.auth-brand__text {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.auth-brand__title {
		font-size: 28rpx;
		font-weight: 700;
		color: #ecfffb;
	}

	.auth-brand__desc {
		margin-top: 6rpx;
		font-size: 22rpx;
		line-height: 1.6;
		color: rgba(222, 245, 241, 0.62);
	}

	.auth-header {
		margin-bottom: 28rpx;
	}

	.auth-title {
		display: block;
		font-size: 50rpx;
		line-height: 1.2;
		font-weight: 800;
		color: #f4fffd;
		letter-spacing: 1rpx;
	}

	.auth-subtitle {
		display: block;
		margin-top: 12rpx;
		font-size: 24rpx;
		line-height: 1.7;
		color: rgba(220, 241, 237, 0.7);
	}

	.mode-row {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16rpx;
		padding: 10rpx;
		border-radius: 999rpx;
		background: rgba(255, 255, 255, 0.04);
		border: 1rpx solid rgba(127, 255, 225, 0.08);
	}

	.mode-chip {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 84rpx;
		border-radius: 999rpx;
		color: rgba(219, 239, 235, 0.72);
		font-size: 28rpx;
		font-weight: 700;
		transition: all 0.2s ease;
	}

	.mode-chip.active {
		background: linear-gradient(135deg, #39e0c2 0%, #178990 100%);
		color: #ffffff;
		box-shadow: 0 12rpx 26rpx rgba(41, 220, 189, 0.22);
	}

	.form-stack {
		display: grid;
		gap: 22rpx;
		margin-top: 28rpx;
	}

	.form-group {
		display: grid;
		gap: 12rpx;
	}

	.form-label {
		padding-left: 6rpx;
		font-size: 24rpx;
		font-weight: 700;
		color: #dff7f1;
	}

	.input-shell {
		display: flex;
		align-items: center;
		min-height: 96rpx;
		padding: 0 22rpx;
		border-radius: 24rpx;
		background: rgba(255, 255, 255, 0.04);
		border: 1rpx solid rgba(127, 255, 225, 0.12);
		box-shadow: inset 0 1rpx 0 rgba(255, 255, 255, 0.03);
	}

	.input-icon {
		width: 36rpx;
		margin-right: 14rpx;
		font-size: 28rpx;
		font-weight: 700;
		color: #64e9d1;
		text-align: center;
	}

	.notice-card {
		display: flex;
		align-items: flex-start;
		gap: 12rpx;
		margin-top: 22rpx;
		padding: 18rpx 20rpx;
		border-radius: 20rpx;
		font-size: 24rpx;
		line-height: 1.7;
	}

	.notice-card--error {
		background: rgba(255, 104, 104, 0.12);
		border: 1rpx solid rgba(255, 121, 121, 0.18);
		color: #ffb8b8;
	}

	.notice-icon {
		margin-top: 2rpx;
		font-size: 24rpx;
		font-weight: 800;
	}

	.notice-text {
		flex: 1;
	}

	.auth-btn {
		width: 100%;
		margin-top: 26rpx;
		min-height: 94rpx;
		border-radius: 999rpx !important;
		overflow: hidden;
		font-size: 30rpx;
		font-weight: 800;
		letter-spacing: 1rpx;
		box-shadow: 0 16rpx 30rpx rgba(35, 202, 172, 0.22);
	}

	.mode-hint {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 12rpx;
		margin-top: 24rpx;
		font-size: 24rpx;
		color: rgba(220, 241, 237, 0.68);
	}

	.mode-link {
		color: #6ef0d7;
		font-weight: 800;
	}

	.auth-footer {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 12rpx;
		margin-top: 28rpx;
		padding-top: 24rpx;
		border-top: 1rpx solid rgba(127, 255, 225, 0.08);
		font-size: 22rpx;
		line-height: 1.7;
		color: rgba(220, 241, 237, 0.56);
	}

	.footer-pill {
		padding: 8rpx 16rpx;
		border-radius: 999rpx;
		background: rgba(91, 231, 206, 0.08);
		border: 1rpx solid rgba(127, 255, 225, 0.1);
		color: #cffff6;
	}

	:deep(.u-input) {
		background: transparent !important;
	}

	:deep(.u-input__content__field-wrapper__field) {
		font-size: 28rpx !important;
		color: #f3fffc !important;
	}

	:deep(.u-input__content__field-wrapper__field::placeholder) {
		color: rgba(213, 235, 231, 0.4) !important;
	}

	:deep(.u-button) {
		border: none !important;
		background: linear-gradient(135deg, #3be0c4 0%, #188992 100%) !important;
	}

	@media screen and (max-width: 360px) {
		.auth-card {
			padding: 30rpx 24rpx;
		}

		.auth-title {
			font-size: 44rpx;
		}

		.mode-chip {
			font-size: 26rpx;
		}
	}
</style>
