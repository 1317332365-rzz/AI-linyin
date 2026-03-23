<template>
	<view v-if="visible" class="loading-progress">
		<view class="loading-progress__panel">
			<view class="loading-progress__header">
				<text class="loading-progress__label">{{ label || '正在处理' }}</text>
				<text class="loading-progress__value">{{ safeValue }}%</text>
			</view>
			<view class="loading-progress__track">
				<view class="loading-progress__bar" :style="{ width: `${safeValue}%` }"></view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		name: 'LoadingProgress',
		props: {
			visible: {
				type: Boolean,
				default: false
			},
			label: {
				type: String,
				default: ''
			},
			value: {
				type: Number,
				default: 0
			}
		},
		computed: {
			safeValue() {
				const value = Number(this.value)
				if (!Number.isFinite(value)) {
					return 0
				}
				if (value < 0) {
					return 0
				}
				if (value > 100) {
					return 100
				}
				return Math.round(value)
			}
		}
	}
</script>

<style scoped lang="scss">
	.loading-progress {
		position: fixed;
		top: calc(18rpx + env(safe-area-inset-top));
		left: 24rpx;
		right: 24rpx;
		z-index: 120;
		pointer-events: none;
	}

	.loading-progress__panel {
		padding: 18rpx 20rpx;
		border-radius: 24rpx;
		background: rgba(255, 252, 247, 0.96);
		border: 1rpx solid rgba(118, 136, 118, 0.16);
		box-shadow: 0 16rpx 50rpx rgba(98, 103, 82, 0.14);
	}

	.loading-progress__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16rpx;
		margin-bottom: 12rpx;
	}

	.loading-progress__label,
	.loading-progress__value {
		font-size: 22rpx;
		color: #445248;
	}

	.loading-progress__label {
		font-weight: 700;
	}

	.loading-progress__value {
		color: #6d7b70;
	}

	.loading-progress__track {
		height: 12rpx;
		overflow: hidden;
		border-radius: 999rpx;
		background: rgba(132, 152, 130, 0.16);
	}

	.loading-progress__bar {
		height: 100%;
		border-radius: inherit;
		background: linear-gradient(90deg, #9ab08b, #6f8f77);
		transition: width 0.24s ease;
	}
</style>
