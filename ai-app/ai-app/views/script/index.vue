<template>
	<view class="redirect-page"><text>正在进入剧本模块...</text></view>
</template>

<script>
	export default {
		onLoad() {
			uni.redirectTo({ url: '/views/projects/index?tab=create&panel=script' })
		}
	}
</script>

<style scoped>
	.redirect-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #667064; }
</style>
