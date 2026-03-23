<script>
	export default {
		onLaunch() {}
	}
</script>

<style lang="scss">
	/*每个页面公共css */
	page {
		background:
			radial-gradient(circle at top, rgba(33, 96, 101, 0.6), rgba(10, 29, 32, 0.94) 42%, #071011 100%);
		color: #e9f7f2;
		font-size: 28rpx;
	}

	view,
	text,
	scroll-view,
	swiper,
	swiper-item,
	image,
	video,
	input,
	textarea,
	button {
		box-sizing: border-box;
	}

	button {
		margin: 0;
		padding: 0;
		background: linear-gradient(135deg, #15b29b, #0c8878);
		color: #f6fffd;
		border: none;
		border-radius: 24rpx;
		font-size: 28rpx;
		line-height: 1.2;
	}

	button::after {
		border: none;
	}

	input,
	textarea {
		width: 100%;
		color: #ecfaf6;
	}

	.app-page {
		min-height: 100vh;
		padding: 28rpx 24rpx 220rpx;
	}

	.hero-card,
	.section-card,
	.item-card,
	.notice-card {
		background: rgba(9, 27, 29, 0.78);
		border: 1rpx solid rgba(105, 168, 159, 0.2);
		border-radius: 28rpx;
		box-shadow: 0 24rpx 80rpx rgba(1, 10, 11, 0.22);
		backdrop-filter: blur(14rpx);
	}

	.hero-card {
		padding: 28rpx;
		margin-bottom: 24rpx;
	}

	.section-card,
	.notice-card {
		padding: 24rpx;
		margin-bottom: 20rpx;
	}

	.item-card {
		padding: 22rpx;
		margin-bottom: 16rpx;
	}

	.eyebrow {
		display: block;
		margin-bottom: 10rpx;
		color: #7ed7c6;
		font-size: 22rpx;
		letter-spacing: 4rpx;
		text-transform: uppercase;
	}

	.page-title {
		display: block;
		font-size: 44rpx;
		font-weight: 700;
		line-height: 1.2;
		color: #f4fffc;
	}

	.page-subtitle,
	.muted,
	.form-hint,
	.helper-text {
		display: block;
		color: #8db7af;
		line-height: 1.6;
	}

	.page-subtitle {
		margin-top: 10rpx;
		font-size: 24rpx;
	}

	.section-title,
	.card-title {
		display: block;
		font-size: 32rpx;
		font-weight: 700;
		color: #f0fffb;
	}

	.section-title {
		margin-bottom: 18rpx;
	}

	.card-title {
		margin-bottom: 8rpx;
	}

	.form-group {
		margin-bottom: 20rpx;
	}

	.form-label {
		display: block;
		margin-bottom: 12rpx;
		font-size: 24rpx;
		color: #c7ece5;
	}

	.form-input,
	.form-textarea,
	.form-picker,
	.inline-chip,
	.status-chip {
		background: rgba(13, 37, 39, 0.9);
		border: 1rpx solid rgba(115, 178, 169, 0.18);
		border-radius: 20rpx;
	}

	.form-input,
	.form-textarea {
		padding: 22rpx 20rpx;
		font-size: 28rpx;
	}

	.form-textarea {
		min-height: 220rpx;
	}

	.form-picker {
		padding: 20rpx;
	}

	.inline-row,
	.action-row,
	.meta-row,
	.grid-two {
		display: flex;
		flex-wrap: wrap;
		gap: 16rpx;
	}

	.grid-two > view,
	.grid-two > button {
		flex: 1 1 calc(50% - 8rpx);
		min-width: 0;
	}

	.action-btn,
	.secondary-btn,
	.ghost-btn,
	.mini-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 84rpx;
		padding: 0 28rpx;
		border-radius: 22rpx;
		font-weight: 600;
	}

	.secondary-btn {
		background: rgba(24, 58, 59, 0.96);
		color: #dcfaf4;
	}

	.ghost-btn {
		background: transparent;
		border: 1rpx solid rgba(126, 215, 198, 0.28);
		color: #d8faf3;
	}

	.mini-btn {
		min-height: 66rpx;
		padding: 0 22rpx;
		font-size: 24rpx;
		border-radius: 18rpx;
	}

	.chip-row {
		display: flex;
		flex-wrap: wrap;
		gap: 12rpx;
	}

	.inline-chip,
	.status-chip {
		display: inline-flex;
		align-items: center;
		padding: 12rpx 18rpx;
		font-size: 22rpx;
		color: #cdeee8;
	}

	.status-chip.active,
	.inline-chip.active {
		background: rgba(21, 178, 155, 0.2);
		border-color: rgba(92, 214, 194, 0.38);
		color: #8ef0df;
	}

	.notice-card.error,
	.status-panel.error {
		border-color: rgba(244, 114, 114, 0.32);
		background: rgba(74, 20, 27, 0.44);
	}

	.notice-card.success,
	.status-panel.success {
		border-color: rgba(94, 234, 212, 0.26);
		background: rgba(7, 61, 54, 0.42);
	}

	.empty-state {
		padding: 54rpx 24rpx;
		text-align: center;
		color: #94b9b2;
		line-height: 1.7;
	}

	.image-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16rpx;
	}

	.preview-image,
	.preview-video {
		width: 100%;
		border-radius: 22rpx;
		background: rgba(7, 18, 20, 0.92);
		border: 1rpx solid rgba(105, 168, 159, 0.14);
	}

	.preview-image {
		height: 320rpx;
	}

	.preview-video {
		height: 360rpx;
	}

	.divider {
		height: 1rpx;
		margin: 16rpx 0;
		background: rgba(118, 176, 168, 0.12);
	}

	.fixed-space {
		height: calc(120rpx + env(safe-area-inset-bottom));
	}
</style>
