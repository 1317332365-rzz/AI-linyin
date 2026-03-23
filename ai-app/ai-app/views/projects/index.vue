<template>
	<view class="studio-page">
		<LoadingProgress :visible="progress.visible" :value="progress.value" :label="progress.label" />
		<view class="studio-page__bg"></view>

		<view class="app-page studio-shell">
			<view class="section-card tab-card">
				<view class="section-head">
					<view>
						<text class="section-title">动漫生成</text>
						<text class="section-subtitle">项目、剧本、资产、导演四个阶段顺序推进，切换时保留当前编辑状态。</text>
					</view>
				</view>
				<view class="segment-row no-top-gap">
					<text
						v-for="item in createTabs"
						:key="item.key"
						class="segment-pill"
						:class="{ active: activeCreateTab === item.key }"
						@click="handleCreateTabChange(item.key)"
					>
						{{ item.label }}
					</text>
				</view>
			</view>

			<view v-show="activeCreateTab === 'project'" class="panel-stack">
				<view class="section-card">
					<view class="section-head">
						<view>
							<text class="section-title">项目工作区</text>
							<text class="section-subtitle">每个账号的项目和缓存分开保存，继续创作时会自动恢复当前项目。</text>
						</view>
						<u-button class="secondary-btn mini-btn" @click="loadProjects">刷新</u-button>
					</view>
					<view v-if="activeProjectCache" class="focus-card top-gap">
						<text class="focus-title">{{ activeProjectCache.name || '未命名项目' }}</text>
						<text class="section-subtitle">{{ activeProjectCache.script_title || '未填写剧本标题' }} · 第 {{ activeProjectCache.episode_no || 1 }} 集</text>
						<view class="chip-row top-gap">
							<text class="info-chip">{{ providerText(activeProjectCache.video_provider) }}</text>
							<text class="info-chip">资产 {{ assetCount(activeProjectCache) }}</text>
							<text class="info-chip">镜头 {{ shotCount(activeProjectCache) }}</text>
						</view>
						<u-button class="primary-btn mini-btn top-gap" type="primary" @click="openCurrentProject">继续创作</u-button>
					</view>
				</view>

				<view class="section-card">
					<text class="section-title">创建新项目</text>
					<view class="form-grid two-col top-gap">
						<view class="form-group">
							<text class="field-label">项目名称</text>
							<input v-model="projectName" class="field-input" type="text" placeholder="例如：仙侠短剧第一季" placeholder-class="field-placeholder" :adjust-position="false" />
						</view>
						<view class="form-group">
							<text class="field-label">剧本标题</text>
							<input v-model="scriptTitle" class="field-input" type="text" placeholder="例如：剑心追月" placeholder-class="field-placeholder" :adjust-position="false" />
						</view>
					</view>
					<view class="form-group">
						<text class="field-label">起始集数</text>
						<picker :range="episodeChoices" :value="episodeChoiceIndex" @change="handleEpisodeChange">
							<view class="picker-field">第 {{ selectedEpisode }} 集</view>
						</picker>
					</view>
					<u-button class="primary-btn large-btn" type="primary" :loading="creating" @click="createNewProject">{{ creating ? '正在创建项目...' : '创建并进入剧本阶段' }}</u-button>
				</view>

				<view class="section-card">
					<view class="section-head">
						<view>
							<text class="section-title">项目历史</text>
							<text class="section-subtitle">按最近更新时间排序，点击可继续创作</text>
						</view>
					</view>
					<view v-if="loading" class="empty-block"><text>正在同步项目列表...</text></view>
					<view v-else-if="!projects.length" class="empty-block"><text>还没有项目，先创建一个再开始。</text></view>
					<view v-else class="project-history-list top-gap">
						<view v-for="project in projects" :key="project.id" class="project-history-card" @click="openProject(project)">
							<view class="project-history-line"></view>
							<view class="project-history-body">
								<text class="list-card__title">{{ project.name || '未命名项目' }}</text>
								<text class="project-history-meta">{{ formatProjectUpdatedAt(project.updatedAt || project.createdAt) }} · {{ project.script_title || '未填写剧本标题' }} · 第 {{ project.episode_no || 1 }} 集</text>
								<view class="chip-row top-gap">
									<text class="info-chip">{{ providerText(project.video_provider) }}</text>
									<text class="info-chip">资产 {{ assetCount(project) }}</text>
									<text class="info-chip">镜头 {{ shotCount(project) }}</text>
								</view>
							</view>
							<u-button class="ghost-btn mini-btn project-history-action">打开</u-button>
						</view>
					</view>
				</view>
			</view>

			<view v-show="activeCreateTab === 'script'" class="panel-stack">
				<view v-if="!hasProject" class="section-card empty-block">
					<text>先在项目模块创建或打开项目，再继续写剧本。</text>
					<u-button class="primary-btn mini-btn top-gap" type="primary" @click="handleCreateTabChange('project')">去项目模块</u-button>
				</view>
				<template v-else>
					<view class="section-card">
						<view class="section-head">
							<view>
								<text class="section-title">剧本设定</text>
								<text class="section-subtitle">先写本集故事，再生成分镜结果并同步到导演模块。</text>
							</view>
							<text class="info-chip active">状态自动保留</text>
						</view>
						<view class="form-grid two-col top-gap">
							<view class="form-group">
								<text class="field-label">项目名称</text>
								<input v-model="currentProjectName" class="field-input" type="text" placeholder="请输入项目名称" placeholder-class="field-placeholder" :adjust-position="false" />
							</view>
							<view class="form-group">
								<text class="field-label">剧本标题</text>
								<input v-model="currentScriptTitle" class="field-input" type="text" placeholder="请输入剧本标题" placeholder-class="field-placeholder" :adjust-position="false" />
							</view>
						</view>
						<view class="form-grid three-col">
							<view class="form-group">
								<text class="field-label">集数</text>
								<picker :range="episodeOptions" :value="episodeIndex" @change="handleCurrentEpisodeChange"><view class="picker-field">第 {{ currentEpisodeNo }} 集</view></picker>
							</view>
							<view class="form-group">
								<text class="field-label">视频接口</text>
								<picker :range="providerLabels" :value="providerIndex" @change="handleProviderChange"><view class="picker-field">{{ providerLabels[providerIndex] }}</view></picker>
							</view>
							<view class="form-group">
								<text class="field-label">目标时长</text>
								<picker :range="durationLabels" :value="durationIndex" @change="handleDurationChange"><view class="picker-field">{{ durationLabels[durationIndex] }}</view></picker>
							</view>
						</view>
						<view v-if="targetDuration === 'custom'" class="form-group">
							<text class="field-label">自定义时长</text>
							<input v-model="customDuration" class="field-input" type="text" placeholder="例如：40s 或 6min" placeholder-class="field-placeholder" :adjust-position="false" />
						</view>
						<view class="action-row compact-actions top-gap">
							<u-button class="secondary-btn" :loading="saving" @click="saveProject">保存项目</u-button>
							<u-button class="ghost-btn" @click="addEpisode">新增集数</u-button>
							<u-button class="ghost-btn" @click="loadProject(true)">重新加载</u-button>
						</view>
					</view>

					<view class="section-card">
						<text class="section-title">本集剧本输入</text>
						<view class="form-group top-gap">
							<textarea v-model="scriptInput" class="field-textarea large-textarea" placeholder="输入本集故事梗概、人物冲突和关键转折" placeholder-class="field-placeholder"></textarea>
						</view>
						<view v-if="errorMessage" class="message-card message-card--error"><text>{{ errorMessage }}</text></view>
						<view class="action-row compact-actions top-gap">
							<u-button class="primary-btn" type="primary" :loading="parsing" @click="parseCurrentScript">{{ parsing ? '正在生成分镜脚本...' : '生成分镜脚本' }}</u-button>
							<u-button class="secondary-btn" @click="saveProject">先保存草稿</u-button>
						</view>
					</view>

					<view v-if="sceneRows.length" class="section-card">
						<view class="section-head">
							<text class="section-title">分镜结果</text>
							<u-button class="secondary-btn mini-btn" @click="syncScenesToShots">同步到导演模块</u-button>
						</view>
						<view class="list-stack top-gap">
							<view v-for="(scene, index) in sceneRows.slice(0, 8)" :key="`scene-${index}`" class="list-card list-card--stack">
								<text class="list-card__title">场次 {{ scene.scene_id || index + 1 }} · {{ scene.duration || '5s' }}</text>
								<text class="list-card__desc">{{ scene.description || '暂无场景描述' }}</text>
								<text class="meta-hint">{{ scene.shot_description || '暂无镜头摘要' }}</text>
							</view>
						</view>
					</view>

					<view class="section-card">
						<text class="section-title">结果 JSON</text>
						<textarea v-model="rawResultText" class="field-textarea json-textarea top-gap" placeholder="生成完成后，可直接微调 JSON" placeholder-class="field-placeholder"></textarea>
						<view class="action-row compact-actions top-gap">
							<u-button class="secondary-btn" @click="applyEditedResult">应用修改</u-button>
							<u-button class="ghost-btn" @click="resetEditedResult">恢复原结果</u-button>
						</view>
					</view>
				</template>
			</view>

			<view v-show="activeCreateTab === 'assets'" class="panel-stack">
				<view v-if="!hasProject" class="section-card empty-block">
					<text>先选中项目，再生成角色和场景资产。</text>
					<u-button class="primary-btn mini-btn top-gap" type="primary" @click="handleCreateTabChange('project')">去项目模块</u-button>
				</view>
				<template v-else>
					<view class="section-card">
						<view class="section-head">
							<view>
								<text class="section-title">AI 提取推荐</text>
								<text class="section-subtitle">只做推荐，不会自动写入表单。角色行支持长按快速导入。</text>
							</view>
						</view>
						<view class="action-row compact-actions top-gap">
							<u-button class="secondary-btn mini-btn" :loading="extractingCharacters" :disabled="extractingScenes || !hasScriptInput" @click="extractCharactersByAi">{{ extractingCharacters ? '正在提取角色...' : 'AI 提取角色' }}</u-button>
							<u-button class="secondary-btn mini-btn" :loading="extractingScenes" :disabled="extractingCharacters || !hasScriptInput" @click="extractScenesByAi">{{ extractingScenes ? '正在提取场景...' : 'AI 提取场景' }}</u-button>
						</view>
						<view v-if="recommendActionMessage" class="message-card recommend-message top-gap"><text>{{ recommendActionMessage }}</text></view>
						<view v-if="!hasRecommendationCandidates" class="empty-block top-gap"><text>先在剧本模块生成分镜，或点击上方按钮提取推荐。</text></view>
						<template v-else>
							<view v-if="recommendedSceneCandidates.length" class="top-gap">
								<text class="field-label">场景推荐</text>
								<scroll-view scroll-x class="recommend-scroll">
									<view class="recommend-table">
										<view class="recommend-row recommend-head">
											<text class="recommend-col col-name">场景</text>
											<text class="recommend-col col-desc">描述</text>
											<text class="recommend-col col-status">状态</text>
											<text class="recommend-col col-action">操作</text>
										</view>
										<view v-for="(item, index) in recommendedSceneCandidates" :key="`scene-rec-${index}`" class="recommend-row">
											<text class="recommend-col col-name">{{ item.name }}</text>
											<text class="recommend-col col-desc">{{ item.description || item.shotSummary || '-' }}</text>
											<text class="recommend-col col-status">{{ item.generated ? `已生成：${item.matchedAssets.join('、')}` : '推荐生成' }}</text>
											<view class="recommend-col col-action">
												<u-button class="ghost-btn mini-btn" @click="fillSceneFromCandidate(item)">导入</u-button>
											</view>
										</view>
									</view>
								</scroll-view>
							</view>
							<view v-if="recommendedCharacterCandidates.length" class="top-gap">
								<text class="field-label">角色推荐（长按可导入）</text>
								<scroll-view scroll-x class="recommend-scroll">
									<view class="recommend-table">
										<view class="recommend-row recommend-head">
											<text class="recommend-col col-name">角色</text>
											<text class="recommend-col col-role">定位</text>
											<text class="recommend-col col-desc">目标 / 视觉锚点</text>
											<text class="recommend-col col-status">状态</text>
											<text class="recommend-col col-action">操作</text>
										</view>
										<view
											v-for="(item, index) in recommendedCharacterCandidates"
											:key="`char-rec-${index}`"
											class="recommend-row recommend-row--importable"
											@longpress="importCharacterFromCandidate(item, true)"
										>
											<text class="recommend-col col-name">{{ item.name || '-' }}</text>
											<text class="recommend-col col-role">{{ item.role || '-' }}</text>
											<text class="recommend-col col-desc">{{ [item.goal, item.visualAnchor].filter(Boolean).join(' | ') || '-' }}</text>
											<text class="recommend-col col-status">{{ item.generated ? `已生成：${item.matchedAssets.join('、')}` : '推荐生成' }}</text>
											<view class="recommend-col col-action">
												<u-button class="ghost-btn mini-btn" @click="importCharacterFromCandidate(item)">导入</u-button>
											</view>
										</view>
									</view>
								</scroll-view>
							</view>
						</template>
					</view>

					<view class="section-card">
						<text class="section-title">角色资产</text>
						<view class="form-group top-gap"><text class="field-label">角色名称</text><input v-model="currentCharacter.name" class="field-input" type="text" placeholder="例如：叶青霜" placeholder-class="field-placeholder" :adjust-position="false" /></view>
						<view class="form-group"><text class="field-label">角色描述</text><textarea v-model="currentCharacter.description" class="field-textarea" placeholder="描述外貌、年龄感、服装和角色气质" placeholder-class="field-placeholder"></textarea></view>
						<view class="form-group"><text class="field-label">造型版本</text><picker :range="wardrobeOptions" :value="wardrobeIndex" @change="handleWardrobeChange"><view class="picker-field">{{ currentCharacter.wardrobe }}</view></picker></view>
						<view v-if="currentCharacter.wardrobe === '自定义'" class="form-group"><text class="field-label">自定义造型</text><input v-model="currentCharacter.customWardrobe" class="field-input" type="text" placeholder="例如：雨夜战损版" placeholder-class="field-placeholder" :adjust-position="false" /></view>
						<view class="form-group"><text class="field-label">角色提示词</text><textarea v-model="currentCharacter.prompt" class="field-textarea" placeholder="可手动调整，也可先点增强提示词" placeholder-class="field-placeholder"></textarea></view>
						<view class="action-row compact-actions">
							<u-button class="secondary-btn" :loading="characterEnhancing" @click="enhanceCharacterPrompt">{{ characterEnhancing ? '正在增强...' : '增强提示词' }}</u-button>
							<u-button class="primary-btn" type="primary" :loading="characterLoading" @click="generateCharacterAsset">{{ characterLoading ? '正在生成...' : '生成角色资产' }}</u-button>
						</view>
					</view>

					<view class="section-card">
						<text class="section-title">场景资产</text>
						<view class="form-group top-gap"><text class="field-label">场景名称</text><input v-model="currentScene.name" class="field-input" type="text" placeholder="例如：青云山门" placeholder-class="field-placeholder" :adjust-position="false" /></view>
						<view class="form-group"><text class="field-label">场景描述</text><textarea v-model="currentScene.description" class="field-textarea" placeholder="描述空间关系、建筑、天气和氛围" placeholder-class="field-placeholder"></textarea></view>
						<view class="form-group"><text class="field-label">场景提示词</text><textarea v-model="currentScene.prompt" class="field-textarea" placeholder="可手动调整，也可先点增强提示词" placeholder-class="field-placeholder"></textarea></view>
						<view class="action-row compact-actions">
							<u-button class="secondary-btn" :loading="sceneEnhancing" @click="enhanceScenePrompt">{{ sceneEnhancing ? '正在增强...' : '增强提示词' }}</u-button>
							<u-button class="primary-btn" type="primary" :loading="sceneLoading" @click="generateSceneAsset">{{ sceneLoading ? '正在生成...' : '生成场景资产' }}</u-button>
						</view>
					</view>

					<view class="section-card">
						<view class="section-head">
							<text class="section-title">资产库</text>
							<text class="info-chip">{{ filteredAssets.length }} 项</text>
						</view>
						<view class="segment-row no-top-gap">
							<text v-for="item in assetFilters" :key="item.value" class="segment-pill" :class="{ active: assetFilter === item.value }" @click="assetFilter = item.value">{{ item.label }}</text>
						</view>
						<view v-if="!filteredAssets.length" class="empty-block"><text>还没有资产，先生成角色图或场景图。</text></view>
						<view v-else class="list-stack top-gap">
							<view v-for="(asset, index) in filteredAssets" :key="asset.id || index" class="asset-card">
								<image v-if="asset.image_url" class="asset-image" :src="asset.image_url" mode="aspectFill"></image>
								<view class="list-card__body">
									<text class="list-card__title">{{ asset.name || `资产 ${index + 1}` }}</text>
									<text class="list-card__desc">{{ assetTypeLabel(asset) }}</text>
									<text v-if="asset.prompt" class="meta-hint">{{ asset.prompt }}</text>
									<u-button class="ghost-btn mini-btn top-gap" @click="deleteAsset(index, asset)">删除</u-button>
								</view>
							</view>
						</view>
					</view>
				</template>
			</view>

			<view v-show="activeCreateTab === 'director'" class="panel-stack">
				<view v-if="!hasProject" class="section-card empty-block">
					<text>先准备项目和剧本，再进入导演模块拆分镜头。</text>
					<u-button class="primary-btn mini-btn top-gap" type="primary" @click="handleCreateTabChange('project')">去项目模块</u-button>
				</view>
				<template v-else>
					<view class="section-card">
						<view class="section-head">
							<text class="section-title">镜头清单</text>
							<view class="action-row compact-actions">
								<u-button class="secondary-btn mini-btn" :loading="saving" @click="saveProject">保存镜头</u-button>
								<u-button class="ghost-btn mini-btn" @click="loadShotsFromScript">从剧本导入</u-button>
								<u-button class="ghost-btn mini-btn" @click="addShot">新增镜头</u-button>
							</view>
						</view>
						<view v-if="!shots.length" class="empty-block"><text>还没有镜头，先去剧本模块生成分镜。</text></view>
						<scroll-view v-else scroll-x class="shot-scroll top-gap">
							<view class="shot-strip">
								<view v-for="(shot, index) in shots" :key="`shot-${index}`" class="shot-pill" :class="{ active: selectedShotIndex === index }" @click="selectedShotIndex = index">
									<text class="list-card__title">{{ shot.title || `镜头 ${index + 1}` }}</text>
									<text class="meta-hint">{{ taskStatusText(shot) }}</text>
									<view v-if="taskState(shot) === 'processing'" class="inline-progress"><view class="inline-progress__bar" :style="{ width: `${taskProgressValue(shot)}%` }"></view></view>
								</view>
							</view>
						</scroll-view>
					</view>

					<view v-if="currentShot" class="section-card">
						<view class="section-head">
							<text class="section-title">镜头编辑</text>
							<text class="info-chip active">{{ taskStatusText(currentShot) }}</text>
						</view>
						<view class="form-grid two-col top-gap">
							<view class="form-group"><text class="field-label">镜头标题</text><input v-model="currentShot.title" class="field-input" type="text" placeholder="镜头标题" placeholder-class="field-placeholder" :adjust-position="false" /></view>
							<view class="form-group"><text class="field-label">时长</text><input v-model="currentShot.duration" class="field-input" type="text" placeholder="例如：5s" placeholder-class="field-placeholder" :adjust-position="false" /></view>
						</view>
						<view class="form-group"><text class="field-label">镜头概述</text><textarea v-model="currentShot.shotSummary" class="field-textarea" placeholder="描述景别、动作和镜头变化" placeholder-class="field-placeholder"></textarea></view>
						<view class="form-group"><text class="field-label">镜头提示词</text><textarea v-model="currentShot.prompt" class="field-textarea" placeholder="后续用于关键帧和视频生成" placeholder-class="field-placeholder"></textarea></view>
						<u-button class="secondary-btn" :loading="shotEnhancing" @click="enhanceCurrentShotPrompt">{{ shotEnhancing ? '正在增强...' : '增强镜头提示词' }}</u-button>
						<view class="form-grid two-col top-gap">
							<view class="form-group"><text class="field-label">起始帧描述</text><textarea v-model="currentShot.startFrame.description" class="field-textarea" placeholder="起始帧需要呈现什么" placeholder-class="field-placeholder"></textarea></view>
							<view class="form-group"><text class="field-label">结束帧描述</text><textarea v-model="currentShot.endFrame.description" class="field-textarea" placeholder="结束帧需要呈现什么" placeholder-class="field-placeholder"></textarea></view>
						</view>
						<view class="action-row compact-actions top-gap">
							<u-button class="secondary-btn" :loading="frameLoadingKey === 'startFrame'" @click="generateFrame('startFrame')">{{ frameLoadingKey === 'startFrame' ? '正在生成...' : '生成起始帧' }}</u-button>
							<u-button class="secondary-btn" :loading="frameLoadingKey === 'endFrame'" @click="generateFrame('endFrame')">{{ frameLoadingKey === 'endFrame' ? '正在生成...' : '生成结束帧' }}</u-button>
						</view>
						<view class="form-grid two-col top-gap">
							<image v-if="currentShot.startFrame.image_url" class="preview-media" :src="currentShot.startFrame.image_url" mode="aspectFill"></image>
							<view v-else class="empty-block small-empty"><text>起始帧还未生成</text></view>
							<image v-if="currentShot.endFrame.image_url" class="preview-media" :src="currentShot.endFrame.image_url" mode="aspectFill"></image>
							<view v-else class="empty-block small-empty"><text>结束帧还未生成</text></view>
						</view>
						<view v-if="taskState(currentShot) === 'processing'" class="progress-card top-gap"><view class="progress-track"><view class="progress-track__bar" :style="{ width: `${taskProgressValue(currentShot)}%` }"></view></view><text class="meta-hint">当前进度 {{ taskProgressValue(currentShot) }}%</text></view>
						<text v-if="currentShot.videoTask.message" class="meta-hint top-gap">{{ currentShot.videoTask.message }}</text>
						<view class="action-row compact-actions top-gap">
							<u-button class="primary-btn" type="primary" :loading="videoLoading" @click="generateCurrentVideo">{{ videoLoading ? '正在提交任务...' : '生成视频' }}</u-button>
							<u-button class="secondary-btn" @click="refreshCurrentTask">刷新任务</u-button>
							<u-button class="ghost-btn" @click="openExportSection">去导出管理</u-button>
						</view>
						<video v-if="currentShot.videoUrl" class="preview-video top-gap" :src="currentShot.videoUrl" controls playsinline></video>
					</view>
				</template>
			</view>
		</view>
	</view>
