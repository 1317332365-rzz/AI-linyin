<template>
  <div class="phase">
    <h2>{{ phaseTitle }}</h2>
    <div class="workflow-brief">
      <strong>{{ workflowHeadline }}</strong>
      <p>{{ workflowDescription }}</p>
    </div>

    <div class="layout">
      <div class="panel input-panel">
        <div class="extract-toolbar">
          <button
            class="ghost"
            @click="extractCharactersByAi"
            :disabled="extractingCharacters || extractingScenes || !canExtractFromScript"
          >
            {{ extractingCharacters ? '提取中...' : 'AI提取角色' }}
          </button>
          <button
            class="ghost"
            @click="extractScenesByAi"
            :disabled="extractingCharacters || extractingScenes || !canExtractFromScript"
          >
            {{ extractingScenes ? '提取中...' : 'AI提取场景' }}
          </button>
        </div>
        <div v-if="!canExtractFromScript" class="extract-hint">
          当前没有可用剧本文本，请先在“剧本与分镜”阶段输入并保存本集剧本。
        </div>

        <div v-if="hasRecommendationCandidates" class="recommend-toolbar">
          <div class="recommend-controls">
            <select v-model="candidateStatusFilter" class="filter-select">
              <option value="pending">仅看待生成</option>
              <option value="generated">仅看已生成</option>
              <option value="all">全部状态</option>
            </select>
            <input
              v-model.trim="candidateKeyword"
              type="text"
              class="filter-input"
              placeholder="搜索候选关键词（角色名/描述）"
            />
          </div>
          <span class="recommend-summary">{{ recommendationSummary }}</span>
        </div>
        <div v-if="recommendActionMessage" class="candidate-action-msg">{{ recommendActionMessage }}</div>

        <div v-if="false && showSceneBuilder && recommendedSceneCandidates.length" class="candidate-block">
          <div class="candidate-head">
            <h3>分镜场次候选</h3>
            <span>从分镜直接带入场景风格（待生成 {{ pendingSceneCandidates.length }}）</span>
          </div>
          <div class="candidate-list">
            <article v-for="item in displaySceneCandidates" :key="`scene-${item.sceneId}`" class="candidate-item">
              <div class="candidate-main">
                <strong>{{ item.name }}</strong>
                <p>{{ item.description || item.shotSummary }}</p>
                <span>{{ item.duration }}</span>
                <span :class="item.generated ? 'tag-ok' : 'tag-pending'">{{ item.generated ? `已生成：${item.matchedAssets.join('、')}` : '推荐生成' }}</span>
              </div>
              <button class="mini" @click="fillSceneFromCandidate(item)">带入场景表单</button>
            </article>
            <div v-if="!displaySceneCandidates.length" class="candidate-empty">{{ sceneCandidateEmptyText }}</div>
          </div>
        </div>

        <div v-if="false && showCharacterBuilder && recommendedCharacterCandidates.length" class="candidate-block">
          <div class="candidate-head">
            <h3>角色圣经候选</h3>
            <span>从故事设计包直接带入角色库（待生成 {{ pendingCharacterCandidates.length }}）</span>
          </div>
          <div class="candidate-list">
            <article v-for="item in displayCharacterCandidates" :key="`char-${item.id}`" class="candidate-item">
              <div class="candidate-main">
                <strong>{{ item.name }}</strong>
                <p>{{ [item.role, item.goal, item.visualAnchor].filter(Boolean).join(' | ') || '待补充角色锚点' }}</p>
                <span :class="item.generated ? 'tag-ok' : 'tag-pending'">{{ item.generated ? `已生成：${item.matchedAssets.join('、')}` : '推荐生成' }}</span>
              </div>
              <button class="mini" @click="fillCharacterFromCandidate(item)">带入角色表单</button>
            </article>
            <div v-if="!displayCharacterCandidates.length" class="candidate-empty">{{ characterCandidateEmptyText }}</div>
          </div>
        </div>

        <div v-if="showSceneBuilder && recommendedSceneCandidates.length" class="candidate-block">
          <div class="candidate-head">
            <h3>AI 场景推荐</h3>
            <span>仅推荐，不会自动导入表单（待生成 {{ pendingSceneCandidates.length }}）</span>
          </div>
          <div class="candidate-table-wrap">
            <table class="candidate-table">
              <thead>
                <tr>
                  <th style="width: 110px;">推荐场景</th>
                  <th>场景描述</th>
                  <th style="width: 70px;">时长</th>
                  <th style="width: 180px;">状态</th>
                  <th style="width: 90px;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in displaySceneCandidates" :key="`scene-table-${item.sceneId}`">
                  <td>{{ item.name }}</td>
                  <td>{{ item.description || item.shotSummary || '-' }}</td>
                  <td>{{ item.duration || '-' }}</td>
                  <td>
                    <span :class="item.generated ? 'tag-ok' : 'tag-pending'">
                      {{ item.generated ? `已生成：${item.matchedAssets.join('、')}` : '推荐生成' }}
                    </span>
                  </td>
                  <td>
                    <button class="mini" @click="fillSceneFromCandidate(item)">导入</button>
                  </td>
                </tr>
                <tr v-if="!displaySceneCandidates.length">
                  <td class="candidate-empty-cell" colspan="5">{{ sceneCandidateEmptyText }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="showCharacterBuilder && recommendedCharacterCandidates.length" class="candidate-block">
          <div class="candidate-head">
            <h3>AI 角色推荐</h3>
            <span>仅推荐；右键某一行可快速导入角色表单（待生成 {{ pendingCharacterCandidates.length }}）</span>
          </div>
          <div class="candidate-table-wrap">
            <table class="candidate-table">
              <thead>
                <tr>
                  <th style="width: 110px;">角色名</th>
                  <th style="width: 140px;">角色定位</th>
                  <th>目标 / 视觉锚点</th>
                  <th style="width: 180px;">状态</th>
                  <th style="width: 90px;">导入</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in displayCharacterCandidates"
                  :key="`char-table-${item.id}`"
                  class="candidate-row-importable"
                  @contextmenu.prevent="importCharacterByContextMenu(item)"
                >
                  <td>{{ item.name || '-' }}</td>
                  <td>{{ item.role || '-' }}</td>
                  <td>{{ [item.goal, item.visualAnchor].filter(Boolean).join(' | ') || '-' }}</td>
                  <td>
                    <span :class="item.generated ? 'tag-ok' : 'tag-pending'">
                      {{ item.generated ? `已生成：${item.matchedAssets.join('、')}` : '推荐生成' }}
                    </span>
                  </td>
                  <td>
                    <button class="mini" @click="fillCharacterFromCandidate(item)">导入</button>
                  </td>
                </tr>
                <tr v-if="!displayCharacterCandidates.length">
                  <td class="candidate-empty-cell" colspan="5">{{ characterCandidateEmptyText }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="showSceneBuilder" class="section-block">
          <h3>场景风格资产</h3>
          <div class="form-group">
            <label for="sceneName">场景名称</label>
            <input id="sceneName" v-model="currentScene.name" type="text" placeholder="例如：青云山巅" />
          </div>
          <div class="form-group">
            <label for="sceneDesc">场景描述</label>
            <textarea
              id="sceneDesc"
              v-model="currentScene.description"
              rows="3"
              placeholder="描述空间布局、建筑风格、天气、时间、光线和整体氛围。"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="scenePrompt">增强提示词</label>
            <textarea
              id="scenePrompt"
              v-model="currentScene.prompt"
              rows="4"
              placeholder="可直接编辑场景风格提示词，也可以点击下方按钮自动增强。"
            ></textarea>
          </div>
          <div class="action-row">
            <button class="ghost" @click="enhanceScenePrompt" :disabled="sceneEnhancing || sceneLoading">
              {{ sceneEnhancing ? '增强中...' : '增强提示词' }}
            </button>
            <button @click="generateScene" :disabled="sceneLoading || sceneEnhancing" class="primary-btn scene-btn">
              {{ sceneLoading ? '生成中...' : '生成场景风格资产' }}
            </button>
          </div>
        </div>

        <div v-if="showCharacterBuilder" class="section-block" :class="{ 'scene-block': showSceneBuilder }">
          <h3>角色库资产</h3>
          <div class="form-group">
            <label for="characterName">角色名称</label>
            <input id="characterName" v-model="currentCharacter.name" type="text" placeholder="例如：叶青霜" />
          </div>
          <div class="form-group">
            <label for="characterDesc">角色描述</label>
            <textarea
              id="characterDesc"
              v-model="currentCharacter.description"
              rows="3"
              placeholder="描述外貌、年龄感、气质、服装体系、身份和时代质感。"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="wardrobe">造型版本</label>
            <select id="wardrobe" v-model="currentCharacter.wardrobe">
              <option value="日常">日常</option>
              <option value="战斗">战斗</option>
              <option value="仪式">仪式</option>
              <option value="受伤">受伤</option>
              <option value="自定义">自定义</option>
            </select>
            <input
              v-if="currentCharacter.wardrobe === '自定义'"
              v-model="currentCharacter.customWardrobe"
              type="text"
              placeholder="输入自定义造型，例如：雷雨夜披甲版"
              class="mt8"
            />
          </div>
          <div class="form-group">
            <label for="characterPrompt">增强提示词</label>
            <textarea
              id="characterPrompt"
              v-model="currentCharacter.prompt"
              rows="4"
              placeholder="可直接编辑角色定妆提示词，也可以点击下方按钮自动增强。"
            ></textarea>
          </div>
          <div class="action-row">
            <button class="ghost" @click="enhanceCharacterPrompt" :disabled="characterEnhancing || characterLoading">
              {{ characterEnhancing ? '增强中...' : '增强提示词' }}
            </button>
            <button @click="generateCharacter" :disabled="characterLoading || characterEnhancing" class="primary-btn">
              {{ characterLoading ? '生成中...' : '生成角色资产' }}
            </button>
          </div>
        </div>
      </div>

      <div class="panel result-panel">
        <div class="library-head">
          <h3>{{ libraryTitle }} ({{ filteredAssetsForLibrary.length }})</h3>
          <p>{{ libraryDescription }}</p>
        </div>
        <div class="library-toolbar">
          <select v-if="isCombinedStage" v-model="assetKindFilter" class="filter-select">
            <option value="all">全部资产</option>
            <option value="scene">仅场景资产</option>
            <option value="character">仅角色资产</option>
          </select>
          <input
            v-model.trim="assetKeyword"
            type="text"
            class="filter-input"
            placeholder="搜索资产关键词（名称/描述/提示词）"
          />
          <span class="library-summary">第 {{ currentAssetPage }} / {{ totalAssetPages }} 页 · 共 {{ filteredAssetsForLibrary.length }} 条</span>
        </div>
        <div v-if="filteredAssetsForLibrary.length === 0" class="empty-state">{{ assetEmptyText }}</div>
        <div v-else class="asset-grid">
          <div v-for="(asset, index) in pagedVisibleAssets" :key="String(asset?.id || index)" class="asset-item">
            <div class="asset-image">
              <img :src="asset.image_url" :alt="asset.name" />
              <button @click="deleteAsset(asset)" class="delete-btn" title="删除">×</button>
            </div>
            <div class="asset-info">
              <div class="asset-header">
                <h4>{{ asset.name }}</h4>
                <button class="icon-btn delete-icon" @click="deleteAsset(asset)" title="删除资产">删除</button>
              </div>
              <p class="asset-meta">
                {{ assetTypeLabel(asset) }}
                <span v-if="asset.wardrobe"> · {{ asset.wardrobe }}</span>
              </p>
              <p v-if="asset.prompt" class="asset-prompt">{{ asset.prompt }}</p>
            </div>
          </div>
        </div>
        <div v-if="filteredAssetsForLibrary.length > assetPageSize" class="pagination">
          <button class="mini" @click="assetPage = currentAssetPage - 1" :disabled="currentAssetPage <= 1">上一页</button>
          <span>第 {{ currentAssetPage }} / {{ totalAssetPages }} 页</span>
          <button class="mini" @click="assetPage = currentAssetPage + 1" :disabled="currentAssetPage >= totalAssetPages">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AssetsCasting',
  emits: ['asset-added', 'asset-deleted', 'script-updated'],
  props: {
    assets: {
      type: Array,
      default: () => []
    },
    storyboardScenes: {
      type: Array,
      default: () => []
    },
    storyPackage: {
      default: null
    },
    scriptInput: {
      type: String,
      default: ''
    },
    scriptDuration: {
      type: String,
      default: '3min'
    },
    workflowStage: {
      type: String,
      default: 'assets-casting'
    }
  },
  data() {
    return {
      candidateStatusFilter: 'pending',
      candidateKeyword: '',
      assetKeyword: '',
      assetKindFilter: 'all',
      assetPage: 1,
      assetPageSize: 8,
      currentCharacter: {
        name: '',
        description: '',
        wardrobe: '日常',
        customWardrobe: '',
        prompt: ''
      },
      currentScene: {
        name: '',
        description: '',
        prompt: ''
      },
      characterLoading: false,
      sceneLoading: false,
      characterEnhancing: false,
      sceneEnhancing: false,
      extractingCharacters: false,
      extractingScenes: false,
      recommendActionMessage: ''
    };
  },
  computed: {
    isCombinedStage() {
      return this.workflowStage === 'assets-casting';
    },
    isSceneStage() {
      return this.workflowStage === 'scene-style';
    },
    isCharacterStage() {
      return this.workflowStage === 'character-library';
    },
    canExtractFromScript() {
      return String(this.scriptInput || '').trim().length > 0;
    },
    phaseTitle() {
      if (this.isCombinedStage) return 'Phase 02: 资产与选角';
      return this.isCharacterStage ? 'Phase 04: 角色库选择' : 'Phase 03: 场景风格生成';
    },
    workflowHeadline() {
      if (this.isCombinedStage) {
        return '当前阶段统一管理场景资产和角色资产，并支持从分镜与角色圣经快速带入。';
      }
      return this.isCharacterStage
        ? '当前阶段只整理角色库，锁定角色定妆、服装版本和人物气质。'
        : '当前阶段先产出场景风格资产，为后续关键帧统一环境气质和空间结构。';
    },
    workflowDescription() {
      if (this.isCombinedStage) {
        return '建议先生成主场景，再生成主角色；后续在导演工作台按镜头绑定这些资产。';
      }
      return this.isCharacterStage
        ? '建议每个主角色保留一套主资产和少量造型变体，后续在关键帧阶段按镜头绑定。'
        : '建议每个主场景保留 1 到 2 张母版风格图，不要每个镜头都重新定义画风。';
    },
    showSceneBuilder() {
      return this.isCombinedStage || !this.isCharacterStage;
    },
    showCharacterBuilder() {
      return this.isCombinedStage || !this.isSceneStage;
    },
    characterAssets() {
      return (Array.isArray(this.assets) ? this.assets : []).filter((item) => this.assetKindOf(item) === 'character');
    },
    sceneAssets() {
      return (Array.isArray(this.assets) ? this.assets : []).filter((item) => this.assetKindOf(item) === 'scene');
    },
    visibleAssets() {
      if (this.isCombinedStage) return Array.isArray(this.assets) ? this.assets : [];
      return this.isCharacterStage ? this.characterAssets : this.sceneAssets;
    },
    sceneCandidates() {
      return (Array.isArray(this.storyboardScenes) ? this.storyboardScenes : [])
        .map((scene, index) => {
          const sceneId = String(scene?.scene_id || index + 1).trim() || String(index + 1);
          const description = String(scene?.description || '').trim();
          const shotSummary = String(scene?.shot_description || '').trim();
          const detailed = String(scene?.detailed_shot_description || '').trim();
          return {
            sceneId,
            name: `场次 ${sceneId}`,
            description,
            shotSummary,
            detailed,
            duration: String(scene?.duration || '5s').trim()
          };
        })
        .filter((item) => item.description || item.shotSummary || item.detailed);
    },
    characterCandidates() {
      let list = Array.isArray(this.storyPackage?.character_bible) ? this.storyPackage.character_bible : [];
      if (!list.length) {
        list = this.inferCharacterBibleFromScenes();
      }
      return list
        .map((item, index) => {
          const safe = item && typeof item === 'object' ? item : {};
          return {
            id: String(safe.name || index + 1).trim() || String(index + 1),
            name: String(safe.name || `角色${index + 1}`).trim(),
            role: String(safe.role || '').trim(),
            goal: String(safe.goal || '').trim(),
            tension: String(safe.tension || '').trim(),
            voice: String(safe.voice || '').trim(),
            visualAnchor: String(safe.visual_anchor || safe.visualAnchor || '').trim()
          };
        })
        .filter((item) => item.name);
    },
    recommendedSceneCandidates() {
      return this.sceneCandidates.map((item) => {
        const matchedAssets = this.sceneAssets.filter((asset) => this.isSceneCandidateMatched(item, asset));
        return {
          ...item,
          generated: matchedAssets.length > 0,
          matchedAssets: matchedAssets.map((asset) => String(asset?.name || '').trim()).filter(Boolean)
        };
      });
    },
    recommendedCharacterCandidates() {
      return this.characterCandidates.map((item) => {
        const matchedAssets = this.characterAssets.filter((asset) => this.isCharacterCandidateMatched(item, asset));
        return {
          ...item,
          generated: matchedAssets.length > 0,
          matchedAssets: matchedAssets.map((asset) => String(asset?.name || '').trim()).filter(Boolean)
        };
      });
    },
    pendingSceneCandidates() {
      return this.recommendedSceneCandidates.filter((item) => !item.generated);
    },
    pendingCharacterCandidates() {
      return this.recommendedCharacterCandidates.filter((item) => !item.generated);
    },
    displaySceneCandidates() {
      return this.filterCandidates(this.recommendedSceneCandidates);
    },
    displayCharacterCandidates() {
      return this.filterCandidates(this.recommendedCharacterCandidates);
    },
    hasRecommendationCandidates() {
      const sceneCount = this.showSceneBuilder ? this.recommendedSceneCandidates.length : 0;
      const characterCount = this.showCharacterBuilder ? this.recommendedCharacterCandidates.length : 0;
      return sceneCount > 0 || characterCount > 0;
    },
    recommendationSummary() {
      const chunks = [];
      if (this.showCharacterBuilder) {
        chunks.push(`角色待生成 ${this.pendingCharacterCandidates.length} / ${this.recommendedCharacterCandidates.length}`);
      }
      if (this.showSceneBuilder) {
        chunks.push(`场景待生成 ${this.pendingSceneCandidates.length} / ${this.recommendedSceneCandidates.length}`);
      }
      return chunks.join(' · ');
    },
    sceneCandidateEmptyText() {
      if (this.candidateStatusFilter === 'pending' && !this.candidateKeyword.trim()) {
        return '场景候选已全部生成。';
      }
      return '当前筛选条件下暂无场景候选。';
    },
    characterCandidateEmptyText() {
      if (this.candidateStatusFilter === 'pending' && !this.candidateKeyword.trim()) {
        return '角色候选已全部生成。';
      }
      return '当前筛选条件下暂无角色候选。';
    },
    filteredAssetsForLibrary() {
      let list = Array.isArray(this.visibleAssets) ? [...this.visibleAssets] : [];
      if (this.isCombinedStage && this.assetKindFilter !== 'all') {
        list = list.filter((asset) => this.assetKindOf(asset) === this.assetKindFilter);
      }
      const keyword = this.normalizeToken(this.assetKeyword);
      if (!keyword) return list;
      return list.filter((asset) => {
        const text = this.buildAssetSearchText(asset);
        const wardrobe = this.normalizeToken(asset?.wardrobe);
        return text.includes(keyword) || wardrobe.includes(keyword);
      });
    },
    totalAssetPages() {
      return Math.max(1, Math.ceil(this.filteredAssetsForLibrary.length / this.assetPageSize));
    },
    currentAssetPage() {
      const page = Number(this.assetPage) || 1;
      return Math.min(Math.max(page, 1), this.totalAssetPages);
    },
    pagedVisibleAssets() {
      const start = (this.currentAssetPage - 1) * this.assetPageSize;
      return this.filteredAssetsForLibrary.slice(start, start + this.assetPageSize);
    },
    libraryTitle() {
      if (this.isCombinedStage) return '资产库';
      return this.isCharacterStage ? '角色资产库' : '场景风格资产库';
    },
    libraryDescription() {
      if (this.isCombinedStage) {
        return '这里统一展示当前项目的角色资产与场景资产。';
      }
      return this.isCharacterStage
        ? '这些角色资产会在关键帧阶段被绑定到具体镜头。'
        : '这些场景资产会在关键帧阶段锁定环境布局、天气、时间和光线。';
    },
    assetEmptyText() {
      if (!this.visibleAssets.length) {
        return '当前阶段还没有可用资产，请先在左侧生成。';
      }
      return '没有匹配筛选条件的资产，请调整关键词或筛选项。';
    }
  },
  watch: {
    assetKeyword() {
      this.assetPage = 1;
    },
    assetKindFilter() {
      this.assetPage = 1;
    },
    workflowStage() {
      this.assetPage = 1;
      this.assetKindFilter = 'all';
    },
    totalAssetPages(nextPage) {
      if (this.assetPage > nextPage) {
        this.assetPage = nextPage;
      }
    }
  },
  beforeUnmount() {
    if (this._recommendMsgTimer) clearTimeout(this._recommendMsgTimer);
  },
  methods: {
    resolvedScriptDuration() {
      return String(this.scriptDuration || '').trim() || '3min';
    },
    parseTimeoutMs() {
      const text = this.resolvedScriptDuration().toLowerCase();
      if (text === '30s') return 120000;
      if (text === '3min') return 300000;
      if (text === '5min') return 420000;

      const minuteMatch = text.match(/(\d+(?:\.\d+)?)\s*(min|分钟|minute|minutes|m)\b/);
      if (minuteMatch) {
        const minutes = Number(minuteMatch[1]);
        if (Number.isFinite(minutes) && minutes > 0) {
          const seconds = Math.round(minutes * 60);
          return Math.max(120000, Math.min(600000, seconds * 1000 + 90000));
        }
      }

      const secondMatch = text.match(/(\d+)\s*(s|sec|secs|second|seconds|秒)\b/);
      if (secondMatch) {
        const seconds = Number(secondMatch[1]);
        if (Number.isFinite(seconds) && seconds > 0) {
          return Math.max(120000, Math.min(600000, seconds * 1000 + 90000));
        }
      }
      return 240000;
    },
    currentScriptResult() {
      return {
        story_package: this.storyPackage && typeof this.storyPackage === 'object' ? { ...this.storyPackage } : {},
        scenes: Array.isArray(this.storyboardScenes) ? [...this.storyboardScenes] : []
      };
    },
    emitScriptUpdated(result) {
      this.$emit('script-updated', {
        script: String(this.scriptInput || '').trim(),
        duration: this.resolvedScriptDuration(),
        result
      });
    },
    inferCharacterBibleFromScenes() {
      const scenes = Array.isArray(this.storyboardScenes) ? this.storyboardScenes : [];
      const list = [];
      const seen = new Set();
      const pushName = (rawName) => {
        const name = String(rawName || '').trim();
        if (!name || name.length > 16) return;
        const key = name.toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        list.push({
          name,
          role: '待补充',
          goal: '',
          tension: '',
          voice: '',
          visual_anchor: ''
        });
      };

      scenes.forEach((scene) => {
        if (!scene || typeof scene !== 'object') return;
        ['dialogue_details', 'dialogue_beats'].forEach((key) => {
          const beats = scene[key];
          if (!Array.isArray(beats)) return;
          beats.forEach((beat) => {
            if (!beat || typeof beat !== 'object') return;
            pushName(beat.speaker || beat.role || beat.character);
          });
        });
        const dialogueText = String(scene.dialogue || '').trim();
        if (!dialogueText) return;
        dialogueText.split('\n').forEach((line) => {
          const match = line.match(/^\s*([^:：\s]{1,12})\s*[:：]/);
          if (match) pushName(match[1]);
        });
      });

      return list;
    },
    async requestAiExtraction() {
      const scriptText = String(this.scriptInput || '').trim();
      if (!scriptText) {
        throw new Error('请先在剧本阶段输入并保存剧本');
      }
      const response = await axios.post('/api/parse-script', {
        script: scriptText,
        duration: this.resolvedScriptDuration()
      }, {
        timeout: this.parseTimeoutMs()
      });
      return response?.data && typeof response.data === 'object' ? response.data : {};
    },
    sanitizeCharacterBible(items) {
      if (!Array.isArray(items)) return [];
      const seen = new Set();
      return items
        .map((item) => (item && typeof item === 'object' ? item : {}))
        .map((item) => ({
          ...item,
          name: String(item.name || '').trim()
        }))
        .filter((item) => {
          if (!item.name) return false;
          const key = item.name.toLowerCase();
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });
    },
    buildMergedResultFromAi(aiResult) {
      const currentResult = this.currentScriptResult();
      const incomingScenes = Array.isArray(aiResult?.scenes) ? aiResult.scenes : [];
      const incomingStoryPackage = aiResult?.story_package && typeof aiResult.story_package === 'object'
        ? aiResult.story_package
        : {};
      const incomingCharacters = this.sanitizeCharacterBible(incomingStoryPackage.character_bible);
      const currentStoryPackage = currentResult?.story_package && typeof currentResult.story_package === 'object'
        ? currentResult.story_package
        : {};
      const currentCharacters = this.sanitizeCharacterBible(currentStoryPackage.character_bible);

      return {
        ...currentResult,
        ...aiResult,
        story_package: {
          ...currentStoryPackage,
          ...incomingStoryPackage,
          character_bible: incomingCharacters.length ? incomingCharacters : currentCharacters
        },
        scenes: incomingScenes.length
          ? incomingScenes
          : (Array.isArray(currentResult.scenes) ? currentResult.scenes : [])
      };
    },
    async runAiExtraction(trigger = 'all') {
      if (this.extractingCharacters || this.extractingScenes) return;
      if (!this.canExtractFromScript) {
        alert('请先在剧本阶段输入并保存剧本');
        return;
      }

      if (trigger === 'character') {
        this.extractingCharacters = true;
      } else {
        this.extractingScenes = true;
      }

      try {
        const aiResult = await this.requestAiExtraction();
        const mergedResult = this.buildMergedResultFromAi(aiResult);
        const scenes = Array.isArray(mergedResult?.scenes) ? mergedResult.scenes : [];
        const characters = this.sanitizeCharacterBible(mergedResult?.story_package?.character_bible);
        if (!scenes.length && !characters.length) {
          alert('未提取到场景或角色，请补充剧本后重试');
          return;
        }
        this.emitScriptUpdated(mergedResult);
        alert(`AI提取完成：场景 ${scenes.length} 个，角色 ${characters.length} 个`);
      } catch (error) {
        const message = String(error?.response?.data?.error || error?.message || '请求失败').trim();
        alert(`AI提取失败：${message}`);
      } finally {
        this.extractingCharacters = false;
        this.extractingScenes = false;
      }
    },
    async extractCharactersByAi() {
      await this.runAiExtraction('character');
    },
    async extractScenesByAi() {
      await this.runAiExtraction('scene');
    },
    normalizeToken(value) {
      return String(value || '')
        .trim()
        .toLowerCase()
        .replace(/[\s\-_.:,;'"`~!@#$%^&*(){}\[\]<>?/\\|，。！？、；：“”‘’（）【】《》]/g, '');
    },
    buildAssetSearchText(asset) {
      const safe = asset && typeof asset === 'object' ? asset : {};
      const text = [
        safe.name,
        safe.prompt,
        safe.source_description,
        safe.type,
        safe.asset_kind,
        safe.wardrobe
      ].map((item) => this.normalizeToken(item)).join(' ');
      return text;
    },
    filterCandidates(items) {
      const list = Array.isArray(items) ? items : [];
      const keyword = this.normalizeToken(this.candidateKeyword);
      return list.filter((item) => {
        const generated = Boolean(item?.generated);
        if (this.candidateStatusFilter === 'pending' && generated) return false;
        if (this.candidateStatusFilter === 'generated' && !generated) return false;
        if (!keyword) return true;
        const searchText = [
          item?.name,
          item?.description,
          item?.shotSummary,
          item?.detailed,
          item?.role,
          item?.goal,
          item?.tension,
          item?.voice,
          item?.visualAnchor,
          Array.isArray(item?.matchedAssets) ? item.matchedAssets.join(' ') : ''
        ].map((value) => this.normalizeToken(value)).join(' ');
        return searchText.includes(keyword);
      });
    },
    isCharacterCandidateMatched(candidate, asset) {
      const safe = candidate || {};
      const assetText = this.buildAssetSearchText(asset);
      if (!assetText) return false;
      const tokens = [
        this.normalizeToken(safe.name),
        this.normalizeToken(safe.role),
        this.normalizeToken(String(safe.visualAnchor || '').slice(0, 10))
      ].filter((token) => token && token.length >= 2);
      if (!tokens.length) return false;
      return tokens.some((token) => assetText.includes(token));
    },
    isSceneCandidateMatched(candidate, asset) {
      const safe = candidate || {};
      const assetText = this.buildAssetSearchText(asset);
      if (!assetText) return false;
      const sceneName = String(safe.name || '').replace(/^场次\s*\d+\s*/, '');
      const tokens = [
        this.normalizeToken(sceneName),
        this.normalizeToken(String(safe.description || '').slice(0, 12)),
        this.normalizeToken(String(safe.shotSummary || '').slice(0, 12))
      ].filter((token) => token && token.length >= 2);
      if (!tokens.length) return false;
      return tokens.some((token) => assetText.includes(token));
    },
    assetKindOf(asset) {
      const safe = asset && typeof asset === 'object' ? asset : {};
      const typeText = [
        safe.asset_kind,
        safe.assetKind,
        safe.type,
        safe.asset_type,
        safe.category,
        safe.prompt_type
      ].map((item) => String(item || '').trim().toLowerCase()).join(' ');
      const promptText = [safe.name, safe.prompt, safe.source_description]
        .map((item) => String(item || '').trim().toLowerCase())
        .join(' ');

      if (/character|角色/.test(typeText) || /角色/.test(promptText) || String(safe.wardrobe || '').trim()) {
        return 'character';
      }
      if (/scene|场景/.test(typeText) || /场景|环境/.test(promptText)) {
        return 'scene';
      }
      return '';
    },
    assetTypeLabel(asset) {
      return this.assetKindOf(asset) === 'character' ? '角色资产' : '场景资产';
    },
    fillSceneFromCandidate(candidate) {
      const safe = candidate || {};
      const parts = [
        String(safe.description || '').trim(),
        String(safe.shotSummary || '').trim(),
        String(safe.detailed || '').trim()
      ].filter(Boolean);
      this.currentScene.name = String(safe.name || '').trim();
      this.currentScene.description = [...new Set(parts)].join('，');
      this.currentScene.prompt = '';
    },
    setRecommendActionMessage(message) {
      const text = String(message || '').trim();
      this.recommendActionMessage = text;
      if (this._recommendMsgTimer) clearTimeout(this._recommendMsgTimer);
      if (!text) return;
      this._recommendMsgTimer = setTimeout(() => {
        this.recommendActionMessage = '';
      }, 2600);
    },
    importCharacterByContextMenu(candidate) {
      this.fillCharacterFromCandidate(candidate);
      const name = String(candidate?.name || '').trim() || '当前角色';
      this.setRecommendActionMessage(`已右键导入角色：${name}`);
    },
    fillCharacterFromCandidate(candidate) {
      const safe = candidate || {};
      const parts = [
        String(safe.role || '').trim() && `角色定位：${String(safe.role || '').trim()}`,
        String(safe.goal || '').trim() && `目标：${String(safe.goal || '').trim()}`,
        String(safe.tension || '').trim() && `张力：${String(safe.tension || '').trim()}`,
        String(safe.voice || '').trim() && `声音气质：${String(safe.voice || '').trim()}`,
        String(safe.visualAnchor || '').trim() && `视觉锚点：${String(safe.visualAnchor || '').trim()}`
      ].filter(Boolean);
      this.currentCharacter.name = String(safe.name || '').trim();
      this.currentCharacter.description = parts.join('，');
      this.currentCharacter.prompt = '';
      this.currentCharacter.wardrobe = '日常';
      this.currentCharacter.customWardrobe = '';
    },
    normalizedWardrobe() {
      return this.currentCharacter.wardrobe === '自定义'
        ? String(this.currentCharacter.customWardrobe || '').trim()
        : String(this.currentCharacter.wardrobe || '').trim();
    },
    buildCharacterBasePrompt() {
      const wardrobe = this.normalizedWardrobe();
      return [
        this.currentCharacter.name ? `角色：${this.currentCharacter.name}` : '',
        this.currentCharacter.description,
        wardrobe ? `造型：${wardrobe}` : '',
        '中国风动画角色设定图，单幅完整构图，五官、发型、服装和气质保持稳定统一。'
      ].filter(Boolean).join('，');
    },
    buildSceneBasePrompt() {
      return [
        this.currentScene.name ? `场景：${this.currentScene.name}` : '',
        this.currentScene.description,
        '中国风动画场景母版图，单幅完整构图，空间关系明确，禁止分屏、拼贴、字幕和水印。'
      ].filter(Boolean).join('，');
    },
    async requestEnhancedPrompt(prompt, context = {}) {
      const rawPrompt = String(prompt || '').trim();
      if (!rawPrompt) return '';
      const response = await axios.post('/api/enhance-prompt', { prompt: rawPrompt, context });
      return String(response.data?.enhanced_prompt || '').trim();
    },
    async enhanceCharacterPrompt() {
      if (!this.currentCharacter.name || !this.currentCharacter.description) {
        alert('请先输入角色名称和角色描述');
        return;
      }
      this.characterEnhancing = true;
      try {
        const enhanced = await this.requestEnhancedPrompt(this.currentCharacter.prompt || this.buildCharacterBasePrompt(), {
          prompt_type: 'character_asset',
          asset_type: 'character',
          name: this.currentCharacter.name,
          subject_name: this.currentCharacter.name,
          wardrobe: this.normalizedWardrobe(),
          visual_style: '中国风动画，角色定妆稳定，东方电影感'
        });
        if (enhanced) this.currentCharacter.prompt = enhanced;
      } catch (error) {
        const msg = String(error?.response?.data?.error || error?.message || '提示词增强失败').trim();
        alert(`角色提示词增强失败：${msg}`);
      } finally {
        this.characterEnhancing = false;
      }
    },
    async enhanceScenePrompt() {
      if (!this.currentScene.name || !this.currentScene.description) {
        alert('请先输入场景名称和场景描述');
        return;
      }
      this.sceneEnhancing = true;
      try {
        const enhanced = await this.requestEnhancedPrompt(this.currentScene.prompt || this.buildSceneBasePrompt(), {
          prompt_type: 'scene_asset',
          asset_type: 'scene',
          name: this.currentScene.name,
          subject_name: this.currentScene.name,
          visual_style: '中国风动画，东方电影感，单幅场景母版'
        });
        if (enhanced) this.currentScene.prompt = enhanced;
      } catch (error) {
        const msg = String(error?.response?.data?.error || error?.message || '提示词增强失败').trim();
        alert(`场景提示词增强失败：${msg}`);
      } finally {
        this.sceneEnhancing = false;
      }
    },
    async generateCharacter() {
      if (!this.currentCharacter.name || !this.currentCharacter.description) {
        alert('请输入角色名称和角色描述');
        return;
      }

      this.characterLoading = true;
      try {
        const wardrobe = this.normalizedWardrobe();
        const prompt = String(this.currentCharacter.prompt || this.buildCharacterBasePrompt()).trim();
        const response = await axios.post('/api/generate-character', {
          description: prompt
        });

        this.$emit('asset-added', {
          ...response.data,
          name: this.currentCharacter.name,
          type: '角色',
          asset_kind: 'character',
          wardrobe,
          prompt,
          source_description: this.currentCharacter.description
        });
      } catch (error) {
        const msg = String(error?.response?.data?.error || error?.message || '生成角色失败').trim();
        alert(`生成角色失败：${msg}`);
      } finally {
        this.characterLoading = false;
      }
    },
    async generateScene() {
      if (!this.currentScene.name || !this.currentScene.description) {
        alert('请输入场景名称和场景描述');
        return;
      }

      this.sceneLoading = true;
      try {
        const prompt = String(this.currentScene.prompt || this.buildSceneBasePrompt()).trim();
        const response = await axios.post('/api/generate-scene', {
          description: prompt
        });

        this.$emit('asset-added', {
          ...response.data,
          name: this.currentScene.name,
          type: '场景',
          asset_kind: 'scene',
          prompt,
          source_description: this.currentScene.description
        });
      } catch (error) {
        const msg = String(error?.response?.data?.error || error?.message || '生成场景失败').trim();
        alert(`生成场景失败：${msg}`);
      } finally {
        this.sceneLoading = false;
      }
    },
    deleteAsset(asset) {
      const assetId = String(asset?.id || '').trim();
      const index = (Array.isArray(this.assets) ? this.assets : []).findIndex((item) => {
        if (assetId) return String(item?.id || '').trim() === assetId;
        return item === asset;
      });
      if (index >= 0) {
        this.$emit('asset-deleted', index);
      }
    }
  }
};
</script>

<style scoped>
.phase {
  background: linear-gradient(180deg, #0d1f24, #0a171b);
  border-color: #2b4f57;
  color: #e8fbf8;
}

.phase h2 {
  color: #e8fbf8;
  border-bottom: 2px solid rgba(45, 212, 191, 0.5);
}

.workflow-brief {
  margin-bottom: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(19, 48, 56, 0.88);
  border: 1px solid rgba(45, 212, 191, 0.22);
}

.workflow-brief strong {
  display: block;
  color: #e8fbf8;
  margin-bottom: 4px;
}

.workflow-brief p {
  margin: 0;
  color: #9fc5bf;
  line-height: 1.5;
}

.layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 20px;
}

.panel {
  background-color: #123038;
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #2f5861;
  box-shadow: none;
}

.panel :deep(label) {
  color: #bfe6de;
}

.panel :deep(input),
.panel :deep(select),
.panel :deep(textarea) {
  background: #0f252a;
  border-color: #3f6a72;
  color: #e8fbf8;
}

.panel :deep(input:focus),
.panel :deep(select:focus),
.panel :deep(textarea:focus) {
  outline-color: rgba(45, 212, 191, 0.35);
  border-color: #2dd4bf;
}

.section-block h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #e8fbf8;
  font-size: 16px;
  border-left: 4px solid #2dd4bf;
  padding-left: 10px;
}

.extract-toolbar {
  margin-bottom: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.extract-hint {
  margin-bottom: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px dashed #3f6a72;
  color: #9fc5bf;
  font-size: 12px;
  line-height: 1.45;
  background: rgba(15, 40, 46, 0.72);
}

.recommend-toolbar {
  margin-bottom: 14px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #2f5861;
  background: #163840;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  color: #bfe6de;
  font-size: 12px;
}

.recommend-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-select,
.filter-input {
  min-height: 34px;
}

.filter-input {
  min-width: 220px;
}

.recommend-summary {
  margin-left: auto;
  color: #9fc5bf;
  line-height: 1.45;
}

.candidate-action-msg {
  margin-bottom: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(22, 163, 74, 0.55);
  background: rgba(21, 128, 61, 0.18);
  color: #bbf7d0;
  font-size: 12px;
}

.candidate-table-wrap {
  border-radius: 8px;
  border: 1px solid #2f5861;
  overflow-x: auto;
  background: #0f252a;
}

.candidate-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 680px;
}

.candidate-table th,
.candidate-table td {
  border-bottom: 1px solid rgba(63, 106, 114, 0.65);
  padding: 9px 10px;
  text-align: left;
  vertical-align: top;
  font-size: 13px;
  line-height: 1.4;
}

.candidate-table th {
  color: #bfe6de;
  background: rgba(19, 48, 56, 0.72);
  font-weight: 600;
}

.candidate-table td {
  color: #e8fbf8;
}

.candidate-table tbody tr:last-child td {
  border-bottom: none;
}

.candidate-row-importable {
  cursor: context-menu;
}

.candidate-row-importable:hover td {
  background: rgba(45, 212, 191, 0.08);
}

.candidate-empty-cell {
  text-align: center;
  color: #9fc5bf !important;
}

.candidate-block {
  margin-bottom: 18px;
  padding: 14px;
  border-radius: 10px;
  border: 1px solid #2f5861;
  background: #163840;
}

.candidate-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.candidate-head h3 {
  margin: 0;
  color: #e8fbf8;
  font-size: 15px;
}

.candidate-head span {
  color: #9fc5bf;
  font-size: 12px;
}

.candidate-list {
  display: grid;
  gap: 10px;
}

.candidate-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #0f252a;
  border: 1px solid #2f5861;
}

.candidate-main strong {
  display: block;
  color: #e8fbf8;
  margin-bottom: 4px;
}

.candidate-main p {
  margin: 0;
  color: #bfe6de;
  font-size: 13px;
  line-height: 1.45;
}

.candidate-main span {
  display: inline-block;
  margin-top: 6px;
  color: #8fb1ac;
  font-size: 12px;
}

.tag-ok {
  color: #86efac;
}

.tag-pending {
  color: #fbbf24;
}

.candidate-empty {
  padding: 10px 12px;
  border-radius: 8px;
  background: #0f252a;
  border: 1px dashed #3f6a72;
  color: #9fc5bf;
  font-size: 13px;
}

.scene-block {
  margin-top: 20px;
  border-top: 1px solid #2f5861;
  padding-top: 20px;
}

.action-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mt8 {
  margin-top: 8px;
}

.primary-btn {
  background-color: #0f8f78;
}

.primary-btn:hover {
  background-color: #0b7563;
}

.library-head {
  margin-bottom: 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #2f5861;
}

.library-head h3 {
  margin: 0 0 6px;
  color: #e8fbf8;
}

.library-head p {
  margin: 0;
  color: #9fc5bf;
  line-height: 1.5;
}

.library-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.library-summary {
  margin-left: auto;
  color: #9fc5bf;
  font-size: 12px;
}

.empty-state {
  color: #9fc5bf;
  text-align: center;
  padding: 40px;
  background-color: #163840;
  border: 1px dashed #3f6a72;
  border-radius: 8px;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.asset-item {
  background-color: #163840;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #2f5861;
  transition: transform 0.2s;
}

.asset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 0 1px rgba(45, 212, 191, 0.4);
}

.asset-image {
  position: relative;
  height: 180px;
  background-color: #0f252a;
}

.asset-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: rgba(185, 28, 28, 0.9);
  color: white;
  border: none;
  cursor: pointer;
}

.asset-info {
  padding: 12px;
}

.asset-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.asset-header h4 {
  margin: 0;
  color: #e8fbf8;
}

.asset-meta {
  margin: 8px 0;
  color: #9fc5bf;
  font-size: 13px;
}

.asset-prompt {
  margin: 0;
  color: #d7f5ef;
  font-size: 13px;
  line-height: 1.5;
  max-height: 118px;
  overflow: auto;
}

.delete-icon {
  padding: 0;
  min-width: 0;
  background: transparent;
  color: #fda4af;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
  color: #9fc5bf;
  font-size: 12px;
}

@media (max-width: 980px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .recommend-summary,
  .library-summary {
    width: 100%;
    margin-left: 0;
  }

  .filter-input {
    min-width: 160px;
    flex: 1;
  }
}
</style>
