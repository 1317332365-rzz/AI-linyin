<template>
	<view class="studio-tabbar">
		<view
			v-for="item in items"
			:key="item.key"
			class="tab-item"
			:class="{ active: current === item.key }"
			@click="handleClick(item)"
		>
			<text class="tab-label">{{ item.label }}</text>
			<text class="tab-caption">{{ item.caption }}</text>
		</view>
	</view>
</template>

<script>
	export default {
		name: 'StudioTabBar',
		props: {
			current: {
				type: String,
				default: 'create'
			}
		},
		data() {
			return {
				items: [
					{ key: 'create', label: '动漫生成', caption: '项目 / 剧本 / 资产 / 导演' },
					{ key: 'export', label: '视频导出', caption: '导出管理与成片整理' },
					{ key: 'profile', label: '个人中心', caption: '账号与工作空间设置' }
				]
			}
		},
		methods: {
			handleClick(item) {
				if (!item || item.key === this.current) {
					return
				}
				this.$emit('change', item.key)
			}
		}
	}
</script>

<style scoped lang="scss">
	.studio-tabbar {
		position: fixed;
		left: 20rpx;
		right: 20rpx;
		bottom: 20rpx;
		z-index: 90;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 14rpx;
		padding: 16rpx;
		padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
		border-radius: 32rpx;
		background: rgba(255, 251, 245, 0.96);
		border: 1rpx solid rgba(122, 137, 117, 0.12);
		box-shadow: 0 24rpx 80rpx rgba(112, 114, 90, 0.16);
		backdrop-filter: blur(16rpx);
	}

	.tab-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 96rpx;
		padding: 14rpx 10rpx;
		border-radius: 24rpx;
		background: transparent;
		color: #728072;
		text-align: center;
	}

	.tab-item.active {
		background: linear-gradient(135deg, #eff4e7, #e5eedf);
		color: #344339;
		box-shadow: inset 0 0 0 1rpx rgba(123, 145, 120, 0.18);
	}

	.tab-label {
		font-size: 25rpx;
		font-weight: 700;
	}

	.tab-caption {
		margin-top: 6rpx;
		font-size: 19rpx;
		line-height: 1.4;
		opacity: 0.9;
	}
</style>