</template>

<script>
	import LoadingProgress from '../../components/LoadingProgress.vue'
	import UButton from '../../uni_modules/uview-ui/components/u-button/u-button.vue'
	import { createProject, getProject, listProjects } from '../../api/projects'
	import { parseScript } from '../../api/script'
	import { enhancePrompt, generateCharacter, generateScene } from '../../api/assets'
	import { generateVideo, queryVideoTask } from '../../api/workbench'
	import { ensureAuth } from '../../utils/navigation'
	import { applyProject, buildShotsFromScenes, createDefaultProjectState, createEmptyShot, ensureEpisodeState, listEpisodeOptions, normalizeAssetEntry } from '../../utils/project'
	import { loadCurrentProject, saveCurrentProjectState } from '../../utils/project-session'
	import { getCurrentProjectId, getProjectCache, getStudioView, saveProjectCache, saveStudioView, setCurrentProjectId } from '../../utils/storage'

	const CREATE_TABS = [
		{ key: 'project', label: '项目' },
		{ key: 'script', label: '剧本' },
		{ key: 'assets', label: '资产' },
		{ key: 'director', label: '导演' }
	]
	const PROVIDER_OPTIONS = [
		{ value: 'openai', label: '通用接口' },
		{ value: 'jimeng', label: '即梦接口' },
		{ value: 'grsai', label: '第三方接口' }
	]
	const DURATION_OPTIONS = [
		{ value: '30s', label: '30 秒预告' },
		{ value: '3min', label: '3 分钟短剧' },
		{ value: '5min', label: '5 分钟短剧' },
		{ value: 'custom', label: '自定义' }
	]
	const WARDROBE_OPTIONS = ['日常', '战斗', '礼服', '特写', '自定义']
	const ASSET_FILTERS = [{ value: 'all', label: '全部' }, { value: 'character', label: '角色' }, { value: 'scene', label: '场景' }]
	function clone(value, fallback) { try { return JSON.parse(JSON.stringify(value)) } catch (error) { return fallback } }
	function safeText(value) { return String(value || '').trim() }

	export default {
		components: { LoadingProgress, UButton },
		data() {
			return {
				...createDefaultProjectState(),
				initialized: false,
				createTabs: CREATE_TABS,
				providerOptions: PROVIDER_OPTIONS,
				durationOptions: DURATION_OPTIONS,
				wardrobeOptions: WARDROBE_OPTIONS,
				assetFilters: ASSET_FILTERS,
				activeCreateTab: 'project',
				projects: [],
				loading: false,
				creating: false,
				projectName: '',
				scriptTitle: '',
				selectedEpisode: 1,
				episodeChoices: Array.from({ length: 24 }, (_, index) => index + 1),
				activeProjectCache: null,
				progress: { visible: false, value: 0, label: '' },
				progressTimer: null,
				progressHideTimer: null,
				saving: false,
				parsing: false,
				scriptInput: '',
				scriptResult: null,
				rawResultText: '',
				targetDuration: '3min',
				customDuration: '',
				errorMessage: '',
				assetFilter: 'all',
				characterLoading: false,
				characterEnhancing: false,
				sceneLoading: false,
				sceneEnhancing: false,
				extractingCharacters: false,
				extractingScenes: false,
				recommendActionMessage: '',
				recommendMessageTimer: null,
				currentCharacter: { name: '', description: '', wardrobe: '日常', customWardrobe: '', prompt: '' },
				currentScene: { name: '', description: '', prompt: '' },
				selectedShotIndex: -1,
				shotEnhancing: false,
				frameLoadingKey: '',
				videoLoading: false,
				pollTimers: {}
			}
		},
		computed: {
			hasProject() { return Boolean(this.currentProjectId) },
			episodeChoiceIndex() { const choices = Array.isArray(this.episodeChoices) ? this.episodeChoices : []; const index = choices.findIndex((item) => item === this.selectedEpisode); return index >= 0 ? index : 0 },
			episodeOptions() { return listEpisodeOptions(this) },
			episodeIndex() { const index = this.episodeOptions.findIndex((item) => item === this.currentEpisodeNo); return index >= 0 ? index : 0 },
			providerLabels() { const options = Array.isArray(this.providerOptions) ? this.providerOptions : []; return options.map((item) => item.label) },
			providerIndex() { const options = Array.isArray(this.providerOptions) ? this.providerOptions : []; const index = options.findIndex((item) => item.value === this.videoProvider); return index >= 0 ? index : 0 },
			durationLabels() { const options = Array.isArray(this.durationOptions) ? this.durationOptions : []; return options.map((item) => item.label) },
			durationIndex() { const options = Array.isArray(this.durationOptions) ? this.durationOptions : []; const index = options.findIndex((item) => item.value === this.targetDuration); return index >= 0 ? index : 0 },
			sceneRows() { return this.scriptResult && Array.isArray(this.scriptResult.scenes) ? this.scriptResult.scenes : [] },
			storyPackage() { return this.scriptResult && this.scriptResult.story_package && typeof this.scriptResult.story_package === 'object' ? this.scriptResult.story_package : {} },
			hasScriptInput() { return Boolean(safeText(this.scriptInput) || safeText(this.lastScript && this.lastScript.input)) },
			characterAssets() { return (Array.isArray(this.assets) ? this.assets : []).filter((item) => safeText(item && item.asset_kind).toLowerCase() === 'character') },
			sceneAssets() { return (Array.isArray(this.assets) ? this.assets : []).filter((item) => safeText(item && item.asset_kind).toLowerCase() === 'scene') },
			characterCandidates() {
				let list = Array.isArray(this.storyPackage.character_bible) ? this.storyPackage.character_bible : []
				if (!list.length) { list = this.inferCharacterBibleFromScenes(this.sceneRows) }
				return list
					.map((item, index) => {
						const safe = item && typeof item === 'object' ? item : {}
						return {
							id: safeText(safe.name) || String(index + 1),
							name: safeText(safe.name) || `角色${index + 1}`,
							role: safeText(safe.role),
							goal: safeText(safe.goal),
							tension: safeText(safe.tension),
							voice: safeText(safe.voice),
							visualAnchor: safeText(safe.visual_anchor || safe.visualAnchor)
						}
					})
					.filter((item) => item.name)
			},
			recommendedSceneCandidates() {
				return this.sceneRows
					.map((scene, index) => {
						const sceneId = safeText(scene && scene.scene_id) || String(index + 1)
						const row = {
							sceneId,
							name: `场次 ${sceneId}`,
							description: safeText(scene && scene.description),
							shotSummary: safeText(scene && scene.shot_description),
							detailed: safeText(scene && scene.detailed_shot_description),
							duration: safeText(scene && scene.duration) || '5s'
						}
						const matchedAssets = this.sceneAssets.filter((asset) => this.isSceneCandidateMatched(row, asset))
						return {
							...row,
							generated: matchedAssets.length > 0,
							matchedAssets: matchedAssets.map((asset) => safeText(asset && asset.name)).filter(Boolean)
						}
					})
					.filter((item) => item.description || item.shotSummary || item.detailed)
			},
			recommendedCharacterCandidates() {
				return this.characterCandidates.map((item) => {
					const matchedAssets = this.characterAssets.filter((asset) => this.isCharacterCandidateMatched(item, asset))
					return {
						...item,
						generated: matchedAssets.length > 0,
						matchedAssets: matchedAssets.map((asset) => safeText(asset && asset.name)).filter(Boolean)
					}
				})
			},
			hasRecommendationCandidates() { return this.recommendedSceneCandidates.length > 0 || this.recommendedCharacterCandidates.length > 0 },
			wardrobeIndex() { const options = Array.isArray(this.wardrobeOptions) ? this.wardrobeOptions : []; const index = options.findIndex((item) => item === this.currentCharacter.wardrobe); return index >= 0 ? index : 0 },
			filteredAssets() { return this.assetFilter === 'all' ? this.assets : this.assets.filter((item) => safeText(item && item.asset_kind).toLowerCase() === this.assetFilter) },
			currentShot() { return this.selectedShotIndex >= 0 && this.selectedShotIndex < this.shots.length ? this.shots[this.selectedShotIndex] : null }
		},
		onLoad(options) { this.restoreStudioView(); this.applyLaunchState(options) },
		onShow() {
			if (!ensureAuth()) { return }
			this.activeProjectCache = getProjectCache()
			this.restoreStudioView()
			if (!this.initialized) { this.initializePage() }
		},
		onPullDownRefresh() { if (!ensureAuth()) { uni.stopPullDownRefresh(); return } this.refreshCurrentView() },
		onUnload() {
			this.clearProgressTimer()
			if (this.recommendMessageTimer) { clearTimeout(this.recommendMessageTimer); this.recommendMessageTimer = null }
			Object.keys(this.pollTimers || {}).forEach((key) => this.clearPolling(key))
		},
		methods: {
			showToast(message) { uni.showToast({ title: safeText(message) || '操作失败', icon: 'none' }) },
			clearProgressTimer() { if (this.progressTimer) { clearInterval(this.progressTimer); this.progressTimer = null } if (this.progressHideTimer) { clearTimeout(this.progressHideTimer); this.progressHideTimer = null } },
			startProgress(label) { this.clearProgressTimer(); this.progress = { visible: true, value: 14, label: safeText(label) || '正在处理' }; this.progressTimer = setInterval(() => { const currentValue = Number(this.progress.value || 0); const delta = currentValue < 60 ? 9 : currentValue < 84 ? 4 : 0; this.progress.value = Math.min(currentValue + delta, 90) }, 220) },
			finishProgress(label) { this.clearProgressTimer(); this.progress.label = safeText(label) || this.progress.label || '已完成'; this.progress.value = 100; this.progressHideTimer = setTimeout(() => { this.progress.visible = false; this.progress.value = 0 }, 320) },
			async runTask(label, handler, options = {}) { this.startProgress(label); try { const result = await handler(); this.finishProgress(options.successText || '已完成'); return result } catch (error) { this.finishProgress(safeText(error && error.message) || options.failureText || '操作失败'); throw error } },
			persistStudioView() { saveStudioView({ mainTab: 'create', createTab: this.activeCreateTab }) },
			restoreStudioView() { const view = getStudioView(); if (!view || typeof view !== 'object') { return } const createTab = safeText(view.createTab).toLowerCase(); if (['project', 'script', 'assets', 'director'].includes(createTab)) { this.activeCreateTab = createTab } },
			applyLaunchState(options = {}) { const panel = safeText(options.panel || options.tab).toLowerCase(); if (['project', 'script', 'assets', 'director'].includes(panel)) { this.activeCreateTab = panel; this.persistStudioView() } },
			async initializePage() { try { await this.runTask('正在同步工作台', async () => { await this.fetchProjects(); if (getCurrentProjectId()) { await this.fetchCurrentProject() } }, { successText: '工作台已就绪' }); this.initialized = true } catch (error) { this.showToast(error.message || '初始化失败') } finally { uni.stopPullDownRefresh() } },
			async refreshCurrentView() { try { await this.runTask('正在刷新工作台', async () => { await this.fetchProjects(); if (this.hasProject || getCurrentProjectId()) { await this.fetchCurrentProject(true) } }, { successText: '工作台已刷新' }) } catch (error) { this.showToast(error.message || '刷新失败') } finally { uni.stopPullDownRefresh() } },
			handleCreateTabChange(key) { if (!key) { return } this.activeCreateTab = key; this.persistStudioView() },
			providerText(value) { const target = this.providerOptions.find((item) => item.value === safeText(value).toLowerCase()); return target ? target.label : '通用接口' },
			formatProjectUpdatedAt(value) {
				const text = safeText(value)
				if (!text) { return '更新时间未知' }
				const normalized = text.replace('T', ' ').replace('Z', '')
				return `更新于 ${normalized}`
			},
			assetCount(project) { return Array.isArray(project && project.assets) ? project.assets.length : 0 },
			shotCount(project) { return Array.isArray(project && project.shots) ? project.shots.length : 0 },
			upsertProjectSummary(project) { if (!project || !project.id) { return } const summary = clone(project, {}); const list = Array.isArray(this.projects) ? [...this.projects] : []; const index = list.findIndex((item) => String(item && item.id) === String(summary.id)); if (index >= 0) { list.splice(index, 1, { ...list[index], ...summary }) } else { list.unshift(summary) } this.projects = list },
			resetAssetForms() { this.currentCharacter = { name: '', description: '', wardrobe: '日常', customWardrobe: '', prompt: '' }; this.currentScene = { name: '', description: '', prompt: '' } },
			normalizeShot(shot, index = 0) { const safeShot = shot && typeof shot === 'object' ? clone(shot, {}) : {}; const defaults = createEmptyShot(index + 1); return { ...defaults, ...safeShot, title: safeText(safeShot.title) || `镜头 ${index + 1}`, duration: safeText(safeShot.duration) || '5s', startFrame: { ...defaults.startFrame, ...(safeShot.startFrame || {}) }, endFrame: { ...defaults.endFrame, ...(safeShot.endFrame || {}) }, videoTask: { ...defaults.videoTask, ...(safeShot.videoTask || {}) } } },
			hydrateProject(project) { const next = applyProject(project); next.shots = (next.shots || []).map((shot, index) => this.normalizeShot(shot, index)); Object.assign(this, next); this.scriptInput = safeText(next.lastScript && next.lastScript.input); this.scriptResult = next.lastScript && next.lastScript.result ? next.lastScript.result : null; this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : ''; this.applyDuration((next.lastScript && next.lastScript.duration) || '3min'); this.selectedShotIndex = next.shots.length ? 0 : -1; this.activeProjectCache = clone(project, {}); this.errorMessage = ''; this.resetAssetForms() },
			async fetchProjects() { const response = await listProjects(); this.projects = Array.isArray(response) ? response : []; this.activeProjectCache = getProjectCache(); return this.projects },
			async loadProjects(silent = false) { this.loading = true; try { if (silent) { await this.fetchProjects() } else { await this.runTask('正在同步项目列表', () => this.fetchProjects(), { successText: '项目列表已更新' }) } } catch (error) { this.showToast(error.message || '加载项目失败') } finally { this.loading = false; uni.stopPullDownRefresh() } },
			async fetchCurrentProject(forceRemote = false) { const project = await loadCurrentProject({ forceRemote }); if (project) { this.hydrateProject(project) } return project },
			async loadProject(forceRemote = false, silent = false) { if (!this.hasProject && !getCurrentProjectId()) { return } try { if (silent) { await this.fetchCurrentProject(forceRemote) } else { await this.runTask('正在同步当前项目', () => this.fetchCurrentProject(forceRemote), { successText: '项目数据已更新' }) } } catch (error) { this.showToast(error.message || '加载项目失败') } finally { uni.stopPullDownRefresh() } },
			activateProject(project, panel = 'project') { if (!project || !project.id) { return } saveProjectCache(project); setCurrentProjectId(project.id); this.hydrateProject(project); this.upsertProjectSummary(project); this.activeCreateTab = panel; this.persistStudioView() },
			async createNewProject() { this.creating = true; try { const detail = await this.runTask('正在创建项目', async () => { const created = await createProject({ name: safeText(this.projectName) || `项目 ${this.projects.length + 1}`, script_title: safeText(this.scriptTitle), episode_no: this.selectedEpisode }); return getProject(created.id) }, { successText: '项目已创建' }); this.projectName = ''; this.scriptTitle = ''; this.selectedEpisode = 1; this.activateProject(detail, 'script') } catch (error) { this.showToast(error.message || '创建项目失败') } finally { this.creating = false } },
			async openProject(project, panel = 'script') { if (!project || !project.id) { return } try { const detail = await this.runTask('正在打开项目', () => getProject(project.id), { successText: '项目已打开' }); this.activateProject(detail, panel) } catch (error) { this.showToast(error.message || '打开项目失败') } },
			openCurrentProject() { if (this.activeProjectCache && this.activeProjectCache.id) { this.openProject(this.activeProjectCache, 'script'); return } this.handleCreateTabChange('project') },
			handleEpisodeChange(event) { const next = this.episodeChoices[Number(event.detail.value || 0)] || 1; this.selectedEpisode = Number(next) || 1 },
			persistCurrentEpisodeState() { const key = ensureEpisodeState(this.episodeScripts, this.episodeShots, this.currentEpisodeNo); this.lastScript = { input: safeText(this.scriptInput), duration: this.resolveDurationText() || '3min', result: this.scriptResult || null }; this.episodeScripts[key] = { script: clone(this.lastScript, { ...this.lastScript }), history: clone(this.scriptHistory, []) }; this.episodeShots[key] = clone(this.shots, []) },
			restoreCurrentEpisodeState() { const key = ensureEpisodeState(this.episodeScripts, this.episodeShots, this.currentEpisodeNo); const episodeState = this.episodeScripts[key]; this.lastScript = { input: safeText(episodeState.script && episodeState.script.input), duration: safeText(episodeState.script && episodeState.script.duration) || '3min', result: clone(episodeState.script && episodeState.script.result, null) }; this.scriptHistory = clone(episodeState.history, []); this.shots = clone(this.episodeShots[key], []).map((shot, index) => this.normalizeShot(shot, index)); this.scriptInput = this.lastScript.input; this.scriptResult = this.lastScript.result; this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : ''; this.applyDuration(this.lastScript.duration); this.selectedShotIndex = this.shots.length ? 0 : -1 },
			handleCurrentEpisodeChange(event) { this.persistCurrentEpisodeState(); this.currentEpisodeNo = this.episodeOptions[Number(event.detail.value || 0)] || 1; this.restoreCurrentEpisodeState() },
			handleProviderChange(event) { this.videoProvider = this.providerOptions[Number(event.detail.value || 0)]?.value || 'openai' },
			handleDurationChange(event) { this.targetDuration = this.durationOptions[Number(event.detail.value || 0)]?.value || '3min' },
			addEpisode() { this.persistCurrentEpisodeState(); const next = (this.episodeOptions[this.episodeOptions.length - 1] || 1) + 1; ensureEpisodeState(this.episodeScripts, this.episodeShots, next); this.currentEpisodeNo = next; this.restoreCurrentEpisodeState(); this.showToast(`已切换到第 ${next} 集`) },
			applyDuration(value) { if (['30s', '3min', '5min'].includes(value)) { this.targetDuration = value; this.customDuration = ''; return } this.targetDuration = 'custom'; this.customDuration = safeText(value) },
			resolveDurationText() { return this.targetDuration === 'custom' ? safeText(this.customDuration) : this.targetDuration },
			async persistProjectState(silent = false) { const saveAction = async () => { this.persistCurrentEpisodeState(); const updated = await saveCurrentProjectState(this); const merged = { ...(this.activeProjectCache || {}), ...updated, id: updated.id || this.currentProjectId }; saveProjectCache(merged); this.activeProjectCache = merged; this.upsertProjectSummary(merged); return merged }; if (silent) { return saveAction() } this.saving = true; try { return await this.runTask('正在保存项目', saveAction, { successText: '项目已保存' }) } finally { this.saving = false } },
			async saveProject() { try { await this.persistProjectState(false) } catch (error) { this.showToast(error.message || '保存失败') } },
			async parseCurrentScript() { const script = safeText(this.scriptInput); const duration = this.resolveDurationText(); if (!script) { this.errorMessage = '请先输入剧本内容'; return } if (!duration) { this.errorMessage = '请先设置目标时长'; return } this.parsing = true; this.errorMessage = ''; try { const result = await this.runTask('正在生成分镜脚本', () => parseScript({ script, duration }), { successText: '分镜脚本已生成' }); this.scriptResult = result; this.rawResultText = JSON.stringify(result, null, 2); this.lastScript = { input: script, duration, result }; await this.persistProjectState(true) } catch (error) { this.errorMessage = error.message || '生成分镜脚本失败' } finally { this.parsing = false } },
			applyEditedResult() { try { const parsed = JSON.parse(this.rawResultText || '{}'); this.scriptResult = parsed; this.lastScript = { input: safeText(this.scriptInput), duration: this.resolveDurationText() || '3min', result: parsed }; this.persistCurrentEpisodeState(); this.errorMessage = ''; this.showToast('结果已应用') } catch (error) { this.errorMessage = 'JSON 格式有误，请检查后再试' } },
			resetEditedResult() { this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : '' },
			async syncScenesToShots() { if (!this.sceneRows.length) { return } this.shots = buildShotsFromScenes(this.sceneRows).map((shot, index) => this.normalizeShot(shot, index)); this.selectedShotIndex = this.shots.length ? 0 : -1; await this.persistProjectState(true); this.activeCreateTab = 'director'; this.persistStudioView(); this.showToast('已同步到导演模块') },
			setRecommendActionMessage(message) {
				this.recommendActionMessage = safeText(message)
				if (this.recommendMessageTimer) { clearTimeout(this.recommendMessageTimer); this.recommendMessageTimer = null }
				if (!this.recommendActionMessage) { return }
				this.recommendMessageTimer = setTimeout(() => { this.recommendActionMessage = ''; this.recommendMessageTimer = null }, 2600)
			},
			normalizeToken(value) { return safeText(value).toLowerCase().replace(/[\s\-_.:,;'"`~!@#$%^&*(){}\[\]<>?/\\|，。！？、；：“”‘’（）【】《》]/g, '') },
			buildAssetSearchText(asset) {
				const safeAsset = asset && typeof asset === 'object' ? asset : {}
				return [safeAsset.name, safeAsset.prompt, safeAsset.source_description, safeAsset.type, safeAsset.asset_kind, safeAsset.wardrobe].map((item) => this.normalizeToken(item)).join(' ')
			},
			isCharacterCandidateMatched(candidate, asset) {
				const text = this.buildAssetSearchText(asset)
				if (!text) { return false }
				const safeCandidate = candidate && typeof candidate === 'object' ? candidate : {}
				const tokens = [this.normalizeToken(safeCandidate.name), this.normalizeToken(safeCandidate.role), this.normalizeToken(String(safeCandidate.visualAnchor || '').slice(0, 10))].filter((token) => token && token.length >= 2)
				return tokens.some((token) => text.includes(token))
			},
			isSceneCandidateMatched(candidate, asset) {
				const text = this.buildAssetSearchText(asset)
				if (!text) { return false }
				const safeCandidate = candidate && typeof candidate === 'object' ? candidate : {}
				const sceneName = safeText(safeCandidate.name).replace(/^场次\s*\d+\s*/, '')
				const tokens = [this.normalizeToken(sceneName), this.normalizeToken(String(safeCandidate.description || '').slice(0, 12)), this.normalizeToken(String(safeCandidate.shotSummary || '').slice(0, 12))].filter((token) => token && token.length >= 2)
				return tokens.some((token) => text.includes(token))
			},
			inferCharacterBibleFromScenes(scenes) {
				const list = []
				const seen = new Set()
				const pushName = (rawName) => {
					const name = safeText(rawName)
					if (!name || name.length > 16) { return }
					const key = name.toLowerCase()
					if (seen.has(key)) { return }
					seen.add(key)
					list.push({ name, role: '待补充', goal: '', tension: '', voice: '', visual_anchor: '' })
				}
				;(Array.isArray(scenes) ? scenes : []).forEach((scene) => {
					if (!scene || typeof scene !== 'object') { return }
					;['dialogue_details', 'dialogue_beats'].forEach((key) => {
						const beats = scene[key]
						if (!Array.isArray(beats)) { return }
						beats.forEach((beat) => { if (beat && typeof beat === 'object') { pushName(beat.speaker || beat.role || beat.character) } })
					})
					const dialogueText = safeText(scene.dialogue)
					if (!dialogueText) { return }
					dialogueText.split('\n').forEach((line) => {
						const match = line.match(/^\s*([^:：\s]{1,12})\s*[:：]/)
						if (match) { pushName(match[1]) }
					})
				})
				return list
			},
			sanitizeCharacterBible(items) {
				const seen = new Set()
				return (Array.isArray(items) ? items : [])
					.map((item) => (item && typeof item === 'object' ? item : {}))
					.map((item) => ({ ...item, name: safeText(item.name) }))
					.filter((item) => {
						if (!item.name) { return false }
						const key = item.name.toLowerCase()
						if (seen.has(key)) { return false }
						seen.add(key)
						return true
					})
			},
			buildMergedResultFromAi(aiResult) {
				const currentResult = this.scriptResult && typeof this.scriptResult === 'object' ? clone(this.scriptResult, {}) : {}
				const incomingScenes = Array.isArray(aiResult && aiResult.scenes) ? aiResult.scenes : []
				const incomingStoryPackage = aiResult && aiResult.story_package && typeof aiResult.story_package === 'object' ? aiResult.story_package : {}
				const currentStoryPackage = currentResult.story_package && typeof currentResult.story_package === 'object' ? currentResult.story_package : {}
				const incomingCharacters = this.sanitizeCharacterBible(incomingStoryPackage.character_bible)
				const currentCharacters = this.sanitizeCharacterBible(currentStoryPackage.character_bible)
				return {
					...currentResult,
					...clone(aiResult, {}),
					story_package: {
						...currentStoryPackage,
						...incomingStoryPackage,
						character_bible: incomingCharacters.length ? incomingCharacters : currentCharacters
					},
					scenes: incomingScenes.length ? incomingScenes : (Array.isArray(currentResult.scenes) ? currentResult.scenes : [])
				}
			},
			fillSceneFromCandidate(candidate) {
				const safeCandidate = candidate && typeof candidate === 'object' ? candidate : {}
				const parts = [safeText(safeCandidate.description), safeText(safeCandidate.shotSummary), safeText(safeCandidate.detailed)].filter(Boolean)
				this.currentScene.name = safeText(safeCandidate.name)
				this.currentScene.description = [...new Set(parts)].join('；')
				this.currentScene.prompt = ''
				this.setRecommendActionMessage(`已导入场景：${this.currentScene.name || '未命名场景'}`)
			},
			fillCharacterFromCandidate(candidate) {
				const safeCandidate = candidate && typeof candidate === 'object' ? candidate : {}
				const parts = [
					safeText(safeCandidate.role) ? `角色定位：${safeText(safeCandidate.role)}` : '',
					safeText(safeCandidate.goal) ? `目标：${safeText(safeCandidate.goal)}` : '',
					safeText(safeCandidate.tension) ? `张力：${safeText(safeCandidate.tension)}` : '',
					safeText(safeCandidate.voice) ? `声音气质：${safeText(safeCandidate.voice)}` : '',
					safeText(safeCandidate.visualAnchor) ? `视觉锚点：${safeText(safeCandidate.visualAnchor)}` : ''
				].filter(Boolean)
				this.currentCharacter.name = safeText(safeCandidate.name)
				this.currentCharacter.description = parts.join('；')
				this.currentCharacter.wardrobe = '日常'
				this.currentCharacter.customWardrobe = ''
				this.currentCharacter.prompt = ''
			},
			importCharacterFromCandidate(candidate, byLongPress = false) {
				this.fillCharacterFromCandidate(candidate)
				const name = safeText(candidate && candidate.name) || '未命名角色'
				this.setRecommendActionMessage(byLongPress ? `已长按导入角色：${name}` : `已导入角色：${name}`)
			},
			async runAiExtraction(trigger = 'all') {
				const script = safeText(this.scriptInput) || safeText(this.lastScript && this.lastScript.input)
				const duration = this.resolveDurationText() || safeText(this.lastScript && this.lastScript.duration) || '3min'
				if (!script) { this.showToast('请先在剧本模块输入并保存剧本'); return }
				if (trigger === 'character') { this.extractingCharacters = true } else { this.extractingScenes = true }
				try {
					const aiResult = await this.runTask('正在提取角色与场景推荐', () => parseScript({ script, duration }), { successText: '提取完成' })
					const merged = this.buildMergedResultFromAi(aiResult)
					const scenes = Array.isArray(merged.scenes) ? merged.scenes : []
					const characters = this.sanitizeCharacterBible(merged.story_package && merged.story_package.character_bible)
					if (!scenes.length && !characters.length) { this.showToast('未提取到场景或角色，请补充剧本后重试'); return }
					this.scriptResult = merged
					this.rawResultText = JSON.stringify(merged, null, 2)
					this.lastScript = { input: script, duration, result: merged }
					await this.persistProjectState(true)
					this.setRecommendActionMessage(`提取完成：场景 ${scenes.length} 个，角色 ${characters.length} 个`)
				} catch (error) {
					this.showToast(error.message || '提取失败')
				} finally {
					this.extractingCharacters = false
					this.extractingScenes = false
				}
			},
			async extractCharactersByAi() { await this.runAiExtraction('character') },
			async extractScenesByAi() { await this.runAiExtraction('scene') },
			handleWardrobeChange(event) { this.currentCharacter.wardrobe = this.wardrobeOptions[Number(event.detail.value || 0)] || '日常' },
			assetTypeLabel(asset) { return safeText(asset && asset.asset_kind).toLowerCase() === 'character' ? `角色${safeText(asset.wardrobe) ? ` · ${safeText(asset.wardrobe)}` : ''}` : '场景' },
			normalizedWardrobe() { return this.currentCharacter.wardrobe === '自定义' ? safeText(this.currentCharacter.customWardrobe) : safeText(this.currentCharacter.wardrobe) },
			buildCharacterBasePrompt() { return [safeText(this.currentCharacter.name) ? `角色：${safeText(this.currentCharacter.name)}` : '', safeText(this.currentCharacter.description), this.normalizedWardrobe() ? `造型：${this.normalizedWardrobe()}` : '', '中国风动画角色设定图，单幅完整构图，人物五官、发型、服装和气质保持稳定统一'].filter(Boolean).join('；') },
			buildSceneBasePrompt() { return [safeText(this.currentScene.name) ? `场景：${safeText(this.currentScene.name)}` : '', safeText(this.currentScene.description), '中国风动画场景母版图，单幅完整构图，空间关系清晰，禁止拼贴、分屏、文字和水印'].filter(Boolean).join('；') },
			async requestEnhance(rawPrompt, context) { const response = await enhancePrompt({ prompt: rawPrompt, context }); return safeText(response && response.enhanced_prompt) || safeText(rawPrompt) },
			async enhanceCharacterPrompt() { if (!safeText(this.currentCharacter.name) || !safeText(this.currentCharacter.description)) { this.showToast('请先填写角色名称和描述'); return } this.characterEnhancing = true; try { const prompt = safeText(this.currentCharacter.prompt) || this.buildCharacterBasePrompt(); this.currentCharacter.prompt = await this.runTask('正在增强角色提示词', () => this.requestEnhance(prompt, { prompt_type: 'character_asset', asset_type: 'character', name: this.currentCharacter.name, subject_name: this.currentCharacter.name, wardrobe: this.normalizedWardrobe() }), { successText: '角色提示词已准备' }) } catch (error) { this.showToast(error.message || '增强提示词失败') } finally { this.characterEnhancing = false } },
			async enhanceScenePrompt() { if (!safeText(this.currentScene.name) || !safeText(this.currentScene.description)) { this.showToast('请先填写场景名称和描述'); return } this.sceneEnhancing = true; try { const prompt = safeText(this.currentScene.prompt) || this.buildSceneBasePrompt(); this.currentScene.prompt = await this.runTask('正在增强场景提示词', () => this.requestEnhance(prompt, { prompt_type: 'scene_asset', asset_type: 'scene', name: this.currentScene.name, subject_name: this.currentScene.name }), { successText: '场景提示词已准备' }) } catch (error) { this.showToast(error.message || '增强提示词失败') } finally { this.sceneEnhancing = false } },
			async generateCharacterAsset() { if (!safeText(this.currentCharacter.name) || !safeText(this.currentCharacter.description)) { this.showToast('请先填写角色名称和描述'); return } this.characterLoading = true; try { const wardrobe = this.normalizedWardrobe(); const prompt = safeText(this.currentCharacter.prompt) || this.buildCharacterBasePrompt(); const response = await this.runTask('正在生成角色资产', () => generateCharacter({ description: prompt }), { successText: '角色资产已生成' }); this.assets = [normalizeAssetEntry({ ...clone(response, {}), name: safeText(this.currentCharacter.name), type: '角色', asset_kind: 'character', wardrobe, prompt, source_description: safeText(this.currentCharacter.description) }, this.assets.length), ...this.assets]; this.currentCharacter.prompt = safeText(response && response.prompt) || prompt; await this.persistProjectState(true) } catch (error) { this.showToast(error.message || '生成角色资产失败') } finally { this.characterLoading = false } },
			async generateSceneAsset() { if (!safeText(this.currentScene.name) || !safeText(this.currentScene.description)) { this.showToast('请先填写场景名称和描述'); return } this.sceneLoading = true; try { const prompt = safeText(this.currentScene.prompt) || this.buildSceneBasePrompt(); const response = await this.runTask('正在生成场景资产', () => generateScene({ description: prompt }), { successText: '场景资产已生成' }); this.assets = [normalizeAssetEntry({ ...clone(response, {}), name: safeText(this.currentScene.name), type: '场景', asset_kind: 'scene', prompt, source_description: safeText(this.currentScene.description) }, this.assets.length), ...this.assets]; this.currentScene.prompt = safeText(response && response.prompt) || prompt; await this.persistProjectState(true) } catch (error) { this.showToast(error.message || '生成场景资产失败') } finally { this.sceneLoading = false } },
			deleteAsset(index, asset) { uni.showModal({ title: '删除资产', content: `确认删除“${safeText(asset && asset.name) || '未命名资产'}”吗？`, success: async (result) => { if (!result.confirm) { return } const realIndex = this.assets.findIndex((item) => String(item && item.id) === String(asset && asset.id)); this.assets.splice(realIndex >= 0 ? realIndex : index, 1); await this.persistProjectState(true) } }) },
			addShot() { this.shots.push(this.normalizeShot(createEmptyShot(this.shots.length + 1), this.shots.length)); this.selectedShotIndex = this.shots.length - 1 },
			async loadShotsFromScript() { if (!this.sceneRows.length) { this.showToast('当前还没有可导入的分镜结果'); return } this.shots = buildShotsFromScenes(this.sceneRows).map((shot, index) => this.normalizeShot(shot, index)); this.selectedShotIndex = this.shots.length ? 0 : -1; await this.persistProjectState(true); this.showToast('镜头已导入导演模块') },
			buildShotPrompt(shot) { return shot ? [safeText(shot.prompt), safeText(shot.shotSummary), safeText(shot.detailedShotDescription)].filter(Boolean).join('；') : '' },
			async enhanceCurrentShotPrompt() { if (!this.currentShot) { return } this.shotEnhancing = true; try { const basePrompt = this.buildShotPrompt(this.currentShot); const response = await this.runTask('正在增强镜头提示词', () => enhancePrompt({ prompt: basePrompt, context: { prompt_type: 'shot_plan', shot_summary: this.currentShot.shotSummary } }), { successText: '镜头提示词已准备' }); this.currentShot.prompt = safeText(response && response.enhanced_prompt) || basePrompt } catch (error) { this.showToast(error.message || '增强提示词失败') } finally { this.shotEnhancing = false } },
			async generateFrame(frameKey) { if (!this.currentShot) { return } this.frameLoadingKey = frameKey; try { const frame = this.currentShot[frameKey]; const description = safeText(frame.description) || this.buildShotPrompt(this.currentShot); const referenceImages = []; let preferImg2img = false; if (frameKey === 'endFrame' && this.currentShot.startFrame && this.currentShot.startFrame.image_url) { referenceImages.push(this.currentShot.startFrame.image_url); preferImg2img = true } const response = await this.runTask(frameKey === 'startFrame' ? '正在生成起始帧' : '正在生成结束帧', () => generateScene({ description, reference_images: referenceImages, prefer_img2img: preferImg2img, context: { prompt_type: 'frame', frame_key: frameKey } }), { successText: frameKey === 'startFrame' ? '起始帧已生成' : '结束帧已生成' }); frame.description = description; frame.enhanced_prompt = safeText(response && response.prompt) || description; frame.image_url = safeText(response && response.image_url); await this.persistProjectState(true) } catch (error) { this.showToast(error.message || '生成关键帧失败') } finally { this.frameLoadingKey = '' } },
			taskState(shot) { const status = safeText(shot && shot.videoTask && shot.videoTask.status).toLowerCase(); if (safeText(shot && shot.videoUrl) || status === 'succeeded') { return 'succeeded' } if (['submitting', 'submitted', 'processing', 'running', 'pending'].includes(status)) { return 'processing' } if (['failed', 'error'].includes(status)) { return 'failed' } return 'idle' },
			taskStatusText(shot) { const state = this.taskState(shot); return state === 'succeeded' ? '视频已就绪' : state === 'processing' ? '视频生成中' : state === 'failed' ? '视频生成失败' : '待生成' },
			taskProgressValue(shot) { const rawValue = Number(shot && shot.videoTask && shot.videoTask.progress || 0); const state = this.taskState(shot); if (state === 'succeeded') { return 100 } if (state === 'processing') { return rawValue > 0 ? Math.min(Math.round(rawValue), 99) : 35 } return rawValue > 0 ? Math.min(Math.round(rawValue), 100) : 0 },
			applyTaskUpdate(index, payload = {}) { const shot = this.shots[index]; if (!shot) { return } shot.videoTask = { ...shot.videoTask, taskId: safeText(payload.task_id || payload.taskId || shot.videoTask.taskId), status: safeText(payload.status || shot.videoTask.status), message: safeText(payload.message || shot.videoTask.message), progress: Number(payload.progress || shot.videoTask.progress || 0), provider: safeText(payload.provider || shot.videoTask.provider || this.videoProvider), reqKey: safeText(payload.req_key || payload.reqKey || shot.videoTask.reqKey), queryUrl: safeText(payload.query_url || payload.queryUrl || shot.videoTask.queryUrl), queryMethod: safeText(payload.query_method || payload.queryMethod || shot.videoTask.queryMethod) }; const nextUrl = safeText(payload.video_url || payload.videoUrl); if (nextUrl) { shot.videoUrl = nextUrl } },
			clearPolling(index) { if (this.pollTimers[index]) { clearTimeout(this.pollTimers[index]); delete this.pollTimers[index] } },
			startPolling(index) { this.clearPolling(index); const tick = async () => { const shot = this.shots[index]; if (!shot || !shot.videoTask || !shot.videoTask.taskId) { return } try { const response = await queryVideoTask(shot.videoTask.taskId, { provider: shot.videoTask.provider || this.videoProvider, req_key: shot.videoTask.reqKey || '', query_url: shot.videoTask.queryUrl || '', query_method: shot.videoTask.queryMethod || '' }); this.applyTaskUpdate(index, response); await this.persistProjectState(true); if (['succeeded', 'failed'].includes(safeText(response.status).toLowerCase()) || safeText(response.video_url || response.videoUrl)) { this.clearPolling(index); return } this.pollTimers[index] = setTimeout(tick, 5000) } catch (error) { this.applyTaskUpdate(index, { status: 'failed', message: error.message || '任务查询失败' }); await this.persistProjectState(true); this.clearPolling(index) } }; this.pollTimers[index] = setTimeout(tick, 5000) },
			async generateCurrentVideo() { if (!this.currentShot || !safeText(this.currentShot.startFrame && this.currentShot.startFrame.image_url)) { this.showToast('请先生成起始帧'); return } this.videoLoading = true; try { const response = await this.runTask('正在提交视频任务', () => generateVideo({ start_frame: this.currentShot.startFrame, end_frame: this.currentShot.endFrame, mode: 'keyframe-interpolation', context: { video_provider: this.videoProvider, shot_title: this.currentShot.title, shot_prompt: this.buildShotPrompt(this.currentShot) }, provider: this.videoProvider }), { successText: '视频任务已提交' }); this.applyTaskUpdate(this.selectedShotIndex, response); await this.persistProjectState(true); if (safeText(response.task_id || response.taskId) && !safeText(response.video_url || response.videoUrl)) { this.startPolling(this.selectedShotIndex) } } catch (error) { this.showToast(error.message || '提交视频任务失败') } finally { this.videoLoading = false } },
			async refreshCurrentTask() { if (!this.currentShot || !safeText(this.currentShot.videoTask && this.currentShot.videoTask.taskId)) { this.showToast('当前镜头还没有任务 ID'); return } try { const response = await this.runTask('正在刷新视频任务', () => queryVideoTask(this.currentShot.videoTask.taskId, { provider: this.currentShot.videoTask.provider || this.videoProvider, req_key: this.currentShot.videoTask.reqKey || '', query_url: this.currentShot.videoTask.queryUrl || '', query_method: this.currentShot.videoTask.queryMethod || '' }), { successText: '任务状态已更新' }); this.applyTaskUpdate(this.selectedShotIndex, response); await this.persistProjectState(true) } catch (error) { this.showToast(error.message || '刷新任务失败') } },
			openExportSection() { uni.switchTab({ url: '/views/export/index' }) }
		}
	}
</script>

<style scoped lang="scss">
	.studio-page { position: relative; min-height: 100vh; background: linear-gradient(180deg, #f6f1e8 0%, #f5f4ed 38%, #edf1ea 100%); color: #2a342f; }
	.studio-page__bg { position: fixed; inset: 0; background: radial-gradient(circle at top left, rgba(222, 226, 204, 0.88), transparent 38%), radial-gradient(circle at top right, rgba(210, 223, 211, 0.7), transparent 34%), radial-gradient(circle at bottom, rgba(233, 238, 226, 0.92), transparent 46%); pointer-events: none; }
	.studio-shell { position: relative; z-index: 1; padding-bottom: 48rpx; }
	.section-card, .summary-card, .list-card, .focus-card, .asset-card, .shot-pill, .message-card, .progress-card { background: rgba(255, 251, 246, 0.92); border: 1rpx solid rgba(117, 131, 112, 0.12); border-radius: 30rpx; box-shadow: 0 24rpx 80rpx rgba(106, 110, 89, 0.08); }
	.section-card, .summary-card, .focus-card { padding: 24rpx; }
	.section-head { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
	.section-title, .list-card__title, .focus-title, .meta-value { display: block; color: #2b3631; font-weight: 700; }
	.section-title { font-size: 32rpx; }
	.section-subtitle, .meta-hint, .list-card__desc { display: block; font-size: 24rpx; line-height: 1.7; color: #6d766d; }
	.meta-label { display: block; font-size: 22rpx; color: #7b8579; }
	.meta-value { margin-top: 8rpx; font-size: 34rpx; }
	.summary-grid, .form-grid { display: grid; gap: 16rpx; }
	.summary-grid, .two-col { grid-template-columns: repeat(2, minmax(0, 1fr)); }
	.three-col { grid-template-columns: repeat(3, minmax(0, 1fr)); }
	.segment-row, .chip-row, .action-row { display: flex; flex-wrap: wrap; gap: 14rpx; }
	.no-top-gap { margin-top: 0; }
	.segment-pill, .info-chip { display: inline-flex; align-items: center; justify-content: center; min-height: 60rpx; padding: 0 22rpx; border-radius: 999rpx; font-size: 23rpx; color: #657062; background: rgba(242, 245, 237, 0.94); border: 1rpx solid rgba(117, 131, 112, 0.1); }
	.segment-pill.active, .info-chip.active { background: linear-gradient(135deg, #edf3e7, #e1ebde); }
	.panel-stack > .section-card + .section-card, .list-stack > view + view { margin-top: 18rpx; }
	.field-label { display: block; margin-bottom: 10rpx; font-size: 24rpx; font-weight: 600; color: #49554b; }
	.field-input, .field-textarea, .picker-field { width: 100%; border-radius: 24rpx; background: #f8f6f1; border: 1rpx solid rgba(117, 131, 112, 0.12); color: #2c3530; font-size: 28rpx; }
	.field-input, .picker-field { height: 92rpx; padding: 0 24rpx; }
	.field-textarea { min-height: 220rpx; padding: 22rpx 24rpx; }
	.large-textarea, .json-textarea { min-height: 300rpx; }
	.field-placeholder { color: #9ba39c; }
	.picker-field { display: flex; align-items: center; }
	.primary-btn, .secondary-btn, .ghost-btn, .mini-btn, .large-btn { min-height: 84rpx; font-size: 28rpx; font-weight: 700; }
	.secondary-btn { background: rgba(236, 241, 232, 0.96) !important; color: #425041 !important; }
	.ghost-btn { background: transparent !important; border: 1rpx solid rgba(117, 131, 112, 0.16) !important; color: #5a6758 !important; }
	.large-btn { width: 100%; }
	.mini-btn { min-height: 68rpx; padding: 0 22rpx; font-size: 24rpx; border-radius: 20rpx; }
	.empty-block { padding: 44rpx 24rpx; text-align: center; color: #6d766d; }
	.small-empty { padding: 24rpx; }
	.recommend-message { background: rgba(132, 181, 140, 0.16); border: 1rpx solid rgba(92, 139, 99, 0.22); color: #36563f; }
	.recommend-scroll { white-space: nowrap; }
	.recommend-table { display: table; min-width: 1120rpx; width: 100%; border-radius: 22rpx; overflow: hidden; border: 1rpx solid rgba(117, 131, 112, 0.12); background: rgba(255, 252, 248, 0.96); }
	.recommend-row { display: table-row; }
	.recommend-row--importable { transition: background 0.2s ease; }
	.recommend-row--importable:active { background: rgba(220, 231, 214, 0.58); }
	.recommend-head { background: rgba(237, 243, 231, 0.9); }
	.recommend-col { display: table-cell; vertical-align: middle; padding: 16rpx 14rpx; font-size: 24rpx; color: #4f5d52; border-bottom: 1rpx solid rgba(117, 131, 112, 0.1); white-space: normal; line-height: 1.55; }
	.recommend-head .recommend-col { font-weight: 700; color: #384539; }
	.col-name { width: 170rpx; }
	.col-role { width: 170rpx; }
	.col-desc { width: 410rpx; }
	.col-status { width: 230rpx; }
	.col-action { width: 150rpx; text-align: center; }
	.project-history-list { display: flex; flex-direction: column; gap: 14rpx; }
	.project-history-card { display: flex; align-items: flex-start; gap: 16rpx; padding: 22rpx; background: rgba(255, 251, 246, 0.92); border: 1rpx solid rgba(117, 131, 112, 0.12); border-radius: 24rpx; box-shadow: 0 16rpx 48rpx rgba(106, 110, 89, 0.06); }
	.project-history-line { width: 8rpx; min-height: 116rpx; border-radius: 999rpx; background: linear-gradient(180deg, #87a17f 0%, #c7d7bd 100%); flex-shrink: 0; }
	.project-history-body { flex: 1; min-width: 0; }
	.project-history-meta { display: block; margin-top: 8rpx; color: #6d766d; font-size: 24rpx; line-height: 1.6; }
	.project-history-action { margin-left: 8rpx; }
	.list-card, .asset-card { display: flex; gap: 16rpx; align-items: center; justify-content: space-between; padding: 22rpx; }
	.list-card--stack { display: block; }
	.list-card__body { flex: 1; min-width: 0; }
	.asset-image, .preview-media, .preview-video { width: 100%; border-radius: 24rpx; background: #eff1ea; }
	.asset-image { width: 180rpx; height: 180rpx; flex-shrink: 0; }
	.shot-scroll { white-space: nowrap; }
	.shot-strip { display: inline-flex; gap: 14rpx; }
	.shot-pill { min-width: 220rpx; padding: 20rpx; }
	.shot-pill.active { background: linear-gradient(135deg, #edf3e7, #e1ebde); }
	.inline-progress, .progress-track { height: 10rpx; overflow: hidden; border-radius: 999rpx; background: rgba(126, 147, 122, 0.16); }
	.inline-progress { margin-top: 10rpx; }
	.inline-progress__bar, .progress-track__bar { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #9ab08b, #6f8f77); }
	.preview-media { height: 320rpx; }
	.preview-video { height: 420rpx; }
	.message-card { padding: 18rpx 20rpx; font-size: 24rpx; line-height: 1.7; }
	.message-card--error { background: rgba(213, 159, 150, 0.16); border: 1rpx solid rgba(192, 118, 104, 0.22); color: #8a4f45; }
	.top-gap { margin-top: 16rpx; }
</style>
