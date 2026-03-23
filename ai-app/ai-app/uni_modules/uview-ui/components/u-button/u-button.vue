<template>
	<button
		class="u-button"
		:class="[`u-button--${type}`, { 'u-button--disabled': disabled, 'u-button--loading': loading }]"
		:disabled="disabled || loading"
		@click="handleClick"
	>
		<view v-if="loading" class="u-button__loading"></view>
		<slot></slot>
	</button>
</template>

<script>
	export default {
		name: 'UButton',
		props: {
			type: {
				type: String,
				default: 'default'
			},
			loading: {
				type: Boolean,
				default: false
			},
			disabled: {
				type: Boolean,
				default: false
			}
		},
		methods: {
			handleClick(event) {
				if (this.disabled || this.loading) {
					return
				}
				this.$emit('click', event)
			}
		}
	}
</script>

<style scoped lang="scss">
	.u-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 10rpx;
		width: 100%;
		max-width: 100%;
		min-width: 0;
		margin: 0;
		padding: 18rpx 28rpx;
		border: none;
		border-radius: 24rpx;
		background: #eef2e9;
		color: #425041;
		line-height: 1.35;
		white-space: normal;
		word-break: break-word;
		text-align: center;
	}

	.u-button::after {
		border: none;
	}

	.u-button--primary {
		background: linear-gradient(135deg, #8fa77f, #6f876e);
		color: #fffefb;
	}

	.u-button--error {
		background: linear-gradient(135deg, #cb8c81, #b97469);
		color: #fffaf7;
	}

	.u-button--disabled,
	.u-button--loading {
		opacity: 0.72;
	}

	.u-button__loading {
		width: 24rpx;
		height: 24rpx;
		border: 4rpx solid rgba(255, 255, 255, 0.4);
		border-top-color: currentColor;
		border-radius: 50%;
		animation: u-button-spin 0.8s linear infinite;
	}

	@keyframes u-button-spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}
</style>
