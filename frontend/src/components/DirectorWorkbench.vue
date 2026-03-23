
<template>
  <div class="phase workbench-phase">
    <header class="wb-header">
      <div class="wb-header-top">
        <div>
          <h2>{{ stageTitle }}</h2>
          <p>第 {{ currentEpisodeNo }} 集 · {{ localShots.length }} 个镜头 · {{ stageSummary }}</p>
        </div>
        <div class="wb-toolbar">
          <button
            class="ghost"
            @click="importShotsFromStoryboard"
            :disabled="!parsedScenes.length || batchGeneratingFrames || batchGeneratingVideos"
          >
            重写导入分镜
          </button>
          <button class="ghost" @click="sortShotsBySceneNo" :disabled="!localShots.length || batchGeneratingFrames || batchGeneratingVideos">
            按场景编号排序
          </button>
          <button class="ghost" @click="addShot">新增镜头</button>
          <button
            class="ghost"
            @click="aiMatchCharactersForAllShots"
            :disabled="!localShots.length || !characterAssets.length || batchGeneratingFrames || batchGeneratingVideos"
          >
            AI匹配角色
          </button>
          <button
            class="ghost"
            @click="aiMatchScenesForAllShots"
            :disabled="!localShots.length || !sceneAssets.length || batchGeneratingFrames || batchGeneratingVideos"
          >
            AI匹配场景
          </button>
          <label class="toolbar-check">
            <input type="checkbox" v-model="testSegmentMode" />
            片段测试模式
          </label>
          <button v-if="isKeyframeStage" class="ghost" data-tour="btn-generate-all-frames" @click="generateAllFrames" :disabled="!localShots.length || batchGeneratingFrames || batchGeneratingVideos">
            {{ batchGeneratingFrames ? '批量关键帧生成中...' : '一键生成所有前后帧' }}
          </button>
          <button
            v-if="isKeyframeStage"
            class="ghost"
            @click="generateFramesFromCurrent"
            :disabled="selectedShotIndex < 0 || batchGeneratingFrames || batchGeneratingVideos"
          >
            从当前镜头生成后续前后帧
          </button>
          <button v-if="isVideoStage" class="ghost" data-tour="btn-generate-all-videos" @click="generateAllVideos" :disabled="!localShots.length || batchGeneratingFrames || batchGeneratingVideos">
            {{ batchGeneratingVideos ? '批量视频提交中...' : '一键生成所有视频' }}
          </button>
          <button
            v-if="isVideoStage"
            class="ghost"
            @click="generateVideosFromCurrent"
            :disabled="selectedShotIndex < 0 || batchGeneratingFrames || batchGeneratingVideos"
          >
            从当前镜头提交后续视频
          </button>
          <span class="link-toggle">{{ stageTagline }}</span>
        </div>
      </div>
      <div class="workflow-brief">{{ workflowDescription }}</div>
      <div v-if="batchStatusText" class="batch-status">
        <div>{{ batchStatusText }}</div>
        <div v-if="batchProgressTotal > 0" class="batch-inline-progress">
          <div class="progress-track"><div class="progress-fill" :style="{ width: `${batchProgressPercent}%` }"></div></div>
          <span>{{ batchProgressPercent }}%</span>
        </div>
      </div>
    </header>

    <div class="wb-layout">
      <section class="panel-dark">
        <div v-if="parsedScenes.length" class="scene-auto-tip">
          已自动载入当前集分镜 {{ parsedScenes.length }} 条，可直接在下方表格编辑。
        </div>
        <div v-else class="empty-inline">当前集暂无分镜，先去剧本阶段生成或手动新增镜头。</div>

        <div v-if="isVideoStage" class="table-config-row">
          <div class="config-group">
            <label for="videoMode">模式</label>
            <select id="videoMode" v-model="videoMode">
              <option value="image-to-video">image-to-video</option>
              <option value="keyframe-interpolation">keyframe-interpolation</option>
            </select>
          </div>
          <div class="config-group">
            <label for="videoRatio">画幅</label>
            <select id="videoRatio" v-model="videoRatio">
              <option value="16:9">16:9（全屏）</option>
              <option value="adaptive">adaptive</option>
              <option value="9:16">9:16</option>
              <option value="1:1">1:1</option>
            </select>
          </div>
          <div class="config-checks">
            <label><input type="checkbox" v-model="generateAudio" /> 生成音频</label>
            <label><input type="checkbox" v-model="watermark" /> 添加水印</label>
          </div>
        </div>

        <div class="section-head mt8">
          <h3>导演工作台</h3>
          <span>操作集中在每行右侧工具栏</span>
        </div>
        <div v-if="localShots.length" class="workbench-table-wrap">
          <table class="workbench-table">
            <thead>
              <tr>
                <th style="width: 74px;">镜头</th>
                <th style="width: 140px;">标题</th>
                <th style="width: 84px;">时长</th>
                <th>Shot Prompt</th>
                <th style="width: 220px;">旁白</th>
                <th style="width: 220px;">资产绑定</th>
                <th style="width: 140px;">起始帧</th>
                <th style="width: 140px;">结束帧</th>
                <th style="width: 120px;">状态</th>
                <th style="width: 220px;">视频预览</th>
                <th style="width: 260px;">工具栏</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(shot, index) in localShots"
                :key="`wb-shot-${index}`"
                :class="{ selected: selectedShotIndex === index }"
                @click="selectShot(index)"
              >
                <td class="idx-col">SHOT {{ String(index + 1).padStart(2, '0') }}</td>
                <td>
                  <div class="cell-title">{{ shot.title || `镜头 ${index + 1}` }}</div>
                </td>
                <td>
                  <div class="cell-duration">{{ shot.duration || '5s' }}</div>
                </td>
                <td>
                  <pre class="narrative-preview">{{ shotPromptPreview(shot, 3) }}</pre>
                </td>
                <td>
                  <pre class="narrative-preview">{{ shotVoiceoverPreview(shot, 3) }}</pre>
                </td>
                <td>
                  <div class="binding-preview">
                    <strong>角色：</strong>{{ shotCharacterBindingText(shot) }}
                  </div>
                  <div class="binding-preview">
                    <strong>场景：</strong>{{ shotSceneBindingText(shot) }}
                  </div>
                </td>
                <td>
                  <div class="frame-mini-box">
                    <img v-if="shot.startFrame?.image_url" :src="shot.startFrame.image_url" alt="start frame" />
                    <div v-else class="thumb-empty">暂无</div>
                  </div>
                  <div class="frame-url-preview">{{ shortUrlText(shot.startFrame?.image_url) }}</div>
                </td>
                <td>
                  <div class="frame-mini-box">
                    <img v-if="shot.endFrame?.image_url" :src="shot.endFrame.image_url" alt="end frame" />
                    <div v-else class="thumb-empty">暂无</div>
                  </div>
                  <div class="frame-url-preview">{{ shortUrlText(shot.endFrame?.image_url) }}</div>
                </td>
                <td>
                  <span class="shot-state" :class="`state-${shotStatusClass(shot)}`">{{ shotStatusLabel(shot) }}</span>
                  <div class="progress-track progress-track-mini">
                    <div class="progress-fill" :style="{ width: `${rowTaskProgress(shot)}%` }"></div>
                  </div>
                  <a v-if="shot.videoUrl" :href="shot.videoUrl" target="_blank" rel="noopener" @click.stop>预览</a>
                </td>
                <td>
                  <div class="video-mini-box" @click.stop>
                    <video
                      v-if="shot.videoUrl"
                      :src="shot.videoUrl"
                      controls
                      playsinline
                      preload="metadata"
                    ></video>
                    <div v-else class="thumb-empty">暂无视频</div>
                  </div>
                </td>
                <td class="row-tools" @click.stop>
                  <button class="mini" :disabled="batchGeneratingFrames || batchGeneratingVideos" @click="openEditShotDialog(index)">
                    编辑
                  </button>
                  <button
                    v-if="isKeyframeStage"
                    class="mini row-btn"
                    :disabled="batchGeneratingFrames || batchGeneratingVideos || isStartFrameLoading(index)"
                    @click="generateStartFrameForRow(index)"
                  >
                    <span v-if="isStartFrameLoading(index)" class="btn-spinner"></span>
                    {{ isStartFrameLoading(index) ? '生成中' : '起始帧' }}
                  </button>
                  <button
                    v-if="isKeyframeStage"
                    class="mini row-btn"
                    :disabled="batchGeneratingFrames || batchGeneratingVideos || isEndFrameLoading(index)"
                    @click="generateEndFrameForRow(index)"
                  >
                    <span v-if="isEndFrameLoading(index)" class="btn-spinner"></span>
                    {{ isEndFrameLoading(index) ? '生成中' : '结束帧' }}
                  </button>
                  <button
                    v-if="isVideoStage"
                    class="mini row-btn"
                    :disabled="batchGeneratingFrames || batchGeneratingVideos || isVideoLoading(index) || !isUsableImageUrl(shot?.startFrame?.image_url)"
                    @click="generateVideoForRow(index)"
                  >
                    <span v-if="isVideoLoading(index)" class="btn-spinner"></span>
                    {{ isVideoLoading(index) ? '提交中' : '提交视频' }}
                  </button>
                  <button
                    v-if="isVideoStage"
                    class="mini row-btn"
                    :disabled="isRefreshLoading(index) || !String(shot?.videoTask?.taskId || '').trim()"
                    @click="refreshVideoTaskStatusForRow(index)"
                  >
                    <span v-if="isRefreshLoading(index)" class="btn-spinner"></span>
                    {{ isRefreshLoading(index) ? '刷新中' : '刷新' }}
                  </button>
                  <button class="mini danger-inline" :disabled="batchGeneratingFrames || batchGeneratingVideos" @click="deleteShotRow(index)">
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-inline">暂无镜头，点击新增镜头开始。</div>
      </section>
    </div>

    <div v-if="editDialogVisible" class="dialog-mask" @click.self="closeEditShotDialog">
      <div class="dialog-card">
        <div class="dialog-head">
          <h4>编辑镜头</h4>
          <span>SHOT {{ String(editingShotIndex + 1).padStart(2, '0') }}</span>
        </div>
        <div class="dialog-body">
          <div class="dialog-grid">
            <div class="form-group">
              <label>标题</label>
              <input v-model="editingShotDraft.title" type="text" placeholder="镜头标题" />
            </div>
            <div class="form-group">
              <label>时长</label>
              <input v-model="editingShotDraft.duration" type="text" placeholder="例如 5s" />
            </div>
            <div class="form-group full-width">
              <div class="field-label-row">
                <label>Shot Plan 提示词</label>
                <button
                  class="mini ghost"
                  type="button"
                  :disabled="shotPromptEnhancing"
                  @click="enhanceEditingShotPrompt"
                >
                  {{ shotPromptEnhancing ? '增强中...' : '增强提示词' }}
                </button>
              </div>
              <textarea
                v-model="editingShotDraft.shotPrompt"
                rows="7"
                placeholder="填写该镜头的提示词（用于前后帧生成）"
              ></textarea>
            </div>
            <div class="form-group full-width">
              <div class="field-label-row">
                <label>旁白文案</label>
                <button
                  class="mini ghost"
                  type="button"
                  :disabled="voiceoverGenerating"
                  @click="generateEditingShotVoiceover"
                >
                  {{ voiceoverGenerating ? '生成中...' : 'AI生成旁白' }}
                </button>
              </div>
              <textarea
                v-model="editingShotDraft.voiceoverText"
                rows="4"
                placeholder="可选：填写该镜头旁白，用于视频上下文与导出文案"
              ></textarea>
            </div>
            <div class="form-group">
              <label>起始帧 URL</label>
              <input v-model="editingShotDraft.startFrameImageUrl" type="text" placeholder="https://..." />
            </div>
            <div class="form-group">
              <label>结束帧 URL</label>
              <input v-model="editingShotDraft.endFrameImageUrl" type="text" placeholder="https://..." />
            </div>
            <div class="form-group">
              <label>起始帧描述</label>
              <textarea v-model="editingShotDraft.startFrameDescription" rows="3" placeholder="起始帧内容描述"></textarea>
            </div>
            <div class="form-group">
              <label>结束帧描述</label>
              <textarea v-model="editingShotDraft.endFrameDescription" rows="3" placeholder="结束帧内容描述"></textarea>
            </div>
            <div class="form-group full-width">
              <label>起始帧提示词</label>
              <textarea
                v-model="editingShotDraft.startFramePrompt"
                rows="4"
                placeholder="用于起始帧生成；点击上方增强按钮会一起增强"
              ></textarea>
            </div>
            <div class="form-group full-width">
              <label>结束帧提示词</label>
              <textarea
                v-model="editingShotDraft.endFramePrompt"
                rows="4"
                placeholder="用于结束帧生成；点击上方增强按钮会一起增强"
              ></textarea>
            </div>
            <div class="binding-card full-width">
              <div class="binding-head">
                <label>角色资产绑定</label>
                <span>已绑定 {{ editBoundCharacterNames.length }} 个</span>
              </div>
              <div class="binding-toolbar">
                <button class="mini" type="button" @click="bindAllCharactersForEdit">全选角色</button>
                <button class="mini ghost" type="button" @click="clearCharactersForEdit">清空角色</button>
              </div>
              <div v-if="characterAssets.length" class="binding-grid">
                <label
                  v-for="(asset, idx) in characterAssets"
                  :key="`edit-character-${String(asset?.id || idx)}`"
                  class="binding-item"
                >
                  <input
                    type="checkbox"
                    :checked="isCharacterBoundInEdit(asset)"
                    @change="toggleCharacterBindingInEdit(asset)"
                  />
                  <span class="binding-name">{{ asset?.name || `角色${idx + 1}` }}</span>
                  <span class="binding-meta">{{ asset?.id || '-' }}</span>
                </label>
              </div>
              <div v-else class="empty-inline">暂无角色资产，请先在资产阶段生成角色。</div>
            </div>

            <div class="binding-card full-width">
              <div class="binding-head">
                <label>场景资产绑定</label>
                <span>已绑定 {{ editBoundSceneNames.length }} 个</span>
              </div>
              <div class="binding-toolbar">
                <button class="mini" type="button" @click="bindAllScenesForEdit">全选场景</button>
                <button class="mini ghost" type="button" @click="clearScenesForEdit">清空场景</button>
              </div>
              <div v-if="sceneAssets.length" class="binding-grid">
                <label
                  v-for="(asset, idx) in sceneAssets"
                  :key="`edit-scene-${String(asset?.id || idx)}`"
                  class="binding-item"
                >
                  <input
                    type="checkbox"
                    :checked="isSceneBoundInEdit(asset)"
                    @change="toggleSceneBindingInEdit(asset)"
                  />
                  <span class="binding-name">{{ asset?.name || `场景${idx + 1}` }}</span>
                  <span class="binding-meta">{{ asset?.id || '-' }}</span>
                </label>
              </div>
              <div v-else class="empty-inline">暂无场景资产，请先在资产阶段生成场景。</div>
            </div>
          </div>
        </div>
        <div class="dialog-actions">
          <button class="ghost" @click="closeEditShotDialog">取消</button>
          <button @click="saveEditShotDialog">保存</button>
        </div>
      </div>
    </div>

    <div v-if="deleteConfirmVisible" class="dialog-mask" @click.self="cancelDeleteShotDialog">
      <div class="dialog-card confirm-card">
        <div class="dialog-head">
          <h4>确认删除</h4>
        </div>
        <div class="confirm-body">
          确认删除镜头「{{ pendingDeleteShotTitle }}」吗？删除后不可恢复。
        </div>
        <div class="dialog-actions">
          <button class="ghost" @click="cancelDeleteShotDialog">取消</button>
          <button class="danger-inline" @click="confirmDeleteShotDialog">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DirectorWorkbench',
  props: {
    assets: { type: Array, default: () => [] },
    shots: { type: Array, default: () => [] },
    storyboardScenes: { type: Array, default: () => [] },
    videoProvider: { type: String, default: 'openai' },
    currentEpisodeNo: { type: Number, default: 1 },
    workflowStage: { type: String, default: 'director-workbench' }
  },
  data() {
    return {
      localShots: [],
      selectedShotIndex: -1,
      videoMode: 'keyframe-interpolation',
      videoRatio: '16:9',
      generateAudio: true,
      watermark: false,
      testSegmentMode: false,
      loading: false,
      taskRefreshing: false,
      rowStartFrameLoading: {},
      rowEndFrameLoading: {},
      rowVideoLoading: {},
      rowRefreshLoading: {},
      batchGeneratingFrames: false,
      batchGeneratingVideos: false,
      batchStatusText: '',
      batchProgressPercent: 0,
      batchProgressDone: 0,
      batchProgressTotal: 0,
      hasAutoImportedScenes: false,
      editDialogVisible: false,
      shotPromptEnhancing: false,
      voiceoverGenerating: false,
      editingShotIndex: -1,
      editingShotDraft: {
        title: '',
        duration: '5s',
        sceneNarrative: '',
        shotPrompt: '',
        voiceoverText: '',
        startFrameImageUrl: '',
        endFrameImageUrl: '',
        startFrameDescription: '',
        endFrameDescription: '',
        startFramePrompt: '',
        endFramePrompt: '',
        boundCharacterAssetIds: [],
        boundCharacterNames: [],
        boundSceneAssetIds: [],
        boundSceneNames: []
      },
      deleteConfirmVisible: false,
      pendingDeleteIndex: -1
    };
  },
  computed: {
    isCombinedStage() {
      return this.workflowStage === 'director-workbench';
    },
    isKeyframeStage() {
      return this.isCombinedStage || this.workflowStage === 'keyframes';
    },
    isVideoStage() {
      return this.isCombinedStage || this.workflowStage === 'veo-video';
    },
    stageTitle() {
      if (this.isCombinedStage) return '导演工作台';
      return this.workflowStage === 'veo-video' ? 'Veo视频生成' : '关键帧生成';
    },
    stageSummary() {
      if (this.isCombinedStage) return '镜头资产绑定、关键帧与视频生成';
      return this.workflowStage === 'veo-video' ? '关键帧确认后提交视频任务' : '按镜头生成起始帧与结束帧';
    },
    stageTagline() {
      if (this.isCombinedStage) return '一站式镜头生成';
      return this.workflowStage === 'veo-video' ? '视频任务阶段' : '关键帧阶段';
    },
    workflowDescription() {
      if (this.isCombinedStage) {
        return '在一个页面完成镜头草稿导入、角色/场景资产绑定、前后关键帧生成和视频任务提交。';
      }
      return this.workflowStage === 'veo-video'
        ? '本阶段只负责把已确认的关键帧提交到 Veo 视频模型，重点检查时长、画幅和视频状态。'
        : '本阶段只负责镜头级关键帧。先绑定角色与场景资产，再生成起始帧和结束帧。';
    },
    currentShot() {
      if (this.selectedShotIndex < 0 || this.selectedShotIndex >= this.localShots.length) return null;
      return this.localShots[this.selectedShotIndex];
    },
    parsedScenes() {
      const scenes = Array.isArray(this.storyboardScenes) ? [...this.storyboardScenes] : [];
      return scenes.sort((a, b) => this.sceneNoFromScene(a, 0) - this.sceneNoFromScene(b, 0));
    },
    characterAssets() {
      return (Array.isArray(this.assets) ? this.assets : []).filter((item) => this.assetKindOf(item) === 'character');
    },
    sceneAssets() {
      return (Array.isArray(this.assets) ? this.assets : []).filter((item) => this.assetKindOf(item) === 'scene');
    },
    hasStartFrameImage() {
      return this.isUsableImageUrl(this.currentShot?.startFrame?.image_url);
    },
    currentTaskProgress() {
      const value = Number(this.currentShot?.videoTask?.progress);
      return Number.isFinite(value) ? Math.max(0, Math.min(100, Math.round(value))) : 0;
    },
    showTaskProgress() {
      const status = this.normalizeTaskStatus(this.currentShot?.videoTask?.status, {
        hasVideo: Boolean(this.currentShot?.videoUrl),
        hasTaskId: Boolean(this.currentShot?.videoTask?.taskId)
      });
      return ['submitting', 'submitted', 'processing', 'succeeded', 'failed'].includes(status);
    },
    hasNextShot() {
      return this.selectedShotIndex >= 0 && this.selectedShotIndex < this.localShots.length - 1;
    },
    currentShotHasExplicitCharacterBindings() {
      return this.hasExplicitCharacterBindings(this.currentShot);
    },
    currentShotBoundCharacterNames() {
      return this.resolveBoundCharacterAssetsForShot(this.currentShot).map((item, idx) => String(item?.name || `角色${idx + 1}`).trim()).filter(Boolean);
    },
    currentShotHasExplicitSceneBindings() {
      return this.hasExplicitSceneBindings(this.currentShot);
    },
    currentShotBoundSceneNames() {
      return this.resolveBoundSceneAssetsForShot(this.currentShot).map((item, idx) => String(item?.name || `场景${idx + 1}`).trim()).filter(Boolean);
    },
    pendingDeleteShotTitle() {
      if (this.pendingDeleteIndex < 0 || this.pendingDeleteIndex >= this.localShots.length) return '';
      const target = this.localShots[this.pendingDeleteIndex];
      return String(target?.title || `#${this.pendingDeleteIndex + 1}`).trim();
    },
    editBoundCharacterNames() {
      const ids = this.normalizeStringArray(this.editingShotDraft?.boundCharacterAssetIds);
      const names = this.resolveAssetNamesByIds(ids, this.characterAssets, this.editingShotDraft?.boundCharacterNames || []);
      return names;
    },
    editBoundSceneNames() {
      const ids = this.normalizeStringArray(this.editingShotDraft?.boundSceneAssetIds);
      const names = this.resolveAssetNamesByIds(ids, this.sceneAssets, this.editingShotDraft?.boundSceneNames || []);
      return names;
    }
  },
  watch: {
    shots: {
      deep: true,
      handler(newVal) {
        const next = Array.isArray(newVal) ? newVal : [];
        this.localShots = this.dedupeShots(JSON.parse(JSON.stringify(next)));
        if (this.localShots.length) {
          this.hasAutoImportedScenes = true;
          if (this.selectedShotIndex < 0) this.selectedShotIndex = 0;
          else this.selectedShotIndex = Math.min(this.selectedShotIndex, this.localShots.length - 1);
          return;
        }

        if (this.autoImportShotsFromStoryboardIfNeeded({ emit: true })) return;
        this.selectedShotIndex = -1;
      }
    },
    storyboardScenes: {
      deep: true,
      handler() {
        if (this.localShots.length) return;
        this.autoImportShotsFromStoryboardIfNeeded({ emit: true });
      }
    },
    currentEpisodeNo() {
      this.hasAutoImportedScenes = false;
      if (!this.localShots.length) {
        this.autoImportShotsFromStoryboardIfNeeded({ emit: true });
      }
    },
    assets: {
      deep: true,
      handler() {
        this.pruneShotAssetBindings();
      }
    },
    'currentShot.videoUrl': function (newVal, oldVal) {
      if (newVal && newVal !== oldVal) this.autoPlayCurrentVideo();
    }
  },
  mounted() {
    if (this.shots && this.shots.length > 0) {
      this.localShots = this.dedupeShots(JSON.parse(JSON.stringify(this.shots)));
      this.selectedShotIndex = 0;
      this.hasAutoImportedScenes = true;
    } else {
      const imported = this.autoImportShotsFromStoryboardIfNeeded({ emit: true });
      if (!imported) {
        this.localShots = [];
        this.selectedShotIndex = -1;
      }
    }
  },
  methods: {
    autoImportShotsFromStoryboardIfNeeded({ emit = false, force = false } = {}) {
      if (!force) {
        if (this.hasAutoImportedScenes) return false;
        if (this.localShots.length) return false;
      }
      if (!this.parsedScenes.length) return false;

      const imported = this.parsedScenes
        .reduce((acc, scene, index) => acc.concat(this.shotsFromScene(scene, index)), []);
      const deduped = this.dedupeShots(imported);

      if (!deduped.length) return false;
      this.localShots = deduped;
      this.selectedShotIndex = 0;
      this.hasAutoImportedScenes = true;
      if (emit) this.emitShots();
      return true;
    },
    sceneNoFromValue(value, fallback = 0) {
      const text = String(value || '').trim();
      if (!text) return fallback;
      const match = text.match(/(\d+)/);
      if (!match) return fallback;
      const no = Number(match[1]);
      return Number.isFinite(no) ? no : fallback;
    },
    sceneNoFromScene(scene, fallback = 0) {
      if (scene && scene.scene_id !== undefined && scene.scene_id !== null) {
        return this.sceneNoFromValue(scene.scene_id, fallback);
      }
      return fallback;
    },
    sceneNoFromShot(shot, fallback = 0) {
      if (shot && shot.sceneNo !== undefined && shot.sceneNo !== null) {
        return this.sceneNoFromValue(shot.sceneNo, fallback);
      }
      return this.sceneNoFromValue(shot?.title, fallback);
    },
    normalizeStringArray(value) {
      if (!Array.isArray(value)) return [];
      return [...new Set(value.map((item) => String(item || '').trim()).filter(Boolean))];
    },
    normalizeVideoTail(value, fallbackFrameUrl = '') {
      const safe = value && typeof value === 'object' ? value : {};
      const frameCandidate = this.normalizeImageUrl(
        safe.last_frame_url || safe.lastFrameUrl || fallbackFrameUrl
      );
      const tailSecondsRaw = Number(safe.tail_seconds ?? safe.tailSeconds ?? 0.5);
      const overlapRaw = Number(safe.overlap_seconds ?? safe.overlapSeconds ?? 0.5);
      const tailSeconds = Number.isFinite(tailSecondsRaw)
        ? Math.max(0.1, Math.min(2, tailSecondsRaw))
        : 0.5;
      const overlapSeconds = Number.isFinite(overlapRaw)
        ? Math.max(0.3, Math.min(0.7, overlapRaw))
        : 0.5;
      return {
        tail_seconds: Number(tailSeconds.toFixed(2)),
        overlap_seconds: Number(overlapSeconds.toFixed(2)),
        last_frame_url: frameCandidate,
        source: String(safe.source || 'end_frame').trim() || 'end_frame',
        transition: String(safe.transition || 'crossfade').trim() || 'crossfade'
      };
    },
    normalizeCharacterBindingList(value) {
      if (!Array.isArray(value)) return [];
      const normalized = [];
      const seen = new Set();
      value.forEach((item) => {
        if (!item || typeof item !== 'object') return;
        const characterName = String(item.character_name || item.characterName || item.name || '').trim();
        const assetId = String(item.asset_id || item.assetId || item.id || '').trim();
        if (!characterName && !assetId) return;
        const key = `${characterName}::${assetId}`;
        if (seen.has(key)) return;
        seen.add(key);
        normalized.push({
          character_name: characterName,
          asset_id: assetId
        });
      });
      return normalized;
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
      const promptText = [
        safe.name,
        safe.prompt,
        safe.source_description
      ].map((item) => String(item || '').trim().toLowerCase()).join(' ');

      if (
        /character|角色|瑙掕壊/.test(typeText) ||
        /角色|瑙掕壊/.test(promptText) ||
        String(safe.wardrobe || '').trim()
      ) {
        return 'character';
      }
      if (
        /scene|场景|鍦烘櫙/.test(typeText) ||
        /场景|鍦烘櫙|环境/.test(promptText)
      ) {
        return 'scene';
      }
      return '';
    },
    formatShotPlanItem(item, index = 0) {
      if (!item || typeof item !== 'object') return String(item || '').trim();
      const beatId = String(item.beat_id || item.id || index + 1).trim();
      const shotType = String(item.shot_type || item.lens || item.framing || '').trim();
      const cameraAngle = String(item.camera_angle || item.angle || '').trim();
      const cameraMovement = String(item.camera_movement || item.movement || '').trim();
      const blocking = String(item.blocking || item.beat || item.description || item.action || '').trim();
      const dialogue = String(item.dialogue || item.line || '').trim();
      const duration = String(item.duration || '').trim();

      const lensPart = [shotType, cameraAngle, cameraMovement].filter(Boolean).join(' / ');
      let line = `${beatId}. ${lensPart ? `${lensPart}：` : ''}${blocking || '镜头推进'}`;
      if (dialogue) line += ` | 台词:${dialogue}`;
      if (duration) line += ` | ${duration}`;
      return line;
    },
    buildSceneShotDeployment(scene) {
      const explicitNotes = String(scene?.staging_notes || scene?.shot_deployment || '').trim();
      if (explicitNotes) return explicitNotes;
      const plan = Array.isArray(scene?.shot_plan) ? scene.shot_plan : [];
      if (!plan.length) return '';
      return plan
        .slice(0, 6)
        .map((item, index) => this.formatShotPlanItem(item, index))
        .filter(Boolean)
        .join('\n');
    },
    buildSceneActionDetails(scene) {
      const explicit = String(scene?.action_details || scene?.actionDetails || '').trim();
      if (explicit) return explicit;
      const actions = Array.isArray(scene?.character_actions) ? scene.character_actions : [];
      if (!actions.length) return '';
      return actions
        .map((item) => String(item || '').trim())
        .filter(Boolean)
        .join('\n');
    },
    formatDialogueBeatItem(item, index = 0) {
      if (!item || typeof item !== 'object') return String(item || '').trim();
      const beatId = String(item.beat_id || item.id || index + 1).trim();
      const speaker = String(item.speaker || item.role || `角色${index + 1}`).trim();
      const line = String(item.line || item.dialogue || item.text || '').trim();
      const tone = String(item.tone || item.emotion || '').trim();
      const reaction = String(item.reaction || item.listener_reaction || '').trim();
      const parts = [];
      if (speaker || line) parts.push(`${speaker}${line ? `：${line}` : ''}`);
      if (tone) parts.push(`语气:${tone}`);
      if (reaction) parts.push(`反应:${reaction}`);
      const content = parts.join(' | ').trim();
      return content ? `${beatId}. ${content}` : '';
    },
    buildSceneDialogueBeatDetails(scene) {
      const explicit = String(scene?.dialogue_beat_details || scene?.dialogueBeatDetails || '').trim();
      if (explicit) return explicit;
      const beats = Array.isArray(scene?.dialogue_beats) ? scene.dialogue_beats : [];
      if (!beats.length) return '';
      return beats
        .slice(0, 6)
        .map((item, index) => this.formatDialogueBeatItem(item, index))
        .filter(Boolean)
        .join('\n');
    },
    normalizeArcLines(value, maxItems = 4) {
      if (Array.isArray(value)) {
        return value
          .map((item) => String(item || '').trim())
          .filter(Boolean)
          .slice(0, maxItems);
      }
      const text = String(value || '').trim();
      if (!text) return [];
      return text
        .split(/\r?\n|；|;/)
        .map((item) => String(item || '').replace(/^\d+\s*[\.、\)]\s*/, '').trim())
        .filter(Boolean)
        .slice(0, maxItems);
    },
    resolveShotMotionInstruction(shot = {}) {
      const safe = shot || {};
      const explicit = String(
        safe.motionInstruction ||
        safe.motion_instruction ||
        safe.action_instruction ||
        safe.Action ||
        safe.action ||
        ''
      ).trim();
      if (explicit) return explicit;

      const actionArc = this.normalizeArcLines(safe.actionArc || safe.action_arc || safe.character_actions, 3);
      if (actionArc.length) return actionArc.join('；');

      return String(safe.actionDetails || safe.action_details || '').trim();
    },
    resolveShotTargetState(shot = {}) {
      const safe = shot || {};
      return String(
        safe.targetState ||
        safe.target_state ||
        safe.endFrameGoal ||
        safe.end_frame_goal ||
        safe.EndFrame ||
        safe.end_frame ||
        ''
      ).trim();
    },
    resolveShotPrevState(shot = {}) {
      const safe = shot || {};
      return String(
        safe.prevState ||
        safe.prev_state ||
        safe.previous_state ||
        safe.startFrameGoal ||
        safe.start_frame_goal ||
        safe.startFrame?.description ||
        '承接上一镜头同场景基础状态'
      ).trim();
    },
    resolveShotVisualAnchor(shot = {}) {
      const safe = shot || {};
      return String(
        safe.visualAnchor ||
        safe.visual_anchor ||
        ''
      ).trim();
    },
    resolveShotContinuityHint(shot = {}) {
      const safe = shot || {};
      return String(
        safe.continuityHint ||
        safe.continuity_hint ||
        ''
      ).trim();
    },
    compactNarrativeText(text = '') {
      return String(text || '')
        .replace(/\r/g, '\n')
        .replace(/\u3000/g, ' ')
        .replace(/\n+/g, '，')
        .replace(/，+/g, '，')
        .replace(/；+/g, '；')
        .replace(/。+/g, '。')
        .replace(/\s+/g, ' ')
        .trim();
    },
    stripNarrativeWrappers(text = '') {
      let value = this.compactNarrativeText(text);
      if (!value) return '';

      const wrappers = [
        /^承接\s*[“"']?/,
        /^延续\s*[“"']?/,
        /^继承\s*[“"']?/,
        /^同一空间锚点\s*[：:]\s*/,
        /^当前镜头状态收束\s*[：:]\s*/,
        /^状态继承基线\s*[：:]\s*/,
        /^继承状态\s*[：:]\s*/,
        /^动作推导\s*[：:]\s*/,
        /^目标状态锚点\s*[：:]\s*/,
        /^起始画面锚点\s*[：:]\s*/,
        /^下一镜头变化方向\s*[：:]\s*/,
        /^空间连续\s*[：:]\s*/,
        /^物理连续\s*[：:]\s*/
      ];

      let previous = '';
      while (value && value !== previous) {
        previous = value;
        wrappers.forEach((pattern) => {
          value = value.replace(pattern, '').trim();
        });
        value = value
          .replace(/^[“"']+/, '')
          .replace(/[”"']+$/, '')
          .replace(/^[，。；;:：\s]+/, '')
          .replace(/[，。；;:：\s]+$/, '')
          .trim();
      }
      return value;
    },
    summarizeNarrativeSnippet(text = '', maxLength = 42) {
      const value = this.stripNarrativeWrappers(text);
      if (!value) return '';
      return value.length > maxLength ? value.slice(0, maxLength) : value;
    },
    splitNarrativeSegments(text = '', separatorPattern = /[。；;\n]/) {
      return String(text || '')
        .replace(/\r/g, '\n')
        .split(separatorPattern)
        .map((item) => this.compactNarrativeText(item))
        .filter(Boolean);
    },
    ensureMotionInstructionFromPrevState(prevState = '', motionInstruction = '') {
      const prev = this.summarizeNarrativeSnippet(prevState, 24);
      let motion = this.compactNarrativeText(motionInstruction);
      if (!motion) {
        if (prev) return `承接“${prev.slice(0, 24)}”，重心前移并触发下一步动作。`;
        return '主体动作持续推进并保持物理连续。';
      }
      motion = motion
        .replace(/已经走完/g, '重心前移，脚抬起并准备落步')
        .replace(/走完/g, '重心前移，脚抬起并准备落步')
        .replace(/已经完成/g, '动作持续推进中')
        .replace(/完成动作/g, '动作持续推进中')
        .replace(/已经结束/g, '动作进入收束阶段');
      motion = this.stripNarrativeWrappers(motion);
      if (prev) {
        const anchor = this.summarizeNarrativeSnippet(prev, 20);
        if (anchor) {
          motion = `承接“${anchor}”，${motion}`;
        }
      }
      return this.compactNarrativeText(motion);
    },
    inferSpatialAnchor(text = '') {
      return String(text || '')
        .split(/[，。；\n]/)
        .map((item) => String(item || '').trim())
        .find((item) => item) || '';
    },
    ensureVisualAnchorWithPrevState(visualAnchor = '', prevState = '', targetState = '', sourceDescription = '') {
      const parts = this.splitNarrativeSegments(visualAnchor, /[；;\n]/);
      const pushUnique = (segment) => {
        const text = this.compactNarrativeText(segment);
        if (!text) return;
        const key = text.toLowerCase();
        if (parts.some((item) => this.compactNarrativeText(item).toLowerCase() === key)) return;
        parts.push(text);
      };
      const prev = this.summarizeNarrativeSnippet(prevState, 42);
      const target = this.summarizeNarrativeSnippet(targetState, 42);
      const space = this.summarizeNarrativeSnippet(this.inferSpatialAnchor(sourceDescription), 42);
      if (space) pushUnique(`同一空间锚点：${space}`);
      if (prev) pushUnique(`承接上一镜头目标状态：${prev}`);
      if (target) pushUnique(`当前镜头状态收束：${target}`);
      return parts.join('；').replace(/；+/g, '；').trim();
    },
    ensureContinuityHint(continuityHint = '', targetState = '', prevState = '', sourceDescription = '') {
      const parts = this.splitNarrativeSegments(continuityHint, /[。；;\n]/);
      const hasSegment = (needle) => parts.some((item) => this.compactNarrativeText(item).includes(needle));
      const pushUnique = (segment) => {
        const text = this.compactNarrativeText(segment);
        if (!text) return;
        if (parts.some((item) => this.compactNarrativeText(item).toLowerCase() === text.toLowerCase())) return;
        parts.push(text);
      };
      const target = this.summarizeNarrativeSnippet(targetState, 34);
      const prev = this.summarizeNarrativeSnippet(prevState, 30);
      const space = this.summarizeNarrativeSnippet(this.inferSpatialAnchor(sourceDescription), 24);

      if (!parts.length) {
        const direction = target || '动作能量持续推进后收束';
        pushUnique(`下一镜头变化方向：继承当前状态并沿“${direction.slice(0, 34)}”继续演化`);
      }

      if (!hasSegment('下一镜头变化方向')) {
        const direction = target || '动作能量持续推进后收束';
        pushUnique(`下一镜头变化方向：沿“${direction.slice(0, 34)}”继续演化`);
      }
      if (!hasSegment('空间连续')) {
        pushUnique(`空间连续：保持同一地点（${space || '当前场景'}），仅允许机位或景别平滑变化`);
      }
      if (!hasSegment('物理连续') && !hasSegment('过渡')) {
        pushUnique('物理连续：风场、能量、姿态变化必须有过渡，禁止突变');
      }
      if (prev && !hasSegment('状态继承基线') && !hasSegment('继承')) {
        pushUnique(`状态继承基线：${prev}`);
      }

      return parts
        .filter(Boolean)
        .join('。')
        .replace(/。+/g, '。')
        .replace(/。$/, '')
        .concat('。');
    },
    ensureGradualTargetState(targetState = '', motionInstruction = '') {
      let text = this.compactNarrativeText(targetState);
      const motion = this.summarizeNarrativeSnippet(motionInstruction, 28);
      if (!text) {
        return motion
          ? `承接“${motion.slice(0, 28)}”，动作幅度逐渐减弱并稳定，环境反馈缓慢收束。`
          : '';
      }

      const replacements = [
        [/突然静止/g, '动作幅度逐渐减弱并趋于稳定'],
        [/瞬间静止/g, '动作幅度逐渐减弱并趋于稳定'],
        [/突然爆炸/g, '能量持续抬升后向外扩散'],
        [/瞬间爆炸/g, '能量持续抬升后向外扩散'],
        [/突然/g, '逐渐'],
        [/瞬间/g, '逐步'],
        [/立刻/g, '随动作推进'],
        [/马上/g, '随动作推进']
      ];
      replacements.forEach(([pattern, nextText]) => {
        text = text.replace(pattern, nextText);
      });

      if (!/(逐渐|逐步|缓慢|持续|收束|趋于|回落)/.test(text)) {
        text = `${text}，并逐渐收束到稳定状态`;
      }

      text = this.stripNarrativeWrappers(text);
      if (motion) {
        const anchor = this.summarizeNarrativeSnippet(motion, 20);
        if (anchor) text = `承接“${anchor}”，${text}`;
      }

      return this.compactNarrativeText(text);
    },
    buildSceneNarrativeFromFields({
      sourceDescription = '',
      shotSummary = '',
      detailedShotDescription = '',
      detailedPlot = '',
      actionArc = [],
      emotionArc = [],
      rhythmPlan = '',
      startFrameGoal = '',
      prevState = '',
      motionInstruction = '',
      targetState = '',
      visualAnchor = '',
      continuityHint = '',
      endFrameGoal = '' // legacy fallback
    } = {}) {
      const lines = [];
      const source = String(sourceDescription || '').trim();
      const summary = String(shotSummary || '').trim();
      const detailed = String(detailedShotDescription || '').trim();
      const plot = String(detailedPlot || '').trim();
      const rhythm = String(rhythmPlan || '').trim();
      const startGoal = String(startFrameGoal || '').trim();
      const prev = String(prevState || startGoal || '承接上一镜头同场景基础状态').trim();
      const actionInstruction = this.ensureMotionInstructionFromPrevState(prev, String(motionInstruction || '').trim());
      const target = this.ensureGradualTargetState(
        String(targetState || endFrameGoal || '').trim(),
        actionInstruction
      );
      const anchor = this.ensureVisualAnchorWithPrevState(visualAnchor, prev, target, source);
      const continuity = this.ensureContinuityHint(continuityHint, target, prev, source);
      const actionLines = this.normalizeArcLines(actionArc, 4);
      const emotionLines = this.normalizeArcLines(emotionArc, 4);

      if (source) lines.push(`场次剧情：${source}`);
      if (summary) lines.push(`镜头概述：${summary}`);
      if (detailed) lines.push(`详细分镜：${detailed}`);
      if (actionLines.length) lines.push(`动作节拍：${actionLines.map((item, idx) => `${idx + 1}. ${item}`).join('；')}`);
      if (prev) lines.push(`上一状态：${prev}`);
      if (actionInstruction) lines.push(`动作指令：${actionInstruction}`);
      if (emotionLines.length) lines.push(`情绪节拍：${emotionLines.map((item, idx) => `${idx + 1}. ${item}`).join('；')}`);
      if (rhythm) lines.push(`节奏设计：${rhythm}`);
      if (startGoal) lines.push(`起始帧目标：${startGoal}`);
      if (target) lines.push(`目标状态：${target}`);
      if (anchor) lines.push(`视觉锚点：${anchor}`);
      if (continuity) lines.push(`连续性提示：${continuity}`);
      if (plot) lines.push(`详细剧情：\n${plot}`);
      return lines.join('\n').trim();
    },
    parseSceneNarrative(text, fallback = {}) {
      const raw = String(text || '').trim();
      const defaults = {
        sourceDescription: String(fallback.sourceDescription || '').trim(),
        shotSummary: String(fallback.shotSummary || '').trim(),
        detailedShotDescription: String(fallback.detailedShotDescription || '').trim(),
        detailedPlot: String(fallback.detailedPlot || '').trim(),
        actionArc: this.normalizeArcLines(fallback.actionArc || [], 4),
        emotionArc: this.normalizeArcLines(fallback.emotionArc || [], 4),
        rhythmPlan: String(fallback.rhythmPlan || '').trim(),
        startFrameGoal: String(fallback.startFrameGoal || '').trim(),
        prevState: String(
          fallback.prevState ||
          fallback.prev_state ||
          fallback.previous_state ||
          fallback.startFrameGoal ||
          '承接上一镜头同场景基础状态'
        ).trim(),
        motionInstruction: String(
          fallback.motionInstruction ||
          fallback.motion_instruction ||
          ''
        ).trim(),
        targetState: String(
          fallback.targetState ||
          fallback.target_state ||
          fallback.endFrameGoal ||
          fallback.end_frame_goal ||
          ''
        ).trim(),
        visualAnchor: String(
          fallback.visualAnchor ||
          fallback.visual_anchor ||
          ''
        ).trim(),
        continuityHint: String(
          fallback.continuityHint ||
          fallback.continuity_hint ||
          ''
        ).trim(),
        endFrameGoal: String(
          fallback.targetState ||
          fallback.target_state ||
          fallback.endFrameGoal ||
          fallback.end_frame_goal ||
          ''
        ).trim()
      };
      if (!raw) return defaults;

      const normalized = raw.replace(/\r/g, '\n');
      const labels = [
        ['sourceDescription', '场次剧情'],
        ['shotSummary', '镜头概述'],
        ['detailedShotDescription', '详细分镜'],
        ['actionArc', '动作节拍'],
        ['motionInstruction', '动作指令'],
        ['emotionArc', '情绪节拍'],
        ['rhythmPlan', '节奏设计'],
        ['startFrameGoal', '起始帧目标'],
        ['prevState', '上一状态'],
        ['targetState', '目标状态'],
        ['visualAnchor', '视觉锚点'],
        ['continuityHint', '连续性提示'],
        ['legacyEndFrameGoal', '结束帧目标'],
        ['detailedPlot', '详细剧情']
      ];
      const labelPattern = labels.map((item) => item[1]).join('|');
      const extracted = {};
      labels.forEach(([key, label]) => {
        const pattern = new RegExp(`(?:^|\\n)${label}\\s*[：:]\\s*([\\s\\S]*?)(?=\\n(?:${labelPattern})\\s*[：:]|$)`, 'm');
        const match = normalized.match(pattern);
        if (match && match[1]) extracted[key] = String(match[1]).trim();
      });

      const lines = normalized.split('\n').map((item) => String(item || '').trim()).filter(Boolean);
      const firstLine = lines[0] || '';

      const sourceDescription = String(extracted.sourceDescription || defaults.sourceDescription || firstLine).trim();
      const shotSummary = String(extracted.shotSummary || defaults.shotSummary || sourceDescription).trim();
      const detailedShotDescription = String(
        extracted.detailedShotDescription || defaults.detailedShotDescription || shotSummary || sourceDescription
      ).trim();

      const actionArc = this.normalizeArcLines(extracted.actionArc || defaults.actionArc, 4);
      const emotionArc = this.normalizeArcLines(extracted.emotionArc || defaults.emotionArc, 4);
      const rhythmPlan = String(extracted.rhythmPlan || defaults.rhythmPlan).trim();
      const startFrameGoal = String(extracted.startFrameGoal || defaults.startFrameGoal).trim();
      const prevState = String(
        extracted.prevState ||
        defaults.prevState ||
        startFrameGoal ||
        '承接上一镜头同场景基础状态'
      ).trim();
      const motionInstruction = this.ensureMotionInstructionFromPrevState(
        prevState,
        String(
        extracted.motionInstruction || defaults.motionInstruction || (actionArc[0] || '')
        ).trim()
      );
      const targetState = this.ensureGradualTargetState(
        String(
          extracted.targetState ||
          extracted.legacyEndFrameGoal ||
          defaults.targetState
        ).trim(),
        motionInstruction
      );
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        String(extracted.visualAnchor || defaults.visualAnchor).trim(),
        prevState,
        targetState,
        sourceDescription
      );
      const continuityHint = this.ensureContinuityHint(
        String(extracted.continuityHint || defaults.continuityHint).trim(),
        targetState,
        prevState,
        sourceDescription
      );

      let detailedPlot = String(extracted.detailedPlot || '').trim();
      if (!detailedPlot) {
        if (raw.includes('详细剧情：') || raw.includes('详细剧情:')) {
          detailedPlot = raw.split(/详细剧情[:：]/).slice(1).join('详细剧情：').trim();
        } else {
          detailedPlot = String(defaults.detailedPlot || '').trim();
        }
      }
      if (!detailedPlot && lines.length > 1) {
        detailedPlot = lines.slice(1).join('\n').trim();
      }

      return {
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        detailedPlot,
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        prevState,
        motionInstruction,
        targetState,
        visualAnchor,
        continuityHint,
        endFrameGoal: targetState // legacy alias
      };
    },
    buildDetailedPlotFromFields({ detailedPlot = '', shotDeployment = '', actionDetails = '', dialogueDetails = '', dialogueBeatDetails = '' } = {}) {
      const explicit = String(detailedPlot || '').trim();
      if (explicit) return explicit;

      const sections = [
        ['分镜调度', shotDeployment],
        ['动作细节', actionDetails],
        ['对白细节', dialogueDetails],
        ['对白节拍', dialogueBeatDetails]
      ];
      const merged = [];
      const seen = new Set();

      sections.forEach(([label, value]) => {
        const text = String(value || '').trim();
        if (!text) return;
        const key = text.replace(/\s+/g, ' ').toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        merged.push(`${label}：\n${text}`);
      });

      return merged.join('\n\n').trim();
    },
    getShotDetailedPlot(shot) {
      const safeShot = shot || {};
      const narrativeText = String(safeShot.sceneNarrative || safeShot.scene_narrative || safeShot.scene_script || '').trim();
      if (narrativeText) {
        const parsed = this.parseSceneNarrative(narrativeText, {
          sourceDescription: safeShot.sourceDescription || safeShot.source_description || safeShot.description,
          shotSummary: safeShot.shotSummary || safeShot.shot_summary || safeShot.shot_description,
          detailedShotDescription: safeShot.detailedShotDescription || safeShot.detailed_shot_description,
          detailedPlot: safeShot.detailedPlot || safeShot.detailed_plot,
          actionArc: safeShot.actionArc || safeShot.action_arc,
          emotionArc: safeShot.emotionArc || safeShot.emotion_arc,
          rhythmPlan: safeShot.rhythmPlan || safeShot.rhythm_plan,
          startFrameGoal: safeShot.startFrameGoal || safeShot.start_frame_goal,
          prevState: safeShot.prevState || safeShot.prev_state || safeShot.previous_state,
          motionInstruction: safeShot.motionInstruction || safeShot.motion_instruction,
          targetState: safeShot.targetState || safeShot.target_state || safeShot.endFrameGoal || safeShot.end_frame_goal,
          visualAnchor: safeShot.visualAnchor || safeShot.visual_anchor,
          continuityHint: safeShot.continuityHint || safeShot.continuity_hint
        });
        if (parsed.detailedPlot) return parsed.detailedPlot;
      }
      return this.buildDetailedPlotFromFields({
        detailedPlot: safeShot.detailedPlot || safeShot.detailed_plot,
        shotDeployment: safeShot.shotDeployment || safeShot.shot_deployment || safeShot.staging_notes,
        actionDetails: safeShot.actionDetails || safeShot.action_details || (Array.isArray(safeShot.character_actions) ? safeShot.character_actions.join('\n') : ''),
        dialogueDetails: safeShot.dialogueDetails || safeShot.dialogue_details || safeShot.dialogue,
        dialogueBeatDetails: safeShot.dialogueBeatDetails || safeShot.dialogue_beat_details
      });
    },
    buildSceneDetailedPlot(scene) {
      return this.buildDetailedPlotFromFields({
        detailedPlot: scene?.detailedPlot || scene?.detailed_plot,
        shotDeployment: this.buildSceneShotDeployment(scene),
        actionDetails: this.buildSceneActionDetails(scene),
        dialogueDetails: String(
          scene?.dialogue_details ||
          (Array.isArray(scene?.dialogue) ? scene.dialogue.join('；') : scene?.dialogue || '') ||
          scene?.dialogue_text ||
          ''
        ).trim(),
        dialogueBeatDetails: this.buildSceneDialogueBeatDetails(scene)
      });
    },
    findSceneDialogueBeat(scene, beatId = '', beatIndex = 0) {
      const beats = Array.isArray(scene?.dialogue_beats) ? scene.dialogue_beats : [];
      if (!beats.length) return null;

      const normalizedBeatId = String(beatId || '').trim();
      if (normalizedBeatId) {
        const matched = beats.find((item) => String(item?.beat_id || item?.id || '').trim() === normalizedBeatId);
        if (matched) return matched;
      }
      return beats[beatIndex] || null;
    },
    buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex = 0) {
      const safeBeat = beat && typeof beat === 'object' ? beat : {};
      const beatId = String(safeBeat.beat_id || safeBeat.id || beatIndex + 1).trim() || String(beatIndex + 1);
      const shotType = String(safeBeat.shot_type || safeBeat.lens || safeBeat.framing || '').trim();
      const cameraAngle = String(safeBeat.camera_angle || safeBeat.angle || '').trim();
      const cameraMovement = String(safeBeat.camera_movement || safeBeat.movement || '').trim();
      const blocking = String(safeBeat.blocking || safeBeat.beat || safeBeat.description || safeBeat.action || beat || '').trim();
      const dialogue = String(safeBeat.dialogue || safeBeat.line || '').trim();
      const transition = String(safeBeat.transition || '').trim();
      const duration = String(safeBeat.duration || '').trim();
      const sourceDescription = String(scene?.description || '').trim();
      const sceneShotSummary = String(scene?.shot_description || '').trim();
      const lensSummary = [shotType, cameraAngle, cameraMovement].filter(Boolean).join(' / ');
      const dialogueBeat = this.findSceneDialogueBeat(scene, beatId, beatIndex);
      const dialogueBeatLine = dialogueBeat
        ? this.formatDialogueBeatItem(dialogueBeat, beatIndex).replace(/^\d+\.\s*/, '').trim()
        : '';
      const sceneActionLine = Array.isArray(scene?.character_actions)
        ? String(scene.character_actions[beatIndex] || '').trim()
        : '';
      const shotDeployment = this.formatShotPlanItem(safeBeat, beatIndex) || [lensSummary, blocking].filter(Boolean).join('：');
      const actionDetails = [...new Set([blocking, sceneActionLine].filter(Boolean))].join('\n');
      const dialogueDetails = [...new Set([dialogue, dialogueBeatLine].filter(Boolean))].join('；');
      const dialogueBeatDetails = dialogueBeat
        ? this.formatDialogueBeatItem(dialogueBeat, beatIndex)
        : (dialogue ? `${beatId}. ${dialogue}` : '');
      const shotSummary = lensSummary || sceneShotSummary || `镜头 ${beatId}`;
      const detailedShotDescription = [
        shotSummary && `镜头设计：${shotSummary}`,
        blocking && `当前动作：${blocking}`,
        dialogue && `对白重点：${dialogue}`,
        transition && `镜头衔接：${transition}`
      ].filter(Boolean).join('，') || blocking || shotSummary || sourceDescription;
      const startFrameDescription = [shotSummary, blocking].filter(Boolean).join('，') || detailedShotDescription;
      const detailedPlot = this.buildDetailedPlotFromFields({
        shotDeployment,
        actionDetails,
        dialogueDetails,
        dialogueBeatDetails
      });
      const actionArcSeed = scene?.action_arc || scene?.Action || scene?.action;
      const actionArc = this.normalizeArcLines(actionArcSeed, 4).length
        ? this.normalizeArcLines(actionArcSeed, 4)
        : this.normalizeArcLines([blocking, sceneActionLine], 3);
      const emotionArc = this.normalizeArcLines(scene?.emotion_arc, 4);
      const rhythmPlan = String(scene?.rhythm_plan || '').trim();
      const startFrameGoal = String(scene?.start_frame_goal || scene?.StartFrame || '').trim();
      const previousBeat = Array.isArray(scene?.shot_plan) && beatIndex > 0
        ? scene.shot_plan[beatIndex - 1]
        : null;
      const prevState = String(
        safeBeat?.prev_state ||
        safeBeat?.prevState ||
        previousBeat?.target_state ||
        previousBeat?.targetState ||
        scene?.prev_state ||
        scene?.previous_state ||
        startFrameGoal ||
        ''
      ).trim();
      const motionInstruction = String(
        safeBeat?.motion_instruction ||
        safeBeat?.motionInstruction ||
        safeBeat?.action ||
        blocking ||
        actionArc[0] ||
        ''
      ).trim();
      const normalizedMotionInstruction = this.ensureMotionInstructionFromPrevState(prevState, motionInstruction);
      const targetState = this.ensureGradualTargetState(
        String(
          safeBeat?.target_state ||
          safeBeat?.targetState ||
          scene?.target_state ||
          scene?.targetState ||
          scene?.end_frame_goal ||
          scene?.EndFrame ||
          ''
        ).trim(),
        normalizedMotionInstruction
      );
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        String(safeBeat?.visual_anchor || safeBeat?.visualAnchor || '').trim(),
        prevState,
        targetState,
        sourceDescription
      );
      const continuityHint = this.ensureContinuityHint(
        String(safeBeat?.continuity_hint || safeBeat?.continuityHint || '').trim(),
        targetState,
        prevState,
        sourceDescription
      );
      const sceneNarrative = String(scene?.scene_script || '').trim() || this.buildSceneNarrativeFromFields({
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        detailedPlot,
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        prevState,
        motionInstruction: normalizedMotionInstruction,
        targetState,
        visualAnchor,
        continuityHint
      });
      const explicitBeatPrompt = this.sanitizeFramePromptText(
        String(
          safeBeat.prompt ||
          safeBeat.enhanced_prompt ||
          ''
        ).trim()
      );
      const scenePrompt = this.sanitizeFramePromptText(String(scene?.prompt || '').trim());
      const beatSpecificPrompt = this.sanitizeFramePromptText(
        [
          [shotType, cameraAngle, cameraMovement].filter(Boolean).join(' / '),
          blocking && `动作：${blocking}`,
          dialogue && `对白：${dialogue}`,
          transition && `转场：${transition}`,
          sourceDescription && `场景：${sourceDescription}`
        ].filter(Boolean).join('，')
      );
      const beatPrompt = explicitBeatPrompt || this.sanitizeFramePromptText(
        [beatSpecificPrompt, scenePrompt].filter(Boolean).join('，')
      );

      return this.normalizeShot({
        sceneNo,
        title: `场次 ${sceneNo} · 镜头 ${beatId}`,
        duration: duration || scene?.duration || '5s',
        prompt: beatPrompt,
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        sceneNarrative,
        shotDeployment,
        actionDetails,
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        prevState,
        motionInstruction: normalizedMotionInstruction,
        prev_state: prevState,
        targetState,
        visualAnchor,
        continuityHint,
        dialogueDetails,
        dialogueBeatDetails,
        detailedPlot,
        startFrame: {
          description: startFrameDescription,
          enhanced_prompt: '',
          image_url: ''
        }
      });
    },
    shotsFromScene(scene, index) {
      const sceneNo = this.sceneNoFromScene(scene, index + 1);
      const plan = Array.isArray(scene?.shot_plan) ? scene.shot_plan.filter((item) => item !== undefined && item !== null) : [];
      if (plan.length) {
        return plan.map((beat, beatIndex) => this.buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex));
      }

      const sourceDescription = String(scene?.description || '').trim();
      const shotSummary = String(scene?.shot_description || '').trim();
      const detailedShotDescription = String(
        scene?.detailed_shot_description || shotSummary || sourceDescription || ''
      ).trim();
      const detailedPlot = this.buildSceneDetailedPlot(scene);
      const actionArc = this.normalizeArcLines(scene?.action_arc || scene?.Action || scene?.action, 4);
      const emotionArc = this.normalizeArcLines(scene?.emotion_arc, 4);
      const rhythmPlan = String(scene?.rhythm_plan || '').trim();
      const startFrameGoal = String(scene?.start_frame_goal || scene?.StartFrame || '').trim();
      const prevState = String(
        scene?.prev_state ||
        scene?.previous_state ||
        startFrameGoal ||
        ''
      ).trim();
      const motionInstruction = String(
        scene?.motion_instruction ||
        scene?.motionInstruction ||
        scene?.Action ||
        scene?.action ||
        actionArc[0] ||
        ''
      ).trim();
      const normalizedMotionInstruction = this.ensureMotionInstructionFromPrevState(prevState, motionInstruction);
      const targetState = this.ensureGradualTargetState(
        String(
          scene?.target_state ||
          scene?.targetState ||
          scene?.end_frame_goal ||
          scene?.EndFrame ||
          ''
        ).trim(),
        normalizedMotionInstruction
      );
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        String(scene?.visual_anchor || scene?.visualAnchor || '').trim(),
        prevState,
        targetState,
        sourceDescription
      );
      const continuityHint = this.ensureContinuityHint(
        String(scene?.continuity_hint || scene?.continuityHint || '').trim(),
        targetState,
        prevState,
        sourceDescription
      );
      const sceneNarrative = String(scene?.scene_script || '').trim() || this.buildSceneNarrativeFromFields({
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        detailedPlot,
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        prevState,
        motionInstruction: normalizedMotionInstruction,
        targetState,
        visualAnchor,
        continuityHint
      });
      const scenePrompt = this.sanitizeFramePromptText(String(scene?.prompt || '').trim());
      return [this.normalizeShot({
        sceneNo,
        title: `场次 ${sceneNo}`,
        duration: scene?.duration || '5s',
        prompt: scenePrompt,
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        sceneNarrative,
        shotDeployment: this.buildSceneShotDeployment(scene),
        actionDetails: this.buildSceneActionDetails(scene),
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        prevState,
        motionInstruction: normalizedMotionInstruction,
        prev_state: prevState,
        targetState,
        visualAnchor,
        continuityHint,
        dialogueDetails: String(
          scene?.dialogue_details ||
          (Array.isArray(scene?.dialogue) ? scene.dialogue.join('；') : scene?.dialogue || '') ||
          ''
        ).trim(),
        dialogueBeatDetails: this.buildSceneDialogueBeatDetails(scene),
        detailedPlot,
        startFrame: {
          description: detailedShotDescription,
          enhanced_prompt: '',
          image_url: ''
        }
      })];
    },
    hasExplicitCharacterBindings(shot) {
      const safeShot = shot || {};
      const boundIds = this.normalizeStringArray(safeShot.boundCharacterAssetIds);
      const boundNames = this.normalizeStringArray(safeShot.boundCharacterNames);
      const structuredBindings = this.normalizeCharacterBindingList(safeShot.character_binding || safeShot.characterBinding);
      return boundIds.length > 0 || boundNames.length > 0 || structuredBindings.length > 0;
    },
    hasExplicitSceneBindings(shot) {
      const safeShot = shot || {};
      const boundIds = this.normalizeStringArray(safeShot.boundSceneAssetIds);
      const boundNames = this.normalizeStringArray(safeShot.boundSceneNames);
      return boundIds.length > 0 || boundNames.length > 0;
    },
    sortShotsBySceneNo() {
      const currentTitle = String(this.currentShot?.title || '');
      this.localShots = this.localShots
        .map((shot, index) => ({ shot, index, sceneNo: this.sceneNoFromShot(shot, index + 1) }))
        .sort((a, b) => {
          if (a.sceneNo !== b.sceneNo) return a.sceneNo - b.sceneNo;
          return a.index - b.index;
        })
        .map((item) => item.shot);

      const nextIndex = this.localShots.findIndex((shot) => String(shot?.title || '') === currentTitle);
      this.selectedShotIndex = nextIndex >= 0 ? nextIndex : (this.localShots.length ? 0 : -1);
      this.emitShots();
    },
    buildShotDedupKey(shot, fallbackIndex = 0) {
      const safe = shot || {};
      const norm = (value) => String(value || '').trim().replace(/\s+/g, ' ');
      const sceneNo = this.sceneNoFromShot(safe, fallbackIndex + 1);
      const keyParts = [
        sceneNo,
        norm(safe.title),
        norm(safe.duration),
        norm(safe.prompt || safe.shot_prompt || safe.shotPrompt),
        norm(safe.sceneNarrative || safe.scene_script),
        norm(safe.shotSummary || safe.shot_summary),
        norm(safe.prevState || safe.prev_state),
        norm(safe.startFrameGoal || safe.start_frame_goal),
        norm(safe.motionInstruction || safe.motion_instruction),
        norm(safe.targetState || safe.target_state || safe.endFrameGoal || safe.end_frame_goal),
        norm(safe.visualAnchor || safe.visual_anchor),
        norm(safe.continuityHint || safe.continuity_hint),
        norm(safe.startFrame?.description),
        norm(safe.endFrame?.description)
      ];
      if (keyParts.every((part) => !part)) return `shot-fallback-${fallbackIndex}`;
      return keyParts.join('|');
    },
    dedupeShots(shots) {
      const list = Array.isArray(shots) ? shots : [];
      const deduped = [];
      const seen = new Set();
      list.forEach((item, index) => {
        const normalized = this.normalizeShot(item);
        const key = this.buildShotDedupKey(normalized, index);
        if (seen.has(key)) return;
        seen.add(key);
        deduped.push(normalized);
      });
      return this.repairUniformShotPrompts(deduped);
    },
    isLikelyGlobalPromptTemplate(promptText) {
      const text = String(promptText || '').trim().toLowerCase();
      if (!text) return false;
      const tokens = [
        'eastern anime style',
        '2d animation',
        'cel shading',
        'mandarin speech',
        'chinese dialogue',
        'no english voice'
      ];
      if (tokens.some((token) => text.includes(token))) return true;
      if (text.length >= 160) return true;
      return false;
    },
    repairUniformShotPrompts(shots) {
      const list = Array.isArray(shots) ? shots : [];
      if (list.length <= 1) return list;

      const normalizedPrompts = list
        .map((shot) => this.sanitizeFramePromptText(String(shot?.prompt || '').trim()))
        .filter(Boolean);
      if (normalizedPrompts.length <= 1) return list;

      const uniquePrompts = [...new Set(normalizedPrompts)];
      if (uniquePrompts.length !== 1) return list;

      const sharedPrompt = uniquePrompts[0];
      if (!this.isLikelyGlobalPromptTemplate(sharedPrompt)) return list;

      let changed = false;
      const repaired = list.map((shot) => {
        const safeShot = shot && typeof shot === 'object' ? { ...shot } : {};
        const beatHint = this.extractShotDeploymentBeat(safeShot, 'startFrame');
        const repairedPrompt = this.sanitizeFramePromptText(
          [
            String(safeShot?.shotSummary || safeShot?.shot_summary || '').trim(),
            beatHint,
            String(safeShot?.startFrame?.description || '').trim(),
            String(safeShot?.actionDetails || safeShot?.action_details || '').trim(),
            String(safeShot?.dialogueDetails || safeShot?.dialogue_details || '').trim()
          ].filter(Boolean).join('，')
        );
        if (repairedPrompt && repairedPrompt !== sharedPrompt) {
          safeShot.prompt = this.summarizeForFrame(repairedPrompt, 180);
          changed = true;
        }
        return safeShot;
      });
      return changed ? repaired : list;
    },
    normalizeShot(shot) {
      const safe = shot || {};
      const structuredCharacterBinding = this.normalizeCharacterBindingList(
        safe.character_binding || safe.characterBinding
      );
      const structuredBindingIds = structuredCharacterBinding.map((item) => String(item.asset_id || '').trim()).filter(Boolean);
      const structuredBindingNames = structuredCharacterBinding.map((item) => String(item.character_name || '').trim()).filter(Boolean);
      const dialogueDetails = String(safe.dialogueDetails || safe.dialogue_details || safe.dialogue || '').trim();
      const dialogueBeatDetails = String(safe.dialogueBeatDetails || safe.dialogue_beat_details || '').trim();
      const actionDetails = String(
        safe.actionDetails ||
        safe.action_details ||
        (Array.isArray(safe.character_actions) ? safe.character_actions.join('\n') : '')
      ).trim();
      const shotDeployment = String(safe.shotDeployment || safe.shot_deployment || safe.staging_notes || '').trim();
      const actionArc = this.normalizeArcLines(safe.actionArc || safe.action_arc || safe.Action || safe.action || safe.character_actions, 4);
      const emotionArc = this.normalizeArcLines(safe.emotionArc || safe.emotion_arc || safe.Mood || safe.mood, 4);
      const rhythmPlan = String(safe.rhythmPlan || safe.rhythm_plan || '').trim();
      const startFrameGoal = String(safe.startFrameGoal || safe.start_frame_goal || safe.StartFrame || safe.start_frame || '').trim();
      const motionInstruction = this.resolveShotMotionInstruction(safe);
      const targetState = this.ensureGradualTargetState(this.resolveShotTargetState(safe), motionInstruction);
      const moodValue = String(safe.mood || safe.Mood || '').trim();

      const legacySourceDescription = String(safe.sourceDescription || safe.source_description || safe.description || '').trim();
      const legacyShotSummary = String(safe.shotSummary || safe.shot_summary || safe.shotDescription || safe.shot_description || '').trim();
      const legacyDetailedShotDescription = String(
        safe.detailedShotDescription ||
        safe.detailed_shot_description ||
        safe.sceneDetailedDescription ||
        ''
      ).trim();
      const legacyDetailedPlot = this.buildDetailedPlotFromFields({
        detailedPlot: safe.detailedPlot || safe.detailed_plot,
        shotDeployment,
        actionDetails,
        dialogueDetails,
        dialogueBeatDetails
      });
      const explicitShotPrompt = this.sanitizeFramePromptText(
        String(safe.prompt || safe.shot_prompt || safe.shotPrompt || '').trim()
      );

      const sceneNarrativeInput = String(
        safe.sceneNarrative || safe.scene_narrative || safe.scene_script || ''
      ).trim();
      const sceneNarrative = sceneNarrativeInput || this.buildSceneNarrativeFromFields({
        sourceDescription: legacySourceDescription,
        shotSummary: legacyShotSummary,
        detailedShotDescription: legacyDetailedShotDescription,
        detailedPlot: legacyDetailedPlot,
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        motionInstruction,
        targetState
      });
      const parsedNarrative = this.parseSceneNarrative(sceneNarrative, {
        sourceDescription: legacySourceDescription,
        shotSummary: legacyShotSummary,
        detailedShotDescription: legacyDetailedShotDescription,
        detailedPlot: legacyDetailedPlot,
        actionArc,
        emotionArc,
        rhythmPlan,
        startFrameGoal,
        prevState: this.resolveShotPrevState(safe),
        motionInstruction,
        targetState,
        visualAnchor: this.resolveShotVisualAnchor(safe),
        continuityHint: this.resolveShotContinuityHint(safe)
      });
      const resolvedPrevState = String(
        parsedNarrative.prevState ||
        this.resolveShotPrevState(safe) ||
        startFrameGoal ||
        '承接上一镜头同场景基础状态'
      ).trim();
      const resolvedMotionInstruction = this.ensureMotionInstructionFromPrevState(
        resolvedPrevState,
        parsedNarrative.motionInstruction || motionInstruction
      );
      const resolvedTargetState = this.ensureGradualTargetState(
        parsedNarrative.targetState || targetState,
        resolvedMotionInstruction
      );
      const resolvedVisualAnchor = this.ensureVisualAnchorWithPrevState(
        parsedNarrative.visualAnchor || this.resolveShotVisualAnchor(safe),
        resolvedPrevState,
        resolvedTargetState,
        parsedNarrative.sourceDescription || legacySourceDescription
      );
      const resolvedContinuityHint = this.ensureContinuityHint(
        parsedNarrative.continuityHint || this.resolveShotContinuityHint(safe),
        resolvedTargetState,
        resolvedPrevState,
        parsedNarrative.sourceDescription || legacySourceDescription
      );
      const normalizedNarrative = this.buildSceneNarrativeFromFields({
        sourceDescription: parsedNarrative.sourceDescription,
        shotSummary: parsedNarrative.shotSummary,
        detailedShotDescription: parsedNarrative.detailedShotDescription,
        detailedPlot: parsedNarrative.detailedPlot,
        actionArc: parsedNarrative.actionArc,
        emotionArc: parsedNarrative.emotionArc,
        rhythmPlan: parsedNarrative.rhythmPlan,
        startFrameGoal: parsedNarrative.startFrameGoal,
        prevState: resolvedPrevState,
        motionInstruction: resolvedMotionInstruction,
        targetState: resolvedTargetState,
        visualAnchor: resolvedVisualAnchor,
        continuityHint: resolvedContinuityHint
      }) || sceneNarrative;

      const normalizedBoundCharacterAssetIds = this.normalizeStringArray([
        ...(safe.boundCharacterAssetIds || safe.bound_character_asset_ids || []),
        ...structuredBindingIds
      ]);
      const normalizedBoundCharacterNames = this.resolveAssetNamesByIds(
        normalizedBoundCharacterAssetIds,
        this.characterAssets,
        [
          ...(safe.boundCharacterNames || safe.bound_character_names || []),
          ...structuredBindingNames
        ]
      );
      const mergedStructuredCharacterBinding = this.normalizeCharacterBindingList([
        ...structuredCharacterBinding,
        ...this.buildStructuredCharacterBindingFromIdsAndNames(
          normalizedBoundCharacterAssetIds,
          normalizedBoundCharacterNames
        )
      ]);

      const normalized = {
        sceneNo: safe.sceneNo || this.sceneNoFromValue(safe.title, 0),
        title: safe.title || '',
        duration: safe.duration || '5s',
        prompt: explicitShotPrompt,
        voiceoverText: String(
          safe.voiceoverText ||
          safe.voiceover_text ||
          safe.narrationText ||
          safe.narration_text ||
          safe.narration ||
          ''
        ).trim(),
        mood: moodValue,
        sourceDescription: parsedNarrative.sourceDescription || legacySourceDescription,
        shotSummary: parsedNarrative.shotSummary || legacyShotSummary,
        detailedShotDescription: parsedNarrative.detailedShotDescription || legacyDetailedShotDescription,
        detailedPlot: parsedNarrative.detailedPlot || legacyDetailedPlot,
        sceneNarrative: normalizedNarrative,
        actionArc: parsedNarrative.actionArc,
        emotionArc: parsedNarrative.emotionArc,
        rhythmPlan: parsedNarrative.rhythmPlan,
        startFrameGoal: parsedNarrative.startFrameGoal,
        prevState: resolvedPrevState,
        prev_state: resolvedPrevState,
        motionInstruction: resolvedMotionInstruction,
        motion_instruction: resolvedMotionInstruction,
        targetState: resolvedTargetState,
        target_state: resolvedTargetState,
        continuityHint: resolvedContinuityHint,
        continuity_hint: resolvedContinuityHint,
        visualAnchor: resolvedVisualAnchor,
        visual_anchor: resolvedVisualAnchor,
        endFrameGoal: resolvedTargetState, // legacy alias
        dialogueDetails,
        dialogueBeatDetails,
        actionDetails,
        shotDeployment,
        boundCharacterAssetIds: normalizedBoundCharacterAssetIds,
        boundCharacterNames: normalizedBoundCharacterNames,
        character_binding: mergedStructuredCharacterBinding,
        boundSceneAssetIds: this.normalizeStringArray(safe.boundSceneAssetIds || safe.bound_scene_asset_ids),
        boundSceneNames: this.normalizeStringArray(safe.boundSceneNames || safe.bound_scene_names),
        startFrame: {
          description: safe.startFrame?.description || parsedNarrative.startFrameGoal || '',
          enhanced_prompt: safe.startFrame?.enhanced_prompt || '',
          image_url: this.normalizeImageUrl(safe.startFrame?.image_url),
          reference_images: this.normalizeStringArray(safe.startFrame?.reference_images).map((item) => this.normalizeImageUrl(item)).filter((item) => this.isUsableImageUrl(item)),
          reference_image_used: this.normalizeImageUrl(safe.startFrame?.reference_image_used),
          generation_mode: String(safe.startFrame?.generation_mode || '').trim()
        },
        endFrame: {
          description: safe.endFrame?.description || resolvedTargetState || '',
          enhanced_prompt: safe.endFrame?.enhanced_prompt || '',
          image_url: this.normalizeImageUrl(safe.endFrame?.image_url),
          reference_images: this.normalizeStringArray(safe.endFrame?.reference_images).map((item) => this.normalizeImageUrl(item)).filter((item) => this.isUsableImageUrl(item)),
          reference_image_used: this.normalizeImageUrl(safe.endFrame?.reference_image_used),
          generation_mode: String(safe.endFrame?.generation_mode || '').trim()
        },
        videoUrl: this.normalizeVideoUrl(safe.videoUrl),
        videoTask: {
          taskId: safe.videoTask?.taskId || '',
          status: safe.videoTask?.status || '',
          message: safe.videoTask?.message || '',
          progress: Number.isFinite(Number(safe.videoTask?.progress)) ? Number(safe.videoTask.progress) : 0,
          provider: String(safe.videoTask?.provider || safe.videoTask?.video_provider || this.videoProvider || 'openai').trim().toLowerCase() || 'openai',
          reqKey: String(safe.videoTask?.reqKey || safe.videoTask?.req_key || '').trim(),
          queryUrl: String(safe.videoTask?.queryUrl || safe.videoTask?.query_url || '').trim(),
          queryMethod: String(safe.videoTask?.queryMethod || safe.videoTask?.query_method || '').trim().toUpperCase()
        },
        videoTail: this.normalizeVideoTail(
          safe.videoTail || safe.video_tail,
          safe.endFrame?.image_url || safe.startFrame?.image_url || ''
        )
      };
      return this.ensureShotFramePrompts(this.ensureShotPlanPrompt(normalized));
    },
    ensureShotPlanPrompt(shot) {
      const safeShot = shot || {};
      const explicitPrompt = this.sanitizeFramePromptText(String(safeShot.prompt || '').trim());
      if (explicitPrompt) {
        safeShot.prompt = explicitPrompt;
        return safeShot;
      }

      const sceneHint = this.sanitizeFramePromptText(
        String(
          safeShot.sourceDescription ||
          safeShot.shotSummary ||
          safeShot.detailedShotDescription ||
          ''
        ).trim()
      );
      const actionHint = this.sanitizeFramePromptText(
        this.extractShotDeploymentBeat(safeShot, 'startFrame') ||
        String(safeShot?.startFrame?.description || '').trim()
      );
      const cameraHint = this.sanitizeFramePromptText(
        [safeShot?.ShotSize || safeShot?.shotSize || '', safeShot?.Camera || safeShot?.camera || '']
          .map((item) => String(item || '').trim())
          .filter(Boolean)
          .join(' / ')
      );
      const derived = [sceneHint, actionHint, cameraHint].filter(Boolean).join('，');
      safeShot.prompt = this.summarizeForFrame(derived, 180);
      return safeShot;
    },
    resolveShotPlanPrompt(shot) {
      const promptText = this.sanitizeFramePromptText(String(shot?.prompt || '').trim());
      if (promptText) return promptText;
      return this.sanitizeFramePromptText(String(this.ensureShotPlanPrompt({ ...(shot || {}) }).prompt || '').trim());
    },
    buildShotFromEditingDraft() {
      const draft = this.editingShotDraft || {};
      return this.normalizeShot({
        title: String(draft.title || '').trim() || `镜头 ${Math.max(1, this.editingShotIndex + 1)}`,
        duration: String(draft.duration || '5s').trim() || '5s',
        sceneNarrative: String(draft.sceneNarrative || '').trim(),
        prompt: String(draft.shotPrompt || '').trim(),
        voiceoverText: String(draft.voiceoverText || '').trim(),
        startFrame: {
          description: String(draft.startFrameDescription || '').trim(),
          enhanced_prompt: String(draft.startFramePrompt || '').trim(),
          image_url: this.normalizeImageUrl(draft.startFrameImageUrl)
        },
        endFrame: {
          description: String(draft.endFrameDescription || '').trim(),
          enhanced_prompt: String(draft.endFramePrompt || '').trim(),
          image_url: this.normalizeImageUrl(draft.endFrameImageUrl)
        },
        boundCharacterAssetIds: this.normalizeStringArray(draft.boundCharacterAssetIds),
        boundCharacterNames: this.normalizeStringArray(draft.boundCharacterNames),
        boundSceneAssetIds: this.normalizeStringArray(draft.boundSceneAssetIds),
        boundSceneNames: this.normalizeStringArray(draft.boundSceneNames)
      });
    },
    buildFrameEnhanceContext(shot, frameKey, shotIndex = -1) {
      const safeShot = this.normalizeShot({ ...(shot || {}) });
      const previousShot = shotIndex > 0 ? this.localShots[shotIndex - 1] : null;
      const nextShot = shotIndex >= 0 && shotIndex < this.localShots.length - 1 ? this.localShots[shotIndex + 1] : null;
      const frameDescription = frameKey === 'endFrame'
        ? this.buildDerivedEndFrameDescription(safeShot)
        : String(
          safeShot?.startFrame?.description ||
          safeShot?.startFrameGoal ||
          safeShot?.start_frame_goal ||
          ''
        ).trim();
      const prevState = this.resolveShotPrevState(safeShot);
      const motionInstruction = this.ensureMotionInstructionFromPrevState(prevState, this.resolveShotMotionInstruction(safeShot));
      const targetState = this.ensureGradualTargetState(this.resolveShotTargetState(safeShot), motionInstruction);
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        this.resolveShotVisualAnchor(safeShot),
        prevState,
        targetState,
        String(safeShot?.sourceDescription || '').trim()
      );
      const continuityHint = this.ensureContinuityHint(
        this.resolveShotContinuityHint(safeShot),
        targetState,
        prevState,
        String(safeShot?.sourceDescription || '').trim()
      );
      return {
        prompt_type: 'frame',
        asset_type: 'scene',
        name: String(safeShot?.title || '当前镜头').trim() || '当前镜头',
        subject_name: String(safeShot?.title || '当前镜头').trim() || '当前镜头',
        visual_style: `高质感国风奇幻动画电影感，完整单幅关键帧，主体明确，空间纵深强，体积光明显，${frameKey === 'startFrame' ? '开场建立感强' : '动作收束落点明确'}`,
        scene_script: String(safeShot?.sceneNarrative || '').trim(),
        shot_prompt: this.resolveShotPlanPrompt(safeShot),
        shot_deployment: String(safeShot?.shotDeployment || '').trim(),
        detailed_plot: this.getShotDetailedPlot(safeShot),
        action_details: String(safeShot?.actionDetails || '').trim(),
        dialogue_details: String(safeShot?.dialogueDetails || '').trim(),
        narration_text: this.resolveShotVoiceoverText(safeShot),
        continuity_rules: this.buildContinuityRules(safeShot),
        scene_hints: this.buildSceneFrameHints(safeShot),
        character_hints: this.buildCharacterFrameHints(safeShot),
        character_identity_rules: this.buildCharacterIdentityRules(safeShot),
        bound_character_names: this.resolveBoundCharacterAssetsForShot(safeShot)
          .map((item, idx) => String(item?.name || `角色${idx + 1}`).trim())
          .filter(Boolean),
        previous_shot_summary: this.buildShotNarrativeSummary(previousShot),
        next_shot_summary: this.buildShotNarrativeSummary(nextShot),
        frame_key: frameKey,
        frame_description: frameDescription,
        start_frame_goal: String(safeShot?.startFrameGoal || safeShot?.start_frame_goal || '').trim(),
        prev_state: prevState,
        motion_instruction: motionInstruction,
        target_state: targetState,
        visual_anchor: visualAnchor,
        continuity_hint: continuityHint
      };
    },
    buildFramePromptSeedForEnhance(shot, frameKey) {
      const safeShot = this.normalizeShot({ ...(shot || {}) });
      if (!safeShot.startFrame) safeShot.startFrame = { description: '', enhanced_prompt: '', image_url: '' };
      if (!safeShot.endFrame) safeShot.endFrame = { description: '', enhanced_prompt: '', image_url: '' };
      safeShot[frameKey] = {
        ...(safeShot[frameKey] || {}),
        enhanced_prompt: ''
      };
      return this.buildIndependentFramePrompt(safeShot, frameKey);
    },
    buildShotPlanEnhanceContext(shot) {
      const safeShot = this.normalizeShot({ ...(shot || {}) });
      const title = String(safeShot?.title || '当前镜头').trim() || '当前镜头';
      const startFrameGoal = String(
        safeShot?.startFrame?.description ||
        safeShot?.startFrameGoal ||
        safeShot?.start_frame_goal ||
        ''
      ).trim();
      const prevState = this.resolveShotPrevState(safeShot);
      const motionInstruction = this.ensureMotionInstructionFromPrevState(prevState, this.resolveShotMotionInstruction(safeShot));
      const targetState = this.ensureGradualTargetState(
        String(
          safeShot?.endFrame?.description ||
          this.resolveShotTargetState(safeShot) ||
          ''
        ).trim(),
        motionInstruction
      );
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        this.resolveShotVisualAnchor(safeShot),
        prevState,
        targetState,
        String(safeShot?.sourceDescription || '').trim()
      );
      const continuityHint = this.ensureContinuityHint(
        this.resolveShotContinuityHint(safeShot),
        targetState,
        prevState,
        String(safeShot?.sourceDescription || '').trim()
      );
      return {
        prompt_type: 'shot_plan',
        asset_type: 'scene',
        name: title,
        subject_name: title,
        visual_style: '高质感国风奇幻动画电影感，单镜头分镜提示词，主体明确，空间纵深强，光影层次清楚',
        scene_script: String(safeShot?.sceneNarrative || '').trim(),
        shot_deployment: String(safeShot?.shotDeployment || '').trim(),
        detailed_plot: this.getShotDetailedPlot(safeShot),
        action_details: String(safeShot?.actionDetails || '').trim(),
        dialogue_details: String(safeShot?.dialogueDetails || '').trim(),
        continuity_rules: [
          this.buildContinuityRules(safeShot),
          '输出应只覆盖当前镜头，不要写成整场戏；需明确景别、机位、主体动作、空间关系、情绪推进和起止帧衔接。'
        ].filter(Boolean).join('\n'),
        scene_hints: this.buildSceneFrameHints(safeShot),
        character_hints: this.buildCharacterFrameHints(safeShot),
        shot_duration: String(safeShot?.duration || '5s').trim() || '5s',
        shot_summary: this.buildShotNarrativeSummary(safeShot),
        prev_state: prevState,
        start_frame_goal: startFrameGoal,
        motion_instruction: motionInstruction,
        target_state: targetState,
        visual_anchor: visualAnchor,
        continuity_hint: continuityHint
      };
    },
    buildPremiumFrameStyleHint(frameKey = '') {
      const stageHint = frameKey === 'startFrame'
        ? '偏开场建立感，先交代人物站位、空间关系与视线方向。'
        : frameKey === 'endFrame'
          ? '偏收束落点，动作结果、姿态变化和情绪落点要明确。'
          : '突出单帧叙事落点与电影感。';
      return [
        '严格中国动漫风 / 国漫风，高质感国风奇幻动画电影感，不要日漫感，不要欧美动画感，不要水墨写意，不要泼墨留白，不要低幼插画感。',
        '完整单幅画面，主体重心明确，构图干净，前景、中景、远景层次清楚，空间纵深强。',
        '体积光、边缘光、环境雾气和建筑植被细节丰富，色彩通透不发灰，画面锐利但不脏。',
        '角色比例修长，服装与发丝细节清楚，整体像高端动画长片关键帧而不是普通分镜草图。',
        stageHint
      ].join('，');
    },
    buildPremiumFrameStyleTags(frameKey = '') {
      const stageHint = frameKey === 'startFrame'
        ? 'opening beat, spatial establishing'
        : frameKey === 'endFrame'
          ? 'ending beat, emotional payoff'
          : 'single-moment storytelling';
      return [
        'strict chinese anime style',
        'guoman style',
        'cinematic chinese fantasy animation',
        'premium keyframe illustration',
        'clear subject dominance',
        'layered foreground midground background',
        'strong depth and perspective',
        'volumetric light',
        'rim light',
        'atmospheric perspective',
        'clean detailed environment',
        'crisp costume details',
        'not japanese anime style',
        'not western cartoon',
        'not ink wash',
        'not minimalist watercolor',
        stageHint
      ].filter(Boolean).join(', ');
    },
    buildDefaultEnhancedPrompt(baseDescription, dialogueDetails = '', seedPrompt = '', shotDeployment = '', actionDetails = '', dialogueBeatDetails = '', frameKey = '') {
      const seed = String(seedPrompt || '').trim();
      const description = String(baseDescription || '').trim();
      const detailedPlot = this.buildDetailedPlotFromFields({
        shotDeployment,
        actionDetails,
        dialogueDetails,
        dialogueBeatDetails
      });
      const parts = [];
      if (seed) parts.push(seed);
      if (description && (!seed || !seed.includes(description))) parts.push(description);
      if (detailedPlot && !seed) parts.push(`详细剧情：${this.summarizeForFrame(detailedPlot, 120)}`);
      parts.push(this.buildPremiumFrameStyleHint(frameKey));
      parts.push('单幅电影感构图，不要分屏，不要多格漫画，不要拼贴，不要字幕文字或UI元素');
      parts.push('主体清晰，动作连贯，情绪明确，光影层次分明，空间纵深自然，场景细节考究');
      return parts.join('，').replace(/，+/g, '，').trim();
    },
    extractShotDeploymentBeat(shot, frameKey) {
      const deployment = String(shot?.shotDeployment || this.getShotDetailedPlot(shot)).trim();
      if (!deployment) return '';
      const lines = deployment
        .split(/\r?\n/)
        .map((item) => String(item || '').trim())
        .filter(Boolean);
      if (!lines.length) return '';

      const rawLine = frameKey === 'endFrame' ? lines[lines.length - 1] : lines[0];
      return rawLine
        .replace(/^\d+\s*[\.、\)]\s*/, '')
        .replace(/\|\s*台词:[^|]*/g, '')
        .replace(/\|\s*\d+(?:\.\d+)?s\b/gi, '')
        .replace(/\s+/g, ' ')
        .trim();
    },
    shouldRefreshFramePrompt(promptText, frameKey) {
      const text = String(promptText || '').trim();
      if (!text) return true;
      const lower = text.toLowerCase();
      if (
        text.includes('电影分镜') ||
        text.includes('强调景别变化') ||
        text.includes('机位运动') ||
        text.includes('动作连续性与面部微反应')
      ) {
        return true;
      }
      if (!text.includes('单幅') || !text.includes('不要分屏')) {
        return true;
      }
      if (frameKey === 'startFrame' && lower.includes('结束帧')) return true;
      if (frameKey === 'endFrame' && lower.includes('起始帧')) return true;
      return false;
    },
    summarizeForFrame(text, maxLength = 160) {
      const normalized = this.sanitizeFramePromptText(text);
      if (!normalized) return '';
      return normalized.length > maxLength ? `${normalized.slice(0, maxLength)}...` : normalized;
    },
    buildDerivedEndFrameDescription(shot) {
      const safeShot = shot || {};
      const explicit = String(safeShot?.endFrame?.description || '').trim();
      if (explicit) return explicit;

      const startDescription = this.summarizeForFrame(String(safeShot?.startFrame?.description || '').trim(), 80);
      const detailedPlot = this.summarizeForFrame(this.getShotDetailedPlot(safeShot), 220);
      const explicitGoal = this.summarizeForFrame(
        this.ensureGradualTargetState(
          this.resolveShotTargetState(safeShot),
          this.resolveShotMotionInstruction(safeShot)
        ),
        140
      );
      const parts = [];

      if (startDescription) parts.push(`保持同一场景与同一人物，但画面状态已从开场推进：${startDescription}`);
      if (detailedPlot) parts.push(`当前镜头详细剧情推进到后段或收束：${detailedPlot}`);
      if (explicitGoal) parts.push(`本镜头目标状态：${explicitGoal}`);
      parts.push('人物姿态、视线、手部动作、道具状态与镜头重心相较起始帧发生明确变化');

      return parts.join('，').replace(/，+/g, '，').trim();
    },
    buildIndependentFramePrompt(shot, frameKey) {
      const safeShot = shot || {};
      const frame = safeShot?.[frameKey] || {};
      const explicitPrompt = String(frame?.enhanced_prompt || '').trim();
      if (explicitPrompt) return explicitPrompt;

      const sourceDescription = this.sanitizeFramePromptText(String(safeShot?.sourceDescription || '').trim());
      const shotSummary = this.sanitizeFramePromptText(String(safeShot?.shotSummary || '').trim());
      const detailedShotDescription = this.sanitizeFramePromptText(String(safeShot?.detailedShotDescription || '').trim());
      const explicitDescription = frameKey === 'endFrame'
        ? this.buildDerivedEndFrameDescription(safeShot)
        : String(frame?.description || '').trim();
      const startDescription = String(safeShot?.startFrame?.description || '').trim();
      const title = String(safeShot?.title || '').trim() || (frameKey === 'startFrame' ? '镜头开场' : '镜头收束');
      const detailedPlot = this.summarizeForFrame(this.extractShotDeploymentBeat(safeShot, frameKey), 160);
      const explicitStartGoal = this.sanitizeFramePromptText(String(safeShot?.startFrameGoal || safeShot?.start_frame_goal || '').trim());
      const explicitEndGoal = this.sanitizeFramePromptText(
        this.ensureGradualTargetState(
          this.resolveShotTargetState(safeShot),
          this.resolveShotMotionInstruction(safeShot)
        )
      );

      const stageDirective = frameKey === 'startFrame'
        ? '这是当前镜头的开场帧，表现动作开始前或开始瞬间，用于建立人物站位、视线方向、空间关系和情绪起点。'
        : '这是当前镜头的结束帧，表现动作推进到后段或收束瞬间，人物姿态、视线、手部动作、道具状态和镜头重心必须相较起始帧明显变化。';
      const independenceDirective = frameKey === 'startFrame'
        ? '只根据当前镜头内容生成，不要借用上一镜头的结束画面。'
        : '只根据当前镜头内容生成，不要借用下一镜头的开场画面，也不要重复当前镜头的起始帧。';
      const shotBeat = this.extractShotDeploymentBeat(safeShot, frameKey);
      const source = [
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        frameKey === 'startFrame' ? explicitStartGoal : explicitEndGoal,
        explicitDescription,
        shotBeat,
        startDescription || title
      ].filter(Boolean).join('，');
      const uniquenessDirective = frameKey === 'startFrame'
        ? `当前镜头标识：${title}，起始画面必须体现本镜头第一个调度重点，不能和其它镜头使用相同构图。`
        : `当前镜头标识：${title}，结束画面必须落在本镜头最后一个调度重点，不能和起始帧或其它镜头重复。`;
      const baseDescription = [source, stageDirective, independenceDirective, uniquenessDirective].filter(Boolean).join('，');

      return this.buildDefaultEnhancedPrompt(
        baseDescription,
        detailedPlot,
        '',
        '',
        '',
        '',
        frameKey
      );
    },
    buildContinuityRules(shot) {
      const safeShot = shot || {};
      const startVisual = this.sanitizeFramePromptText(String(safeShot?.startFrame?.enhanced_prompt || safeShot?.startFrame?.description || '').trim());
      const endVisual = this.sanitizeFramePromptText(String(safeShot?.endFrame?.enhanced_prompt || safeShot?.endFrame?.description || '').trim());
      const prevState = this.resolveShotPrevState(safeShot);
      const motionInstruction = this.ensureMotionInstructionFromPrevState(prevState, this.resolveShotMotionInstruction(safeShot));
      const targetState = this.ensureGradualTargetState(this.resolveShotTargetState(safeShot), motionInstruction);
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        this.resolveShotVisualAnchor(safeShot),
        prevState,
        targetState,
        String(safeShot?.sourceDescription || '').trim()
      );
      const continuityHint = this.ensureContinuityHint(
        this.resolveShotContinuityHint(safeShot),
        targetState,
        prevState,
        String(safeShot?.sourceDescription || '').trim()
      );
      const title = String(safeShot?.title || '当前镜头').trim() || '当前镜头';
      const parts = [
        '连续性约束：同一视频片段内保持同一场景、同一时间段、同一批角色、同一服装与关键道具设定',
        `当前视频片段只负责表现「${title}」这一段动作节拍，不承担整场戏的一镜到底推进`,
        '视频必须从起始帧自然过渡到结束帧，只表现当前镜头片段内的连续动作，不能跨到上一镜头尾声或下一镜头开场',
        '允许同一场次拆成多个镜头逐段生成；当前片段内部禁止分屏、多格漫画、拼贴、字幕、UI、水印',
        '空间连续：地点必须连续，禁止无因果空间跳跃',
        '物理连续：风场、能量、姿态变化必须有过渡，禁止突变',
      ];
      if (prevState) parts.push(`继承状态：${prevState}`);
      if (motionInstruction) parts.push(`动作推导：${motionInstruction}`);
      if (targetState) parts.push(`目标状态：${targetState}`);
      if (visualAnchor) parts.push(`视觉锚点：${visualAnchor}`);
      if (continuityHint) parts.push(`下一镜头方向：${continuityHint}`);
      if (startVisual) parts.push(`起始画面锚点：${startVisual}`);
      if (endVisual) parts.push(`目标状态锚点：${endVisual}`);
      return parts.join('\n');
    },
    ensureShotFramePrompts(shot) {
      const safeShot = shot || {};
      if (!safeShot.startFrame) safeShot.startFrame = { description: '', enhanced_prompt: '', image_url: '' };
      if (!safeShot.endFrame) safeShot.endFrame = { description: '', enhanced_prompt: '', image_url: '' };

      const detailedPlot = this.getShotDetailedPlot(safeShot);
      const shotPlanPrompt = this.resolveShotPlanPrompt(safeShot);
      if (this.shouldRefreshFramePrompt(safeShot.startFrame.enhanced_prompt, 'startFrame')) {
        safeShot.startFrame.enhanced_prompt = this.buildDefaultEnhancedPrompt(
          [safeShot.startFrame.description, this.extractShotDeploymentBeat(safeShot, 'startFrame')].filter(Boolean).join('，'),
          detailedPlot,
          shotPlanPrompt,
          '',
          '',
          '',
          'startFrame'
        );
      }
      if (!String(safeShot.endFrame.description || '').trim()) {
        safeShot.endFrame.description = this.buildDerivedEndFrameDescription(safeShot);
      }
      if (this.shouldRefreshFramePrompt(safeShot.endFrame.enhanced_prompt, 'endFrame') && String(safeShot.endFrame.description || '').trim()) {
        safeShot.endFrame.enhanced_prompt = this.buildDefaultEnhancedPrompt(
          [safeShot.endFrame.description, this.extractShotDeploymentBeat(safeShot, 'endFrame')].filter(Boolean).join('，'),
          detailedPlot,
          shotPlanPrompt,
          '',
          '',
          '',
          'endFrame'
        );
      }
      return safeShot;
    },
    normalizeVideoUrl(value) {
      const text = typeof value === 'string'
        ? value.trim()
        : (value && typeof value === 'object'
          ? String(value.url || value.video_url || value.output_url || value.download_url || '').trim()
          : '');
      if (!text) return '';
      if (text === 'https://...' || text === 'http://...') return '';
      if (text.includes('...')) return '';

      try {
        const parsed = new URL(text);
        if (!/^https?:$/i.test(parsed.protocol)) return '';
        const path = String(parsed.pathname || '').toLowerCase();
        if (/\.(jpg|jpeg|png|webp|gif|bmp|svg)$/i.test(path)) return '';
      } catch (error) {
        return '';
      }
      return text;
    },
    normalizeImageUrl(value) {
      const text = String(value || '').trim();
      if (!text) return '';
      if (text === 'https://...' || text === 'http://...') return '';
      if (text.includes('...')) return '';
      if (text.toLowerCase().includes('via.placeholder.com')) return '';
      try {
        const parsed = new URL(text);
        if (!/^https?:$/i.test(parsed.protocol)) return '';
        if (!parsed.hostname || (!parsed.hostname.includes('.') && parsed.hostname !== 'localhost')) return '';
      } catch (error) {
        return '';
      }
      return text;
    },
    isUsableImageUrl(value) {
      const text = this.normalizeImageUrl(value);
      if (!text) return false;
      return true;
    },
    extractVideoUrl(payload) {
      const urls = [];
      const walk = (node, depth = 0) => {
        if (!node || depth > 8) return;
        if (typeof node === 'string') {
          const text = node.trim();
          if (text.startsWith('http://') || text.startsWith('https://')) urls.push(text);
          return;
        }
        if (Array.isArray(node)) {
          node.forEach((item) => walk(item, depth + 1));
          return;
        }
        if (typeof node === 'object') Object.keys(node).forEach((key) => walk(node[key], depth + 1));
      };
      walk(payload, 0);
      if (!urls.length) return '';
      const preferred = urls.find((url) => /\.mp4|\.m3u8|\.mov|video/i.test(url));
      return preferred || urls[0];
    },
    resolveBoundCharacterAssetsForShot(shot, { explicitOnly = false } = {}) {
      const characterAssets = this.characterAssets;
      if (!characterAssets.length) return [];

      const safeShot = shot || {};
      const boundIds = new Set(this.normalizeStringArray(safeShot.boundCharacterAssetIds));
      const boundNames = new Set(this.normalizeStringArray(safeShot.boundCharacterNames));
      const structuredBindings = this.normalizeCharacterBindingList(safeShot.character_binding || safeShot.characterBinding);
      structuredBindings.forEach((item) => {
        const bindingId = String(item.asset_id || '').trim();
        const bindingName = String(item.character_name || '').trim();
        if (bindingId) boundIds.add(bindingId);
        if (bindingName) boundNames.add(bindingName);
      });

      if (!boundIds.size && !boundNames.size) {
        return [];
      }

      const selected = characterAssets.filter((asset) => {
        const assetId = String(asset?.id || '').trim();
        const assetName = String(asset?.name || '').trim();
        return (assetId && boundIds.has(assetId)) || (assetName && boundNames.has(assetName));
      });

      return selected.slice(0, 6);
    },
    resolveBoundSceneAssetsForShot(shot) {
      const sceneAssets = this.sceneAssets;
      if (!sceneAssets.length) return [];

      const safeShot = shot || {};
      const boundIds = new Set(this.normalizeStringArray(safeShot.boundSceneAssetIds));
      const boundNames = new Set(this.normalizeStringArray(safeShot.boundSceneNames));
      if (!boundIds.size && !boundNames.size) {
        return [];
      }

      const selected = sceneAssets.filter((asset) => {
        const assetId = String(asset?.id || '').trim();
        const assetName = String(asset?.name || '').trim();
        return (assetId && boundIds.has(assetId)) || (assetName && boundNames.has(assetName));
      });
      return selected.slice(0, 3);
    },
    normalizeMatchText(value) {
      return String(value || '')
        .trim()
        .toLowerCase()
        .replace(/[\s\-_.:,;'"`~!@#$%^&*(){}\[\]<>?/\\|，。！？、；：“”‘’（）【】《》\n\r\t]+/g, '');
    },
    extractMatchTokens(value, maxCount = 6) {
      const raw = String(value || '').trim();
      if (!raw) return [];
      const tokens = raw
        .split(/[\s,，。.;；:：、|\\/()\[\]{}'"“”‘’!?！？\-—_]+/)
        .map((item) => String(item || '').trim())
        .filter((item) => item.length >= 2)
        .map((item) => this.normalizeMatchText(item))
        .filter(Boolean);
      return [...new Set(tokens)].slice(0, maxCount);
    },
    buildShotMatchText(shot) {
      const safe = shot || {};
      const chunks = [
        safe.title,
        safe.prompt,
        safe.sceneNarrative,
        safe.sourceDescription,
        safe.shotSummary,
        safe.detailedShotDescription,
        safe.detailedPlot,
        safe.actionDetails,
        safe.dialogueDetails,
        safe.startFrame?.description,
        safe.endFrame?.description
      ];
      return this.normalizeMatchText(chunks.filter(Boolean).join(' '));
    },
    scoreAssetForShotText(shotText, asset, { sceneNo = 0 } = {}) {
      if (!shotText) return 0;
      const safeAsset = asset && typeof asset === 'object' ? asset : {};
      const assetName = this.normalizeMatchText(safeAsset.name);
      const assetText = this.normalizeMatchText(
        [safeAsset.name, safeAsset.source_description, safeAsset.prompt, safeAsset.type, safeAsset.asset_kind]
          .filter(Boolean)
          .join(' ')
      );
      if (!assetText) return 0;

      let score = 0;
      if (assetName && shotText.includes(assetName)) {
        score += 8;
      }

      const tokens = [
        ...this.extractMatchTokens(safeAsset.name, 4),
        ...this.extractMatchTokens(safeAsset.source_description, 4),
        ...this.extractMatchTokens(safeAsset.prompt, 4)
      ];
      [...new Set(tokens)].forEach((token) => {
        if (!token) return;
        if (shotText.includes(token)) {
          score += token.length >= 4 ? 2 : 1;
        }
      });

      if (sceneNo > 0) {
        const sceneHints = [
          this.normalizeMatchText(`场次${sceneNo}`),
          this.normalizeMatchText(`scene${sceneNo}`),
          this.normalizeMatchText(String(sceneNo))
        ];
        if (sceneHints.some((hint) => hint && assetText.includes(hint))) {
          score += 3;
        }
      }
      return score;
    },
    pickMatchedCharacterAssets(shot, maxCount = 3) {
      const shotText = this.buildShotMatchText(shot);
      if (!shotText) return [];
      const scored = this.characterAssets
        .map((asset) => ({
          asset,
          score: this.scoreAssetForShotText(shotText, asset)
        }))
        .filter((item) => item.score >= 2)
        .sort((a, b) => b.score - a.score)
        .slice(0, maxCount)
        .map((item) => item.asset);
      return scored;
    },
    pickMatchedSceneAssets(shot, maxCount = 1) {
      const shotText = this.buildShotMatchText(shot);
      if (!shotText) return [];
      const sceneNo = this.sceneNoFromShot(shot, 0);
      const scored = this.sceneAssets
        .map((asset) => ({
          asset,
          score: this.scoreAssetForShotText(shotText, asset, { sceneNo })
        }))
        .filter((item) => item.score >= 2)
        .sort((a, b) => b.score - a.score)
        .slice(0, maxCount)
        .map((item) => item.asset);
      return scored;
    },
    applyCharacterMatchesToShot(shot, matchedAssets = []) {
      const ids = this.normalizeStringArray([
        ...(shot?.boundCharacterAssetIds || []),
        ...matchedAssets.map((item) => String(item?.id || '').trim())
      ]);
      const names = this.normalizeStringArray([
        ...(shot?.boundCharacterNames || []),
        ...matchedAssets.map((item) => String(item?.name || '').trim())
      ]);
      shot.boundCharacterAssetIds = ids;
      shot.boundCharacterNames = names;
      this.syncShotCharacterBinding(shot);
    },
    applySceneMatchesToShot(shot, matchedAssets = []) {
      const ids = this.normalizeStringArray([
        ...(shot?.boundSceneAssetIds || []),
        ...matchedAssets.map((item) => String(item?.id || '').trim())
      ]);
      const names = this.normalizeStringArray([
        ...(shot?.boundSceneNames || []),
        ...matchedAssets.map((item) => String(item?.name || '').trim())
      ]);
      shot.boundSceneAssetIds = ids;
      shot.boundSceneNames = names;
    },
    aiMatchCharactersForAllShots() {
      if (!this.localShots.length || !this.characterAssets.length) return;
      let changedShots = 0;
      let matchedShots = 0;
      let matchedAssets = 0;
      this.localShots.forEach((shot) => {
        const matched = this.pickMatchedCharacterAssets(shot, 3);
        if (!matched.length) return;
        matchedShots += 1;
        matchedAssets += matched.length;
        const before = `${this.normalizeStringArray(shot?.boundCharacterAssetIds).join('|')}::${this.normalizeStringArray(shot?.boundCharacterNames).join('|')}`;
        this.applyCharacterMatchesToShot(shot, matched);
        const after = `${this.normalizeStringArray(shot?.boundCharacterAssetIds).join('|')}::${this.normalizeStringArray(shot?.boundCharacterNames).join('|')}`;
        if (before !== after) changedShots += 1;
      });
      if (changedShots > 0) {
        this.emitShots();
      }
      alert(`AI角色匹配完成：命中 ${matchedShots} 个镜头，新增/更新 ${changedShots} 个镜头，匹配角色 ${matchedAssets} 个。`);
    },
    aiMatchScenesForAllShots() {
      if (!this.localShots.length || !this.sceneAssets.length) return;
      let changedShots = 0;
      let matchedShots = 0;
      let matchedAssets = 0;
      this.localShots.forEach((shot) => {
        const matched = this.pickMatchedSceneAssets(shot, 1);
        if (!matched.length) return;
        matchedShots += 1;
        matchedAssets += matched.length;
        const before = `${this.normalizeStringArray(shot?.boundSceneAssetIds).join('|')}::${this.normalizeStringArray(shot?.boundSceneNames).join('|')}`;
        this.applySceneMatchesToShot(shot, matched);
        const after = `${this.normalizeStringArray(shot?.boundSceneAssetIds).join('|')}::${this.normalizeStringArray(shot?.boundSceneNames).join('|')}`;
        if (before !== after) changedShots += 1;
      });
      if (changedShots > 0) {
        this.emitShots();
      }
      alert(`AI场景匹配完成：命中 ${matchedShots} 个镜头，新增/更新 ${changedShots} 个镜头，匹配场景 ${matchedAssets} 个。`);
    },
    isCharacterBoundToCurrentShot(asset) {
      if (!this.currentShot) return false;
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      const boundIds = new Set(this.normalizeStringArray(this.currentShot.boundCharacterAssetIds));
      const boundNames = new Set(this.normalizeStringArray(this.currentShot.boundCharacterNames));
      return (assetId && boundIds.has(assetId)) || (assetName && boundNames.has(assetName));
    },
    isSceneBoundToCurrentShot(asset) {
      if (!this.currentShot) return false;
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      const boundIds = new Set(this.normalizeStringArray(this.currentShot.boundSceneAssetIds));
      const boundNames = new Set(this.normalizeStringArray(this.currentShot.boundSceneNames));
      return (assetId && boundIds.has(assetId)) || (assetName && boundNames.has(assetName));
    },
    toggleCharacterBinding(asset) {
      if (!this.currentShot) return;
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      if (!assetId && !assetName) return;

      const boundIds = this.normalizeStringArray(this.currentShot.boundCharacterAssetIds);
      const boundNames = this.normalizeStringArray(this.currentShot.boundCharacterNames);
      const idIndex = assetId ? boundIds.indexOf(assetId) : -1;
      const nameIndex = assetName ? boundNames.indexOf(assetName) : -1;
      const alreadyBound = idIndex !== -1 || nameIndex !== -1;

      if (alreadyBound) {
        if (idIndex !== -1) boundIds.splice(idIndex, 1);
        if (nameIndex !== -1) boundNames.splice(nameIndex, 1);
      } else {
        if (assetId) boundIds.push(assetId);
        if (assetName) boundNames.push(assetName);
      }

      this.currentShot.boundCharacterAssetIds = this.normalizeStringArray(boundIds);
      this.currentShot.boundCharacterNames = this.normalizeStringArray(boundNames);
      this.syncShotCharacterBinding(this.currentShot);
      this.emitShots();
    },
    toggleSceneBinding(asset) {
      if (!this.currentShot) return;
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      if (!assetId && !assetName) return;

      const boundIds = this.normalizeStringArray(this.currentShot.boundSceneAssetIds);
      const boundNames = this.normalizeStringArray(this.currentShot.boundSceneNames);
      const idIndex = assetId ? boundIds.indexOf(assetId) : -1;
      const nameIndex = assetName ? boundNames.indexOf(assetName) : -1;
      const alreadyBound = idIndex !== -1 || nameIndex !== -1;

      if (alreadyBound) {
        if (idIndex !== -1) boundIds.splice(idIndex, 1);
        if (nameIndex !== -1) boundNames.splice(nameIndex, 1);
      } else {
        if (assetId) boundIds.push(assetId);
        if (assetName) boundNames.push(assetName);
      }

      this.currentShot.boundSceneAssetIds = this.normalizeStringArray(boundIds);
      this.currentShot.boundSceneNames = this.normalizeStringArray(boundNames);
      this.emitShots();
    },
    bindAllCharactersToCurrentShot() {
      if (!this.currentShot) return;
      const ids = this.characterAssets.map((item) => String(item?.id || '').trim()).filter(Boolean);
      const names = this.characterAssets.map((item) => String(item?.name || '').trim()).filter(Boolean);
      this.currentShot.boundCharacterAssetIds = this.normalizeStringArray(ids);
      this.currentShot.boundCharacterNames = this.normalizeStringArray(names);
      this.syncShotCharacterBinding(this.currentShot);
      this.emitShots();
    },
    bindAllScenesToCurrentShot() {
      if (!this.currentShot) return;
      const ids = this.sceneAssets.map((item) => String(item?.id || '').trim()).filter(Boolean);
      const names = this.sceneAssets.map((item) => String(item?.name || '').trim()).filter(Boolean);
      this.currentShot.boundSceneAssetIds = this.normalizeStringArray(ids);
      this.currentShot.boundSceneNames = this.normalizeStringArray(names);
      this.emitShots();
    },
    clearBoundCharactersFromCurrentShot() {
      if (!this.currentShot) return;
      this.currentShot.boundCharacterAssetIds = [];
      this.currentShot.boundCharacterNames = [];
      this.syncShotCharacterBinding(this.currentShot);
      this.emitShots();
    },
    clearBoundScenesFromCurrentShot() {
      if (!this.currentShot) return;
      this.currentShot.boundSceneAssetIds = [];
      this.currentShot.boundSceneNames = [];
      this.emitShots();
    },
    copyCurrentCharacterBindingsToNextShot() {
      if (!this.currentShot || !this.hasNextShot) return;
      const nextShot = this.localShots[this.selectedShotIndex + 1];
      nextShot.boundCharacterAssetIds = this.normalizeStringArray(this.currentShot.boundCharacterAssetIds);
      nextShot.boundCharacterNames = this.normalizeStringArray(this.currentShot.boundCharacterNames);
      this.syncShotCharacterBinding(nextShot);
      this.emitShots();
    },
    copyCurrentSceneBindingsToNextShot() {
      if (!this.currentShot || !this.hasNextShot) return;
      const nextShot = this.localShots[this.selectedShotIndex + 1];
      nextShot.boundSceneAssetIds = this.normalizeStringArray(this.currentShot.boundSceneAssetIds);
      nextShot.boundSceneNames = this.normalizeStringArray(this.currentShot.boundSceneNames);
      this.emitShots();
    },
    pruneShotAssetBindings() {
      if (!this.localShots.length) return;
      const validIds = new Set(this.characterAssets.map((item) => String(item?.id || '').trim()).filter(Boolean));
      const validNames = new Set(this.characterAssets.map((item) => String(item?.name || '').trim()).filter(Boolean));
      const validSceneIds = new Set(this.sceneAssets.map((item) => String(item?.id || '').trim()).filter(Boolean));
      const validSceneNames = new Set(this.sceneAssets.map((item) => String(item?.name || '').trim()).filter(Boolean));
      let changed = false;

      this.localShots.forEach((shot) => {
        const prevIds = this.normalizeStringArray(shot?.boundCharacterAssetIds);
        const prevNames = this.normalizeStringArray(shot?.boundCharacterNames);
        const nextIds = prevIds.filter((id) => validIds.has(id));
        const nextNames = prevNames.filter((name) => validNames.has(name));
        const prevSceneIds = this.normalizeStringArray(shot?.boundSceneAssetIds);
        const prevSceneNames = this.normalizeStringArray(shot?.boundSceneNames);
        const nextSceneIds = prevSceneIds.filter((id) => validSceneIds.has(id));
        const nextSceneNames = prevSceneNames.filter((name) => validSceneNames.has(name));
        if (
          nextIds.length !== prevIds.length ||
          nextNames.length !== prevNames.length ||
          nextSceneIds.length !== prevSceneIds.length ||
          nextSceneNames.length !== prevSceneNames.length
        ) {
          shot.boundCharacterAssetIds = nextIds;
          shot.boundCharacterNames = nextNames;
          this.syncShotCharacterBinding(shot);
          shot.boundSceneAssetIds = nextSceneIds;
          shot.boundSceneNames = nextSceneNames;
          changed = true;
        }
      });

      if (changed) this.emitShots();
    },
    shotDescriptionSnippet(shot) {
      const text = String(
        shot?.sceneNarrative ||
        shot?.scene_script ||
        shot?.shotSummary ||
        shot?.sourceDescription ||
        this.getShotDetailedPlot(shot) ||
        shot?.startFrame?.description ||
        ''
      ).trim();
      if (!text) {
        return '暂无描述';
      }
      return text.length > 46 ? `${text.slice(0, 46)}...` : text;
    },
    shotPromptPreview(shot, maxLines = 3) {
      const text = this.resolveShotPlanPrompt(shot);
      if (!text) return '暂无 Shot Prompt';
      const lines = text
        .replace(/\r/g, '\n')
        .split('\n')
        .map((item) => String(item || '').trim())
        .filter(Boolean);
      if (!lines.length) return '暂无 Shot Prompt';
      const clipped = lines.slice(0, Math.max(1, maxLines));
      const preview = clipped.join('\n');
      return lines.length > clipped.length ? `${preview}\n...` : preview;
    },
    resolveShotVoiceoverText(shot) {
      const safeShot = shot || {};
      return String(
        safeShot.voiceoverText ||
        safeShot.voiceover_text ||
        safeShot.narrationText ||
        safeShot.narration_text ||
        safeShot.narration ||
        ''
      ).trim();
    },
    shotVoiceoverPreview(shot, maxLines = 3) {
      const text = this.resolveShotVoiceoverText(shot);
      if (!text) return '暂无旁白';
      const lines = text
        .replace(/\r/g, '\n')
        .split('\n')
        .map((item) => String(item || '').trim())
        .filter(Boolean);
      if (!lines.length) return '暂无旁白';
      const clipped = lines.slice(0, Math.max(1, maxLines));
      const preview = clipped.join('\n');
      return lines.length > clipped.length ? `${preview}\n...` : preview;
    },
    normalizeTaskStatus(statusValue, { hasVideo = false, hasTaskId = false } = {}) {
      const raw = String(statusValue || '').trim().toLowerCase();
      const normalized = raw.replace(/[\s\-]+/g, '_');
      const hasJob = Boolean(hasTaskId);

      if (hasVideo) return 'succeeded';
      if (!normalized) return hasJob ? 'processing' : '';

      if (
        ['succeeded', 'success', 'completed', 'complete', 'finished', 'done'].includes(normalized) ||
        /success|succeed|complete|finished|done/.test(normalized)
      ) {
        return hasJob ? 'processing' : 'succeeded';
      }
      if (
        ['failed', 'fail', 'error', 'canceled', 'cancelled', 'timeout', 'rejected'].includes(normalized) ||
        /fail|error|cancel|timeout|reject/.test(normalized)
      ) {
        return 'failed';
      }
      if (normalized === 'submitting') return 'submitting';
      if (['submitted', 'submit', 'accepted', 'created'].includes(normalized)) return 'submitted';
      if (
        ['processing', 'running', 'pending', 'queued', 'in_queue', 'in_progress', 'generating'].includes(normalized) ||
        /process|running|pending|queue|in_progress|generating/.test(normalized)
      ) {
        return 'processing';
      }

      if (/^\d+$/.test(normalized)) {
        return hasJob ? 'processing' : '';
      }

      return hasJob ? 'processing' : normalized;
    },
    shotStatusClass(shot) {
      const status = this.normalizeTaskStatus(shot?.videoTask?.status, {
        hasVideo: Boolean(shot?.videoUrl),
        hasTaskId: Boolean(shot?.videoTask?.taskId)
      });
      if (status === 'succeeded' || shot?.videoUrl) return 'ready';
      if (status === 'failed') return 'failed';
      if (status === 'processing' || status === 'submitted' || status === 'submitting') return 'processing';
      return 'idle';
    },
    shotStatusLabel(shot) {
      const status = this.normalizeTaskStatus(shot?.videoTask?.status, {
        hasVideo: Boolean(shot?.videoUrl),
        hasTaskId: Boolean(shot?.videoTask?.taskId)
      });
      if (status === 'succeeded' || shot?.videoUrl) return 'READY';
      if (status === 'failed') return 'FAILED';
      if (status === 'processing' || status === 'submitted' || status === 'submitting') return 'PROCESSING';
      return 'STATIC';
    },
    rowTaskProgress(shot) {
      const safeShot = shot || {};
      const status = this.normalizeTaskStatus(safeShot?.videoTask?.status, {
        hasVideo: Boolean(safeShot?.videoUrl),
        hasTaskId: Boolean(safeShot?.videoTask?.taskId)
      });
      if (status === 'succeeded' || safeShot?.videoUrl) return 100;
      const progress = Number(safeShot?.videoTask?.progress);
      if (Number.isFinite(progress)) {
        return Math.max(0, Math.min(100, Math.round(progress)));
      }
      if (status === 'processing' || status === 'submitted' || status === 'submitting') {
        return 12;
      }
      return 0;
    },
    rowLoadKey(index) {
      return String(index);
    },
    setRowLoadingState(field, index, value) {
      const key = this.rowLoadKey(index);
      const next = { ...(this[field] || {}) };
      if (value) next[key] = true;
      else delete next[key];
      this[field] = next;
    },
    isRowLoadingState(field, index) {
      return Boolean((this[field] || {})[this.rowLoadKey(index)]);
    },
    isStartFrameLoading(index) {
      return this.isRowLoadingState('rowStartFrameLoading', index);
    },
    isEndFrameLoading(index) {
      return this.isRowLoadingState('rowEndFrameLoading', index);
    },
    isVideoLoading(index) {
      return this.isRowLoadingState('rowVideoLoading', index);
    },
    isRefreshLoading(index) {
      return this.isRowLoadingState('rowRefreshLoading', index);
    },
    isAnyRowLoading(index) {
      return this.isStartFrameLoading(index) || this.isEndFrameLoading(index) || this.isVideoLoading(index) || this.isRefreshLoading(index);
    },
    sceneNarrativePreview(shot, maxLines = 3) {
      const text = String(shot?.sceneNarrative || '').trim();
      if (!text) return '暂无剧本剧情';
      const lines = text
        .replace(/\r/g, '\n')
        .split('\n')
        .map((item) => String(item || '').trim())
        .filter(Boolean);
      if (!lines.length) return '暂无剧本剧情';
      const clipped = lines.slice(0, Math.max(1, maxLines));
      const preview = clipped.join('\n');
      return lines.length > clipped.length ? `${preview}\n...` : preview;
    },
    shortUrlText(value, maxLen = 42) {
      const text = String(value || '').trim();
      if (!text) return '未设置';
      if (text.length <= maxLen) return text;
      return `${text.slice(0, maxLen - 3)}...`;
    },
    resolveAssetNamesByIds(assetIds, assets, fallbackNames = []) {
      const idSet = new Set(this.normalizeStringArray(assetIds));
      const resolved = (Array.isArray(assets) ? assets : [])
        .filter((asset) => idSet.has(String(asset?.id || '').trim()))
        .map((asset) => String(asset?.name || '').trim())
        .filter(Boolean);
      const merged = [...resolved, ...this.normalizeStringArray(fallbackNames)];
      return this.normalizeStringArray(merged);
    },
    buildStructuredCharacterBindingFromIdsAndNames(assetIds, names) {
      const ids = this.normalizeStringArray(assetIds);
      const resolvedNames = this.resolveAssetNamesByIds(ids, this.characterAssets, names);
      const bindings = [];
      const matchedNameSet = new Set();

      ids.forEach((id) => {
        const asset = this.characterAssets.find((item) => String(item?.id || '').trim() === id);
        const name = String(asset?.name || '').trim();
        if (name) matchedNameSet.add(name);
        bindings.push({
          character_name: name,
          asset_id: id
        });
      });

      resolvedNames.forEach((name) => {
        if (matchedNameSet.has(name)) return;
        const asset = this.characterAssets.find((item) => String(item?.name || '').trim() === name);
        bindings.push({
          character_name: name,
          asset_id: String(asset?.id || '').trim()
        });
      });

      return this.normalizeCharacterBindingList(bindings);
    },
    syncShotCharacterBinding(shot) {
      if (!shot || typeof shot !== 'object') return;
      const ids = this.normalizeStringArray(shot.boundCharacterAssetIds);
      const names = this.resolveAssetNamesByIds(ids, this.characterAssets, shot.boundCharacterNames);
      shot.boundCharacterAssetIds = ids;
      shot.boundCharacterNames = names;
      shot.character_binding = this.buildStructuredCharacterBindingFromIdsAndNames(ids, names);
    },
    shotCharacterBindingText(shot) {
      const assetNames = this.resolveBoundCharacterAssetsForShot(shot)
        .map((item) => String(item?.name || '').trim())
        .filter(Boolean);
      if (assetNames.length) return assetNames.join('、');
      const fallbackNames = this.normalizeStringArray(shot?.boundCharacterNames);
      return fallbackNames.length ? fallbackNames.join('、') : '未绑定';
    },
    shotSceneBindingText(shot) {
      const assetNames = this.resolveBoundSceneAssetsForShot(shot)
        .map((item) => String(item?.name || '').trim())
        .filter(Boolean);
      if (assetNames.length) return assetNames.join('、');
      const fallbackNames = this.normalizeStringArray(shot?.boundSceneNames);
      return fallbackNames.length ? fallbackNames.join('、') : '未绑定';
    },
    ensureEditDraftBindingArrays() {
      if (!this.editingShotDraft || typeof this.editingShotDraft !== 'object') return;
      this.editingShotDraft.boundCharacterAssetIds = this.normalizeStringArray(this.editingShotDraft.boundCharacterAssetIds);
      this.editingShotDraft.boundCharacterNames = this.normalizeStringArray(this.editingShotDraft.boundCharacterNames);
      this.editingShotDraft.boundSceneAssetIds = this.normalizeStringArray(this.editingShotDraft.boundSceneAssetIds);
      this.editingShotDraft.boundSceneNames = this.normalizeStringArray(this.editingShotDraft.boundSceneNames);
    },
    isCharacterBoundInEdit(asset) {
      this.ensureEditDraftBindingArrays();
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      const idSet = new Set(this.editingShotDraft.boundCharacterAssetIds || []);
      const nameSet = new Set(this.editingShotDraft.boundCharacterNames || []);
      return (assetId && idSet.has(assetId)) || (assetName && nameSet.has(assetName));
    },
    isSceneBoundInEdit(asset) {
      this.ensureEditDraftBindingArrays();
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      const idSet = new Set(this.editingShotDraft.boundSceneAssetIds || []);
      const nameSet = new Set(this.editingShotDraft.boundSceneNames || []);
      return (assetId && idSet.has(assetId)) || (assetName && nameSet.has(assetName));
    },
    toggleCharacterBindingInEdit(asset) {
      this.ensureEditDraftBindingArrays();
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      if (!assetId && !assetName) return;
      const boundIds = this.normalizeStringArray(this.editingShotDraft.boundCharacterAssetIds);
      const boundNames = this.normalizeStringArray(this.editingShotDraft.boundCharacterNames);
      const idIndex = assetId ? boundIds.indexOf(assetId) : -1;
      const nameIndex = assetName ? boundNames.indexOf(assetName) : -1;
      const alreadyBound = idIndex !== -1 || nameIndex !== -1;
      if (alreadyBound) {
        if (idIndex !== -1) boundIds.splice(idIndex, 1);
        if (nameIndex !== -1) boundNames.splice(nameIndex, 1);
      } else {
        if (assetId) boundIds.push(assetId);
        if (assetName) boundNames.push(assetName);
      }
      this.editingShotDraft.boundCharacterAssetIds = this.normalizeStringArray(boundIds);
      this.editingShotDraft.boundCharacterNames = this.normalizeStringArray(boundNames);
    },
    toggleSceneBindingInEdit(asset) {
      this.ensureEditDraftBindingArrays();
      const assetId = String(asset?.id || '').trim();
      const assetName = String(asset?.name || '').trim();
      if (!assetId && !assetName) return;
      const boundIds = this.normalizeStringArray(this.editingShotDraft.boundSceneAssetIds);
      const boundNames = this.normalizeStringArray(this.editingShotDraft.boundSceneNames);
      const idIndex = assetId ? boundIds.indexOf(assetId) : -1;
      const nameIndex = assetName ? boundNames.indexOf(assetName) : -1;
      const alreadyBound = idIndex !== -1 || nameIndex !== -1;
      if (alreadyBound) {
        if (idIndex !== -1) boundIds.splice(idIndex, 1);
        if (nameIndex !== -1) boundNames.splice(nameIndex, 1);
      } else {
        if (assetId) boundIds.push(assetId);
        if (assetName) boundNames.push(assetName);
      }
      this.editingShotDraft.boundSceneAssetIds = this.normalizeStringArray(boundIds);
      this.editingShotDraft.boundSceneNames = this.normalizeStringArray(boundNames);
    },
    bindAllCharactersForEdit() {
      const ids = this.characterAssets.map((item) => String(item?.id || '').trim()).filter(Boolean);
      const names = this.characterAssets.map((item) => String(item?.name || '').trim()).filter(Boolean);
      this.editingShotDraft.boundCharacterAssetIds = this.normalizeStringArray(ids);
      this.editingShotDraft.boundCharacterNames = this.normalizeStringArray(names);
    },
    clearCharactersForEdit() {
      this.editingShotDraft.boundCharacterAssetIds = [];
      this.editingShotDraft.boundCharacterNames = [];
    },
    bindAllScenesForEdit() {
      const ids = this.sceneAssets.map((item) => String(item?.id || '').trim()).filter(Boolean);
      const names = this.sceneAssets.map((item) => String(item?.name || '').trim()).filter(Boolean);
      this.editingShotDraft.boundSceneAssetIds = this.normalizeStringArray(ids);
      this.editingShotDraft.boundSceneNames = this.normalizeStringArray(names);
    },
    clearScenesForEdit() {
      this.editingShotDraft.boundSceneAssetIds = [];
      this.editingShotDraft.boundSceneNames = [];
    },
    openEditShotDialog(index) {
      if (index < 0 || index >= this.localShots.length) return;
      const shot = this.localShots[index] || {};
      const structuredBindings = this.normalizeCharacterBindingList(shot?.character_binding || shot?.characterBinding);
      this.selectedShotIndex = index;
      this.editingShotIndex = index;
      this.shotPromptEnhancing = false;
      this.voiceoverGenerating = false;
      this.editingShotDraft = {
        title: String(shot?.title || '').trim(),
        duration: String(shot?.duration || '5s').trim() || '5s',
        sceneNarrative: String(shot?.sceneNarrative || '').trim(),
        shotPrompt: this.resolveShotPlanPrompt(shot),
        voiceoverText: this.resolveShotVoiceoverText(shot),
        startFrameImageUrl: String(shot?.startFrame?.image_url || '').trim(),
        endFrameImageUrl: String(shot?.endFrame?.image_url || '').trim(),
        startFrameDescription: String(shot?.startFrame?.description || '').trim(),
        endFrameDescription: String(shot?.endFrame?.description || '').trim(),
        startFramePrompt: String(shot?.startFrame?.enhanced_prompt || '').trim(),
        endFramePrompt: String(shot?.endFrame?.enhanced_prompt || '').trim(),
        boundCharacterAssetIds: this.normalizeStringArray([
          ...(shot?.boundCharacterAssetIds || []),
          ...structuredBindings.map((item) => String(item.asset_id || '').trim()).filter(Boolean)
        ]),
        boundCharacterNames: this.normalizeStringArray([
          ...(shot?.boundCharacterNames || []),
          ...structuredBindings.map((item) => String(item.character_name || '').trim()).filter(Boolean)
        ]),
        boundSceneAssetIds: this.normalizeStringArray(shot?.boundSceneAssetIds),
        boundSceneNames: this.normalizeStringArray(shot?.boundSceneNames)
      };
      this.editDialogVisible = true;
    },
    closeEditShotDialog() {
      this.editDialogVisible = false;
      this.shotPromptEnhancing = false;
      this.voiceoverGenerating = false;
      this.editingShotIndex = -1;
    },
    saveEditShotDialog() {
      const index = this.editingShotIndex;
      if (index < 0 || index >= this.localShots.length) {
        this.closeEditShotDialog();
        return;
      }
      const shot = this.localShots[index];
      const draft = this.editingShotDraft || {};
      if (!shot.startFrame) shot.startFrame = { description: '', enhanced_prompt: '', image_url: '' };
      if (!shot.endFrame) shot.endFrame = { description: '', enhanced_prompt: '', image_url: '' };

      shot.title = String(draft.title || '').trim() || `镜头 ${index + 1}`;
      shot.duration = String(draft.duration || '').trim() || '5s';
      shot.sceneNarrative = String(draft.sceneNarrative || '').trim();
      shot.prompt = this.sanitizeFramePromptText(String(draft.shotPrompt || '').trim());
      shot.voiceoverText = String(draft.voiceoverText || '').trim();
      shot.startFrame.image_url = this.normalizeImageUrl(draft.startFrameImageUrl);
      shot.endFrame.image_url = this.normalizeImageUrl(draft.endFrameImageUrl);
      shot.startFrame.description = String(draft.startFrameDescription || '').trim();
      shot.endFrame.description = String(draft.endFrameDescription || '').trim();
      shot.startFrame.enhanced_prompt = String(draft.startFramePrompt || '').trim();
      shot.endFrame.enhanced_prompt = String(draft.endFramePrompt || '').trim();
      shot.boundCharacterAssetIds = this.normalizeStringArray(draft.boundCharacterAssetIds);
      shot.boundCharacterNames = this.resolveAssetNamesByIds(
        shot.boundCharacterAssetIds,
        this.characterAssets,
        draft.boundCharacterNames
      );
      this.syncShotCharacterBinding(shot);
      shot.boundSceneAssetIds = this.normalizeStringArray(draft.boundSceneAssetIds);
      shot.boundSceneNames = this.resolveAssetNamesByIds(
        shot.boundSceneAssetIds,
        this.sceneAssets,
        draft.boundSceneNames
      );
      this.ensureShotPlanPrompt(shot);

      this.selectedShotIndex = index;
      this.handleSceneNarrativeChange({ preserveFramePrompts: true });
      this.closeEditShotDialog();
    },
    openDeleteShotDialog(index) {
      if (index < 0 || index >= this.localShots.length) return;
      this.pendingDeleteIndex = index;
      this.deleteConfirmVisible = true;
    },
    cancelDeleteShotDialog() {
      this.deleteConfirmVisible = false;
      this.pendingDeleteIndex = -1;
    },
    performDeleteShotAtIndex(index) {
      if (index < 0 || index >= this.localShots.length) return;
      this.localShots.splice(index, 1);
      if (!this.localShots.length) this.selectedShotIndex = -1;
      else if (this.selectedShotIndex >= this.localShots.length) this.selectedShotIndex = this.localShots.length - 1;
      else if (this.selectedShotIndex > index) this.selectedShotIndex -= 1;
      this.emitShots();
    },
    confirmDeleteShotDialog() {
      const targetIndex = this.pendingDeleteIndex;
      this.cancelDeleteShotDialog();
      this.performDeleteShotAtIndex(targetIndex);
    },
    autoPlayCurrentVideo() {
      this.$nextTick(() => {
        const player = this.$refs.currentVideoPlayer;
        if (player && typeof player.load === 'function') player.load();
        if (player && typeof player.play === 'function') player.play().catch(() => {});
      });
    },
    findShotIndexByTaskId(taskId) {
      const normalizedTaskId = String(taskId || '').trim();
      if (!normalizedTaskId) return -1;
      return this.localShots.findIndex((item) => String(item?.videoTask?.taskId || '').trim() === normalizedTaskId);
    },
    applyTaskUpdateToShot(shotIndex, data) {
      if (shotIndex < 0 || shotIndex >= this.localShots.length) return;
      const shot = this.localShots[shotIndex];
      const taskId = String(data?.task_id || shot?.videoTask?.taskId || '').trim();
      const incomingVideoUrl = this.normalizeVideoUrl(data?.video_url) || this.extractVideoUrl(data?.raw_response || data);
      const status = this.normalizeTaskStatus(data?.status || (data?.error ? 'error' : '') || shot?.videoTask?.status, {
        hasVideo: Boolean(incomingVideoUrl || shot?.videoUrl),
        hasTaskId: Boolean(taskId)
      });
      const incomingProgress = Number(data?.progress);
      const previousProgress = Number(shot?.videoTask?.progress || 0);
      let progress = Number.isFinite(incomingProgress) ? incomingProgress : previousProgress;

      if (status === 'succeeded') progress = 100;
      else if (status === 'failed') progress = 0;
      else {
        if (!Number.isFinite(progress) || progress <= 0) progress = Math.max(8, previousProgress || 8);
        const floor = status === 'submitting' ? 3 : (status === 'submitted' ? 8 : 12);
        const ceiling = status === 'processing' ? 95 : 90;
        progress = Math.min(ceiling, Math.max(floor, Math.max(previousProgress, progress)));
      }

      shot.videoTask = {
        taskId,
        status,
        message: String(data?.message || data?.error || shot?.videoTask?.message || ''),
        progress: Math.max(0, Math.min(100, Math.round(progress))),
        provider: String(data?.provider || shot?.videoTask?.provider || this.videoProvider || 'openai').trim().toLowerCase() || 'openai',
        reqKey: String(data?.req_key || shot?.videoTask?.reqKey || '').trim(),
        queryUrl: String(data?.query_url || shot?.videoTask?.queryUrl || '').trim(),
        queryMethod: String(data?.query_method || shot?.videoTask?.queryMethod || '').trim().toUpperCase()
      };

      if (incomingVideoUrl && status !== 'failed') shot.videoUrl = incomingVideoUrl;
      if (status === 'succeeded' && shot.videoUrl) {
        const continuityPrompt = 'same scene, same composition, consistent character, slow motion, continuous motion, same character position, same background';
        const lastFrameUrl = this.normalizeImageUrl(shot?.endFrame?.image_url || '');
        shot.videoTail = this.normalizeVideoTail(
          {
            tail_seconds: 0.5,
            overlap_seconds: 0.5,
            last_frame_url: lastFrameUrl,
            source: 'end_frame',
            transition: 'crossfade'
          },
          lastFrameUrl
        );
        const nextIndex = shotIndex + 1;
        if (nextIndex < this.localShots.length && this.isUsableImageUrl(lastFrameUrl)) {
          const nextShot = this.localShots[nextIndex];
          const nextStartFrame = {
            ...(nextShot.startFrame || {}),
            image_url: lastFrameUrl,
            enhanced_prompt: continuityPrompt,
            reference_images: [lastFrameUrl],
            reference_image_used: lastFrameUrl,
            generation_mode: 'continuity-from-previous-end-frame'
          };
          this.localShots.splice(nextIndex, 1, {
            ...nextShot,
            startFrame: nextStartFrame,
            endFrame: { ...(nextShot.endFrame || {}) }
          });
        }
        this.selectedShotIndex = shotIndex;
        this.autoPlayCurrentVideo();
      }
      this.emitShots();
    },
    cancelTaskAndNotify(shotIndex, message) {
      if (shotIndex < 0 || shotIndex >= this.localShots.length) return;
      const shot = this.localShots[shotIndex];
      const text = String(message || '任务查询失败').trim() || '任务查询失败';
      shot.videoTask = {
        taskId: String(shot?.videoTask?.taskId || ''),
        status: 'failed',
        message: `已取消查询：${text}`,
        progress: Math.max(0, Math.min(100, Number(shot?.videoTask?.progress || 0))),
        provider: String(shot?.videoTask?.provider || this.videoProvider || 'openai').trim().toLowerCase() || 'openai',
        reqKey: String(shot?.videoTask?.reqKey || '').trim(),
        queryUrl: String(shot?.videoTask?.queryUrl || '').trim(),
        queryMethod: String(shot?.videoTask?.queryMethod || '').trim().toUpperCase()
      };
      this.emitShots();
      alert(`任务失败并已取消：${text}`);
    },
    shotFromScene(scene, index) {
      return this.shotsFromScene(scene, index)[0] || this.normalizeShot({
        sceneNo: this.sceneNoFromScene(scene, index + 1),
        title: `场次 ${this.sceneNoFromScene(scene, index + 1)}`,
        duration: scene?.duration || '5s'
      });
    },
    buildShotNarrativeSummary(shot) {
      const safe = shot || {};
      const parts = [
        String(safe?.sceneNarrative || safe?.scene_script || '').trim(),
        String(safe?.sourceDescription || '').trim(),
        String(safe?.shotSummary || '').trim(),
        String(safe?.detailedShotDescription || '').trim()
      ].filter(Boolean);
      if (!parts.length) {
        const title = String(safe?.title || '').trim();
        const duration = String(safe?.duration || '').trim();
        if (title) parts.push(`镜头标题：${title}`);
        if (duration) parts.push(`镜头时长：${duration}`);
      }
      const merged = parts.join('，');
      return this.summarizeForFrame(merged, 180);
    },
    buildStoryContextForShot(shot) {
      const safeShot = shot || {};
      const currentIndex = this.localShots.findIndex((item) => item === safeShot);
      const previousShot = currentIndex > 0 ? this.localShots[currentIndex - 1] : null;
      const nextShot = currentIndex >= 0 && currentIndex < this.localShots.length - 1 ? this.localShots[currentIndex + 1] : null;
      const lines = [];
      const currentSummary = this.buildShotNarrativeSummary(safeShot);
      const previousSummary = this.buildShotNarrativeSummary(previousShot);
      const nextSummary = this.buildShotNarrativeSummary(nextShot);

      if (previousSummary) lines.push(`上一镜头：${previousSummary}`);
      if (currentSummary) lines.push(`当前镜头：${currentSummary}`);
      if (nextSummary) lines.push(`下一镜头：${nextSummary}`);
      const storyArc = [
        previousSummary ? `前情${previousSummary}` : '',
        currentSummary ? `本镜头${currentSummary}` : '',
        nextSummary ? `后续${nextSummary}` : '',
      ].filter(Boolean);
      if (storyArc.length) lines.push(`故事推进：${storyArc.join('；')}`);
      return lines.join('\n');
    },
    buildCharacterConsistencyBlock(shot = null) {
      const list = this.resolveBoundCharacterAssetsForShot(shot).slice(0, 4);
      if (!list.length) return '';

      const lines = list.map((item, idx) => {
        const name = String(item?.name || `角色${idx + 1}`).trim();
        return `- ${name}：${this.buildCharacterIdentitySummary(item, idx)}`;
      });

      const safeShot = shot || {};
      const hasBinding = this.hasExplicitCharacterBindings(safeShot);
      const title = hasBinding
        ? '角色一致性约束（仅当前镜头绑定角色）：'
        : '角色一致性约束（未绑定时默认应用全部角色）：';

      return [
        title,
        ...lines
      ].join('\n');
    },
    buildCharacterIdentitySummary(asset, index = 0) {
      const safe = asset || {};
      const wardrobe = String(safe?.wardrobe || '').trim();
      const source = this.summarizeForFrame(String(safe?.source_description || '').trim(), 90);
      const prompt = this.summarizeForFrame(String(safe?.prompt || '').trim(), 90);
      const parts = [];
      if (source) parts.push(`外观锚点：${source}`);
      if (wardrobe) parts.push(`服装锚点：${wardrobe}`);
      if (prompt) parts.push(`视觉锚点：${prompt}`);
      if (!parts.length) parts.push('保持同一张脸、同一发型、同一服装体系');
      return parts.join(' | ');
    },
    buildCharacterIdentityRules(shot = null) {
      const list = this.resolveBoundCharacterAssetsForShot(shot).slice(0, 4);
      if (!list.length) return '';

      const roleLines = list.map((item, idx) => {
        const name = String(item?.name || `角色${idx + 1}`).trim();
        return `${idx + 1}. ${name} = ${this.buildCharacterIdentitySummary(item, idx)}`;
      });
      const guardLines = [
        '身份锁定要求：同名角色始终对应同一张脸、同一发型、同一服装体系、同一体型和同一道具归属。',
        '严禁角色互换：不能把甲角色的脸、胡须、服装、武器、站位或表情错误地给到乙角色。',
      ];
      if (list.length > 1) {
        const names = list.map((item, idx) => String(item?.name || `角色${idx + 1}`).trim()).filter(Boolean);
        if (names.length > 1) {
          guardLines.push(`当前镜头多角色同框时，必须明确区分 ${names.join('、')}，不得把其中任何两人混成同一个人。`);
        }
      }
      return ['角色身份锁定：', ...roleLines, ...guardLines].join('\n');
    },
    hasMultipleExplicitCharacterBindings(shot) {
      const list = this.resolveBoundCharacterAssetsForShot(shot, { explicitOnly: true });
      return list.length > 1;
    },
    buildSceneConsistencyBlock(shot = null) {
      const list = this.resolveBoundSceneAssetsForShot(shot).slice(0, 2);
      if (!list.length) return '';

      const lines = list.map((item, idx) => {
        const name = String(item?.name || `场景${idx + 1}`).trim();
        const prompt = String(item?.prompt || '').trim();
        const detail = prompt || '保持环境布局、建筑风格、色调和光影一致';
        return `- ${name}：${detail}`;
      });

      return ['场景一致性约束（仅当前镜头绑定场景）：', ...lines].join('\n');
    },
    buildVideoPromptScaffold(shot) {
      const safeShot = shot || {};
      const title = String(safeShot?.title || '当前镜头').trim() || '当前镜头';
      const duration = String(safeShot?.duration || '5s').trim() || '5s';
      return [
        `镜头任务：仅生成「${title}」这一段，时长约 ${duration}，不要跨到上一镜头尾声或下一镜头开场。`,
        '视觉风格：严格中国动漫风 / 国漫风电影感，完整构图，主体清晰，景别与焦点明确，光影层次自然，空间关系稳定。',
        '调度结构：开场先建立人物与空间站位，中段推进动作与情绪反应，结尾给出清晰收势并留可衔接动作钩子。',
        '叙事要求：必须承接前一镜头的状态变化，并把故事推向下一步，不要只做静态摆拍。',
        '一致性要求：同一角色的脸型、发型、服装、道具、站位和镜头轴线必须稳定，前后帧要处在同一场景几何中。',
        '质量约束：禁止分屏、多格漫画、拼贴、字幕、水印和英文文本，动作与表演要有物理反馈与节奏变化。',
        'Audio language lock: mandarin speech, chinese dialogue, no english voice.'
      ].join('\n');
    },
    buildLowInfoShotCompensation(shot) {
      const safeShot = shot || {};
      const title = String(safeShot?.title || '当前镜头').trim() || '当前镜头';
      const duration = String(safeShot?.duration || '5s').trim() || '5s';
      const prevState = this.resolveShotPrevState(safeShot);
      const startVisual = this.sanitizeFramePromptText(String(safeShot?.startFrame?.description || '').trim());
      const endVisual = this.sanitizeFramePromptText(String(safeShot?.endFrame?.description || '').trim());
      const parts = [
        `镜头补全：当前镜头为「${title}」，目标时长 ${duration}。`
      ];
      if (prevState) parts.push(`继承状态：${prevState}`);
      if (startVisual) parts.push(`起始状态：${startVisual}`);
      if (endVisual) parts.push(`目标状态：${endVisual}`);
      parts.push('连续性要求：空间连续且物理状态连续，禁止跳帧式突变。');
      parts.push('请明确主体、动作、视线、机位变化和收束动作，确保该镜头可以独立成立。');
      return parts.join('\n');
    },
    composeShotPrompt(shot) {
      const safeShot = shot || {};
      const narrationText = this.resolveShotVoiceoverText(safeShot);
      const consistencyBlock = this.buildCharacterConsistencyBlock(safeShot);
      const identityRules = this.buildCharacterIdentityRules(safeShot);
      const sceneConsistencyBlock = this.buildSceneConsistencyBlock(safeShot);
      const continuityBlock = this.buildContinuityRules(safeShot);
      const storyContext = this.buildStoryContextForShot(safeShot);
      const sceneNarrative = String(
        safeShot?.sceneNarrative ||
        this.buildSceneNarrativeFromFields({
          sourceDescription: safeShot?.sourceDescription,
          shotSummary: safeShot?.shotSummary,
          detailedShotDescription: safeShot?.detailedShotDescription,
          detailedPlot: this.getShotDetailedPlot(safeShot),
          actionArc: safeShot?.actionArc || safeShot?.action_arc,
          emotionArc: safeShot?.emotionArc || safeShot?.emotion_arc,
          rhythmPlan: safeShot?.rhythmPlan || safeShot?.rhythm_plan,
          startFrameGoal: safeShot?.startFrameGoal || safeShot?.start_frame_goal,
          prevState: safeShot?.prevState || safeShot?.prev_state,
          motionInstruction: this.resolveShotMotionInstruction(safeShot),
          targetState: this.resolveShotTargetState(safeShot),
          visualAnchor: safeShot?.visualAnchor || safeShot?.visual_anchor,
          continuityHint: safeShot?.continuityHint || safeShot?.continuity_hint
        })
      ).trim();
      const parsedNarrative = this.parseSceneNarrative(sceneNarrative, {
        sourceDescription: safeShot?.sourceDescription,
        shotSummary: safeShot?.shotSummary,
        detailedShotDescription: safeShot?.detailedShotDescription,
        detailedPlot: this.getShotDetailedPlot(safeShot),
        actionArc: safeShot?.actionArc || safeShot?.action_arc,
        emotionArc: safeShot?.emotionArc || safeShot?.emotion_arc,
        rhythmPlan: safeShot?.rhythmPlan || safeShot?.rhythm_plan,
        startFrameGoal: safeShot?.startFrameGoal || safeShot?.start_frame_goal,
        prevState: safeShot?.prevState || safeShot?.prev_state,
        motionInstruction: this.resolveShotMotionInstruction(safeShot),
        targetState: this.resolveShotTargetState(safeShot),
        visualAnchor: safeShot?.visualAnchor || safeShot?.visual_anchor,
        continuityHint: safeShot?.continuityHint || safeShot?.continuity_hint
      });
      const startVisual = this.sanitizeFramePromptText(String(safeShot?.startFrame?.enhanced_prompt || safeShot?.startFrame?.description || '').trim());
      const endVisual = this.sanitizeFramePromptText(String(safeShot?.endFrame?.enhanced_prompt || safeShot?.endFrame?.description || '').trim());
      const detailedPlot = this.getShotDetailedPlot(safeShot);
      const structuredSignals = [
        sceneNarrative,
        detailedPlot,
        parsedNarrative.prevState,
        parsedNarrative.motionInstruction,
        parsedNarrative.startFrameGoal,
        parsedNarrative.targetState,
        parsedNarrative.visualAnchor,
        parsedNarrative.continuityHint,
        startVisual,
        endVisual
      ].filter(Boolean).length;
      const narrativeLength = [sceneNarrative, detailedPlot].join('\n').length;
      const shouldAddScaffold = structuredSignals <= 3 || narrativeLength < 180;
      const sceneLines = [
        `- 镜头：${String(safeShot?.title || '当前镜头').trim() || '当前镜头'}`,
        `- 时长：${String(safeShot?.duration || '5s').trim() || '5s'}`,
      ];
      if (storyContext) sceneLines.push(`- 叙事承接：${storyContext}`);
      if (sceneNarrative) sceneLines.push(`- 镜头脚本：${sceneNarrative}`);

      const characterLines = [];
      if (consistencyBlock) characterLines.push(`- ${consistencyBlock}`);
      if (identityRules) characterLines.push(`- ${identityRules}`);
      if (sceneConsistencyBlock) characterLines.push(`- ${sceneConsistencyBlock}`);
      if (!characterLines.length) characterLines.push('- 当前镜头角色需保持身份和外观连续。');

      const actionLines = [];
      if (Array.isArray(parsedNarrative.actionArc) && parsedNarrative.actionArc.length) {
        actionLines.push(`- 动作节拍：${parsedNarrative.actionArc.join('；')}`);
      }
      if (parsedNarrative.prevState) actionLines.push(`- 上一状态：${parsedNarrative.prevState}`);
      if (parsedNarrative.motionInstruction) actionLines.push(`- 动作指令：${parsedNarrative.motionInstruction}`);
      if (detailedPlot) actionLines.push(`- 详细剧情：${detailedPlot}`);
      if (parsedNarrative.startFrameGoal) actionLines.push(`- 起始帧目标：${parsedNarrative.startFrameGoal}`);
      if (parsedNarrative.targetState) actionLines.push(`- 目标状态：${parsedNarrative.targetState}`);
      if (parsedNarrative.continuityHint) actionLines.push(`- 下一镜头方向：${parsedNarrative.continuityHint}`);
      if (Array.isArray(parsedNarrative.emotionArc) && parsedNarrative.emotionArc.length) {
        actionLines.push(`- 情绪对应动作：${parsedNarrative.emotionArc.join('；')}`);
      }
      if (!actionLines.length) actionLines.push('- 动作必须体现建立 -> 推进 -> 收束。');

      const cameraLines = [];
      if (continuityBlock) cameraLines.push(`- ${continuityBlock}`);
      if (startVisual) cameraLines.push(`- 起始画面：${startVisual}`);
      if (endVisual) cameraLines.push(`- 目标状态画面：${endVisual}`);
      if (parsedNarrative.visualAnchor) cameraLines.push(`- 视觉锚点：${parsedNarrative.visualAnchor}`);
      if (shouldAddScaffold) cameraLines.push(`- ${this.buildVideoPromptScaffold(safeShot)}`);
      if (structuredSignals <= 2) cameraLines.push(`- ${this.buildLowInfoShotCompensation(safeShot)}`);
      cameraLines.push('- 运镜要求：景别、机位、运动路径清晰，结尾动作不重复下一镜头开场。');

      const moodLines = [];
      if (Array.isArray(parsedNarrative.emotionArc) && parsedNarrative.emotionArc.length) {
        moodLines.push(`- 情绪节拍：${parsedNarrative.emotionArc.join('；')}`);
      } else {
        moodLines.push('- 情绪需有起点、转折、落点，不得平铺。');
      }
      if (this.generateAudio) {
        moodLines.push('- 音频：全程中文普通话对白与旁白，禁止英文口播。');
        moodLines.push('- Audio language lock: mandarin speech, chinese dialogue, no english voice.');
      }
      if (narrationText) {
        moodLines.push(`- 旁白文案：${narrationText}`);
      }

      const constraintsLines = [
        '- 单画幅连续视频，禁止分屏、多格漫画、拼贴、字幕、logo、水印和英文文本。',
        '- 单镜头必须单人物、单动作、单空间，禁止人物切换、景别跳变、空间跳变。',
        '- 若出现对话转行动或角色切换，必须拆到相邻镜头，不得并入同一镜头。',
        '- 动作推进必须有因果，角色视线、站位与空间方位保持连续。',
      ];

      const sections = [
        ['Scene', sceneLines],
        ['Character', characterLines],
        ['Action', actionLines],
        ['Camera', cameraLines],
        ['Mood', moodLines],
        ['Constraints', constraintsLines],
      ];
      return sections
        .map(([title, lines]) => `${title}:\n${(lines || []).filter(Boolean).join('\n')}`)
        .join('\n\n');
    },
    appendDialogueToPrompt(basePrompt, shot) {
      const normalizedBasePrompt = String(basePrompt || '').trim();
      const detailedPlot = this.getShotDetailedPlot(shot);
      const consistencyBlock = this.buildCharacterConsistencyBlock(shot);
      const identityRules = this.buildCharacterIdentityRules(shot);
      const sceneConsistencyBlock = this.buildSceneConsistencyBlock(shot);
      const parts = [];
      if (consistencyBlock) parts.push(consistencyBlock);
      if (identityRules) parts.push(identityRules);
      if (sceneConsistencyBlock) parts.push(sceneConsistencyBlock);
      if (detailedPlot) parts.push(`详细剧情：\n${detailedPlot}`);
      if (normalizedBasePrompt) parts.push(normalizedBasePrompt);
      return parts.join('\n').trim();
    },
    sanitizeFramePromptText(text) {
      let value = String(text || '').trim();
      if (!value) return '';
      value = value
        .replace(/\r/g, '\n')
        .replace(/(?:^|\n)\s*\d+\s*[\.\、\)]\s*/g, '\n')
        .replace(/panel\s*\d+/ig, '')
        .replace(/wide establishing/ig, '')
        .replace(/medium action/ig, '')
        .replace(/close up/ig, '')
        .replace(/详细剧情[:：]?/g, '')
        .replace(/镜头部署[:：]?/g, '')
        .replace(/分镜(?:调度|部署)?[:：]?/g, '')
        .replace(/shot\s*plan[:：]?/ig, '')
        .replace(/\n+/g, '，')
        .replace(/，+/g, '，')
        .trim();
      return value;
    },
    escapeRegExp(value) {
      return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },
    stripBoundCharacterNamesFromText(text, shot) {
      let value = String(text || '').trim();
      if (!value) return '';
      const structuredBindings = this.normalizeCharacterBindingList(shot?.character_binding || shot?.characterBinding);
      const boundNames = this.normalizeStringArray([
        ...(shot?.boundCharacterNames || []),
        ...structuredBindings.map((item) => String(item.character_name || '').trim()),
        ...this.resolveBoundCharacterAssetsForShot(shot).map((item) => String(item?.name || '').trim()).filter(Boolean)
      ]);
      boundNames.forEach((name) => {
        if (!name || name.length < 2) return;
        const escaped = this.escapeRegExp(name);
        value = value.replace(new RegExp(escaped, 'g'), '角色');
      });
      return value;
    },
    extractAssetPrimaryReferenceImage(asset) {
      const candidates = [];
      const safeAsset = asset && typeof asset === 'object' ? asset : {};
      if (Array.isArray(safeAsset.images) && safeAsset.images.length) {
        const first = safeAsset.images[0];
        if (typeof first === 'string') candidates.push(first);
        else if (first && typeof first === 'object') {
          candidates.push(first.image_url, first.url, first.src);
        }
      }
      if (Array.isArray(safeAsset.reference_images) && safeAsset.reference_images.length) {
        candidates.push(safeAsset.reference_images[0]);
      }
      if (Array.isArray(safeAsset.referenceImages) && safeAsset.referenceImages.length) {
        candidates.push(safeAsset.referenceImages[0]);
      }
      candidates.push(safeAsset.image_url, safeAsset.imageUrl, safeAsset.url);

      for (const item of candidates) {
        const normalized = this.normalizeImageUrl(item);
        if (this.isUsableImageUrl(normalized)) return normalized;
      }
      return '';
    },
    collectCharacterReferenceImagesForShot(shot) {
      const references = [];
      const pushReference = (value) => {
        const url = this.normalizeImageUrl(value);
        if (!this.isUsableImageUrl(url)) return;
        if (!references.includes(url)) references.push(url);
      };
      const structuredBindings = this.normalizeCharacterBindingList(shot?.character_binding || shot?.characterBinding);
      if (structuredBindings.length) {
        structuredBindings.forEach((binding) => {
          const targetId = String(binding.asset_id || '').trim();
          const targetName = String(binding.character_name || '').trim();
          const asset = this.characterAssets.find((item) => {
            const assetId = String(item?.id || '').trim();
            const assetName = String(item?.name || '').trim();
            if (targetId && assetId === targetId) return true;
            if (!targetId && targetName && assetName === targetName) return true;
            return false;
          });
          if (asset) {
            pushReference(this.extractAssetPrimaryReferenceImage(asset));
          }
        });
      }
      this.resolveBoundCharacterAssetsForShot(shot, { explicitOnly: true }).forEach((asset) => {
        pushReference(this.extractAssetPrimaryReferenceImage(asset));
      });
      return references.slice(0, 4);
    },
    collectSceneReferenceImagesForShot(shot) {
      const references = [];
      const pushReference = (value) => {
        const url = this.normalizeImageUrl(value);
        if (!this.isUsableImageUrl(url)) return;
        if (!references.includes(url)) references.push(url);
      };
      this.resolveBoundSceneAssetsForShot(shot).forEach((asset) => {
        pushReference(this.extractAssetPrimaryReferenceImage(asset));
      });
      return references.slice(0, 2);
    },
    buildSceneVisualHintForFrame(shot) {
      const sceneAssetHints = this.resolveBoundSceneAssetsForShot(shot).map((asset) => {
        const prompt = this.sanitizeFramePromptText(String(asset?.prompt || '').trim());
        return prompt;
      }).filter(Boolean);
      const fallback = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(
          String(shot?.sourceDescription || shot?.detailedShotDescription || shot?.sceneNarrative || '').trim(),
          shot
        )
      );
      const merged = [sceneAssetHints.join('，'), fallback].filter(Boolean).join('，');
      return this.summarizeForFrame(merged, 140);
    },
    buildActionVisualHintForFrame(shot, frameKey) {
      const shotPrompt = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(String(shot?.prompt || '').trim(), shot)
      );
      const frameDescription = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(String((shot?.[frameKey] || {}).description || '').trim(), shot)
      );
      const beat = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(this.extractShotDeploymentBeat(shot, frameKey), shot)
      );
      const detailedPlot = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(this.getShotDetailedPlot(shot), shot)
      );
      return this.summarizeForFrame([shotPrompt, frameDescription, beat, detailedPlot].filter(Boolean).join('，'), 140);
    },
    buildCameraVisualHintForFrame(shot, frameKey) {
      const shotSize = this.sanitizeFramePromptText(String(shot?.ShotSize || shot?.shotSize || '').trim());
      const camera = this.sanitizeFramePromptText(String(shot?.Camera || shot?.camera || '').trim());
      const merged = [shotSize, camera].filter(Boolean).join(', ');
      return merged || 'eye level, slow push-in';
    },
    buildFrameVisualPrompt(shot, frameKey) {
      const shotPrompt = this.summarizeForFrame(
        this.sanitizeFramePromptText(
          this.stripBoundCharacterNamesFromText(String(shot?.prompt || '').trim(), shot)
        ),
        160
      );
      const environment = this.buildSceneVisualHintForFrame(shot) || 'ancient chinese mountain gate, stone stairs';
      const action = this.buildActionVisualHintForFrame(shot, frameKey) || (
        frameKey === 'startFrame' ? 'standing pose, pause before movement' : 'changed pose, action settled'
      );
      const camera = this.buildCameraVisualHintForFrame(shot, frameKey);
      const continuityRule = frameKey === 'endFrame'
        ? 'same scene, same background, consistent composition, same camera framing, slight movement, subtle motion, smooth transition, no abrupt jump'
        : 'same scene, consistent character, stable composition';
      const parts = [
        shotPrompt,
        `environment: ${environment}`,
        `action: ${action}`,
        `camera: ${camera}`,
        continuityRule,
        this.buildPremiumFrameStyleTags(frameKey),
        'single frame'
      ];
      return parts.filter(Boolean).join(', ');
    },
    buildFrameImagePrompt(shot, frameKey) {
      return this.buildFrameVisualPrompt(shot, frameKey);
    },
    buildCharacterFrameHints(shot) {
      const assets = this.resolveBoundCharacterAssetsForShot(shot).slice(0, 4);
      if (!assets.length) return '';
      return assets.map((item, index) => {
        const name = String(item?.name || `角色${index + 1}`).trim();
        const detail = this.buildCharacterIdentitySummary(item, index);
        return `${name} ${detail}`;
      }).join('；');
    },
    buildSceneFrameHints(shot) {
      const assets = this.resolveBoundSceneAssetsForShot(shot).slice(0, 2);
      if (!assets.length) return '';
      return assets.map((item, index) => {
        const name = String(item?.name || `场景${index + 1}`).trim();
        const prompt = String(item?.prompt || '').trim();
        const detail = prompt || '保持空间布局、建筑纹理、光线方向和色调一致';
        return `${name} ${detail}`;
      }).join('；');
    },
    buildFrameReferenceImages(shotIndex, frameKey) {
      if (shotIndex < 0 || shotIndex >= this.localShots.length) return [];

      const shot = this.localShots[shotIndex] || {};
      const characterReferences = this.collectCharacterReferenceImagesForShot(shot);
      if (this.hasExplicitCharacterBindings(shot)) {
        return characterReferences;
      }
      return this.collectSceneReferenceImagesForShot(shot);
    },
    buildCompactFramePrompt(shot, frameKey) {
      const shotPrompt = this.summarizeForFrame(
        this.sanitizeFramePromptText(
          this.stripBoundCharacterNamesFromText(String(shot?.prompt || '').trim(), shot)
        ),
        120
      );
      const action = this.buildActionVisualHintForFrame(shot, frameKey);
      const camera = this.buildCameraVisualHintForFrame(shot, frameKey);
      const continuityRule = frameKey === 'endFrame'
        ? 'same scene, same background, same composition, same camera framing, slight movement'
        : 'same scene, consistent character';
      return [
        shotPrompt || action,
        `camera: ${camera}`,
        continuityRule,
        this.buildPremiumFrameStyleTags(frameKey),
        'single frame'
      ].filter(Boolean).join(', ');
    },
    buildSafeFramePrompt(shot, frameKey) {
      const environment = this.buildSceneVisualHintForFrame(shot) || 'ancient chinese courtyard';
      const action = this.buildActionVisualHintForFrame(shot, frameKey) || 'subtle body movement';
      const continuityRule = frameKey === 'endFrame'
        ? 'same scene, same background, same composition, subtle motion'
        : 'same scene, consistent character, stable composition';
      return [
        `environment: ${environment}`,
        `action: ${action}`,
        continuityRule,
        this.buildPremiumFrameStyleTags(frameKey),
        'single frame'
      ].filter(Boolean).join(', ');
    },
    buildFramePromptCandidates(shot, frameKey) {
      const candidates = [
        this.buildFrameImagePrompt(shot, frameKey),
        this.buildCompactFramePrompt(shot, frameKey),
        this.buildSafeFramePrompt(shot, frameKey)
      ];
      return [...new Set(candidates.map((item) => String(item || '').trim()).filter(Boolean))];
    },
    sleep(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },
    isRetryableFrameError(message = '') {
      const text = String(message || '').toLowerCase();
      return /timeout|timed out|temporarily|try again|connection|network|econn|502|503|504|500|ssl|reset|closed|unavailable/.test(text);
    },
    async enhancePromptText(prompt, context = {}) {
      const rawPrompt = String(prompt || '').trim();
      if (!rawPrompt) return '';
      try {
        const response = await axios.post('/api/enhance-prompt', { prompt: rawPrompt, context });
        return String(response.data?.enhanced_prompt || '').trim();
      } catch (error) {
        return '';
      }
    },
    buildVoiceoverGenerationContext(shot) {
      const safeShot = this.normalizeShot({ ...(shot || {}) });
      const title = String(safeShot?.title || '当前镜头').trim() || '当前镜头';
      const startFrameGoal = String(
        safeShot?.startFrame?.description ||
        safeShot?.startFrameGoal ||
        safeShot?.start_frame_goal ||
        ''
      ).trim();
      const prevState = this.resolveShotPrevState(safeShot);
      const motionInstruction = this.ensureMotionInstructionFromPrevState(prevState, this.resolveShotMotionInstruction(safeShot));
      const targetState = this.ensureGradualTargetState(
        String(
          safeShot?.endFrame?.description ||
          this.resolveShotTargetState(safeShot) ||
          ''
        ).trim(),
        motionInstruction
      );
      const visualAnchor = this.ensureVisualAnchorWithPrevState(
        this.resolveShotVisualAnchor(safeShot),
        prevState,
        targetState,
        String(safeShot?.sourceDescription || '').trim()
      );
      const continuityHint = this.ensureContinuityHint(
        this.resolveShotContinuityHint(safeShot),
        targetState,
        prevState,
        String(safeShot?.sourceDescription || '').trim()
      );
      return {
        shot_title: title,
        subject_name: title,
        shot_duration: String(safeShot?.duration || '5s').trim() || '5s',
        scene_script: String(safeShot?.sceneNarrative || '').trim(),
        shot_summary: this.buildShotNarrativeSummary(safeShot),
        detailed_plot: this.getShotDetailedPlot(safeShot),
        story_context: this.buildStoryContextForShot(safeShot),
        action_details: String(safeShot?.actionDetails || '').trim(),
        dialogue_details: String(safeShot?.dialogueDetails || '').trim(),
        mood: String(safeShot?.mood || '').trim(),
        prev_state: prevState,
        start_frame_goal: startFrameGoal,
        motion_instruction: motionInstruction,
        target_state: targetState,
        visual_anchor: visualAnchor,
        continuity_hint: continuityHint,
        bound_character_names: this.resolveBoundCharacterAssetsForShot(safeShot)
          .map((item, idx) => String(item?.name || `角色${idx + 1}`).trim())
          .filter(Boolean),
        existing_voiceover: this.resolveShotVoiceoverText(safeShot)
      };
    },
    async generateEditingShotVoiceover() {
      const draftShot = this.buildShotFromEditingDraft();
      const shotPrompt = this.resolveShotPlanPrompt(draftShot);
      const fallbackSeed = [
        this.getShotDetailedPlot(draftShot),
        String(draftShot?.sceneNarrative || '').trim(),
        String(draftShot?.actionDetails || '').trim(),
        String(draftShot?.dialogueDetails || '').trim()
      ].find((item) => String(item || '').trim());
      const requestPrompt = String(shotPrompt || fallbackSeed || '').trim();
      if (!requestPrompt) {
        alert('请先填写镜头脚本、Shot Plan 或动作细节');
        return;
      }

      this.voiceoverGenerating = true;
      try {
        const response = await axios.post('/api/generate-voiceover', {
          prompt: requestPrompt,
          context: this.buildVoiceoverGenerationContext(draftShot)
        });
        const voiceoverText = String(response.data?.voiceover_text || '').trim();
        if (!voiceoverText) {
          alert('旁白生成失败：未返回有效内容');
          return;
        }
        this.editingShotDraft.voiceoverText = voiceoverText;
      } catch (error) {
        const msg = String(error?.response?.data?.error || error?.message || '旁白生成失败').trim();
        alert(`旁白生成失败：${msg}`);
      } finally {
        this.voiceoverGenerating = false;
      }
    },
    async enhanceEditingShotPrompt() {
      const draftShot = this.buildShotFromEditingDraft();
      const rawShotPrompt = this.resolveShotPlanPrompt(draftShot);
      const rawStartPrompt = this.buildFramePromptSeedForEnhance(draftShot, 'startFrame');
      const rawEndPrompt = this.buildFramePromptSeedForEnhance(draftShot, 'endFrame');
      if (!rawShotPrompt && !rawStartPrompt && !rawEndPrompt) {
        alert('请先填写镜头脚本、Shot Plan 或前后帧描述');
        return;
      }

      this.shotPromptEnhancing = true;
      try {
        let enhancedShotPrompt = '';
        if (rawShotPrompt) {
          enhancedShotPrompt = await this.enhancePromptText(rawShotPrompt, this.buildShotPlanEnhanceContext(draftShot));
          if (enhancedShotPrompt) {
            this.editingShotDraft.shotPrompt = enhancedShotPrompt;
          }
        }

        const shotForFrames = this.buildShotFromEditingDraft();
        if (enhancedShotPrompt) shotForFrames.prompt = enhancedShotPrompt;

        const [enhancedStartPrompt, enhancedEndPrompt] = await Promise.all([
          rawStartPrompt
            ? this.enhancePromptText(
              this.buildFramePromptSeedForEnhance(shotForFrames, 'startFrame'),
              this.buildFrameEnhanceContext(shotForFrames, 'startFrame', this.editingShotIndex)
            )
            : Promise.resolve(''),
          rawEndPrompt
            ? this.enhancePromptText(
              this.buildFramePromptSeedForEnhance(shotForFrames, 'endFrame'),
              this.buildFrameEnhanceContext(shotForFrames, 'endFrame', this.editingShotIndex)
            )
            : Promise.resolve('')
        ]);

        if (enhancedStartPrompt) this.editingShotDraft.startFramePrompt = enhancedStartPrompt;
        if (enhancedEndPrompt) this.editingShotDraft.endFramePrompt = enhancedEndPrompt;

        if (!enhancedShotPrompt && !enhancedStartPrompt && !enhancedEndPrompt) {
          alert('提示词增强失败：未返回有效结果');
        }
      } catch (error) {
        const msg = String(error?.response?.data?.error || error?.message || '提示词增强失败').trim();
        alert(`提示词增强失败：${msg}`);
      } finally {
        this.shotPromptEnhancing = false;
      }
    },
    addShot() {
      this.localShots.push(this.normalizeShot({ title: `镜头 ${this.localShots.length + 1}` }));
      this.selectedShotIndex = this.localShots.length - 1;
      this.emitShots();
    },
    selectShot(index) {
      this.selectedShotIndex = index;
      if (this.localShots[index]?.videoUrl) this.autoPlayCurrentVideo();
    },
    deleteSelectedShot() {
      if (this.selectedShotIndex === -1) return;
      this.openDeleteShotDialog(this.selectedShotIndex);
    },
    handleSceneNarrativeChangeForRow(index) {
      if (index < 0 || index >= this.localShots.length) return;
      this.selectedShotIndex = index;
      this.handleSceneNarrativeChange();
    },
    async generateStartFrameForRow(index) {
      if (index < 0 || index >= this.localShots.length) return;
      if (this.batchGeneratingFrames || this.batchGeneratingVideos) return;
      if (this.isStartFrameLoading(index)) return;
      this.selectedShotIndex = index;
      this.setRowLoadingState('rowStartFrameLoading', index, true);
      try {
        const result = await this.generateFrameForShot(index, 'startFrame', {
          silent: true,
          allowSegmentStart: this.testSegmentMode,
          segmentStartIndex: index
        });
        if (!result.success) {
          alert(`起始帧生成失败：${result.error || '未知错误'}`);
        }
      } finally {
        this.setRowLoadingState('rowStartFrameLoading', index, false);
      }
    },
    async generateEndFrameForRow(index) {
      if (index < 0 || index >= this.localShots.length) return;
      if (this.batchGeneratingFrames || this.batchGeneratingVideos) return;
      if (this.isEndFrameLoading(index)) return;
      this.selectedShotIndex = index;
      this.setRowLoadingState('rowEndFrameLoading', index, true);
      try {
        const result = await this.generateFrameForShot(index, 'endFrame', {
          silent: true,
          allowSegmentStart: this.testSegmentMode,
          segmentStartIndex: index
        });
        if (!result.success) {
          alert(`结束帧生成失败：${result.error || '未知错误'}`);
        }
      } finally {
        this.setRowLoadingState('rowEndFrameLoading', index, false);
      }
    },
    async generateVideoForRow(index) {
      if (index < 0 || index >= this.localShots.length) return;
      if (this.batchGeneratingFrames || this.batchGeneratingVideos) return;
      if (this.isVideoLoading(index)) return;
      this.selectedShotIndex = index;
      this.setRowLoadingState('rowVideoLoading', index, true);
      try {
        const result = await this.generateVideoForShot(index, {
          silent: true,
          allowSegmentStart: this.testSegmentMode,
          segmentStartIndex: index
        });
        if (!result.success) {
          alert(`视频生成失败：${result.error || '未知错误'}`);
        }
      } finally {
        this.setRowLoadingState('rowVideoLoading', index, false);
      }
    },
    async refreshVideoTaskStatusForRow(index) {
      if (index < 0 || index >= this.localShots.length) return;
      if (this.isRefreshLoading(index)) return;
      this.selectedShotIndex = index;
      const shot = this.localShots[index];
      const taskId = String(shot?.videoTask?.taskId || '').trim();
      if (!taskId) return;
      this.setRowLoadingState('rowRefreshLoading', index, true);
      try {
        const provider = shot?.videoTask?.provider || this.videoProvider;
        const reqKey = shot?.videoTask?.reqKey || '';
        const queryUrl = shot?.videoTask?.queryUrl || '';
        const queryMethod = shot?.videoTask?.queryMethod || '';
        const data = await this.fetchVideoTaskStatus(taskId, provider, reqKey, queryUrl, queryMethod);
        const normalizedStatus = this.normalizeTaskStatus(data?.status || (data?.error ? 'error' : ''), {
          hasVideo: Boolean(data?.video_url || shot?.videoUrl),
          hasTaskId: Boolean(taskId)
        });
        if (normalizedStatus === 'failed' || data?.transient_error) {
          this.cancelTaskAndNotify(index, data?.message || '请检查模型配置与素材');
        }
      } catch (error) {
        console.error('刷新任务状态失败:', error);
        const msg = error?.response?.data?.error || error?.message || '未知错误';
        this.cancelTaskAndNotify(index, msg);
      } finally {
        this.setRowLoadingState('rowRefreshLoading', index, false);
      }
    },
    deleteShotRow(index) {
      if (index < 0 || index >= this.localShots.length) return;
      this.selectedShotIndex = index;
      this.openDeleteShotDialog(index);
    },
    appendShotFromScene(scene, index) {
      const shots = this.shotsFromScene(scene, index);
      if (!shots.length) return;
      const beforeCount = this.localShots.length;
      this.localShots = this.dedupeShots([...this.localShots, ...shots]);
      this.selectedShotIndex = this.localShots.length ? Math.min(beforeCount, this.localShots.length - 1) : -1;
      this.emitShots();
    },
    importShotsFromStoryboard() {
      if (!this.parsedScenes.length) {
        alert('当前没有可导入的分镜场次');
        return;
      }
      this.localShots = this.dedupeShots(
        this.parsedScenes.reduce((acc, scene, index) => acc.concat(this.shotsFromScene(scene, index)), [])
      );
      this.selectedShotIndex = this.localShots.length > 0 ? 0 : -1;
      this.$emit('generated-event', { type: 'storyboard_imported', payload: { episode: this.currentEpisodeNo, scenes_count: this.localShots.length } });
      this.emitShots();
    },
    async requestFrameImage(
      promptCandidates,
      { context = {}, retriesPerPrompt = 2, referenceImages = [], preferImg2Img = false } = {}
    ) {
      const candidates = Array.isArray(promptCandidates)
        ? [...new Set(promptCandidates.map((item) => String(item || '').trim()).filter(Boolean))]
        : [String(promptCandidates || '').trim()].filter(Boolean);
      const normalizedReferences = [...new Set(
        (Array.isArray(referenceImages) ? referenceImages : [])
          .map((item) => this.normalizeImageUrl(item))
          .filter((url) => this.isUsableImageUrl(url))
      )];
      const useImg2Img = Boolean(preferImg2Img && normalizedReferences.length > 0);
      const requestReferences = useImg2Img ? normalizedReferences : [];
      let lastError = '关键帧生成失败，未返回有效图片地址';

      const tryGenerate = async (candidate, maxAttempts) => {
        for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
          try {
            const response = await axios.post('/api/generate-scene', {
              description: candidate,
              reference_images: requestReferences,
              prefer_img2img: useImg2Img,
              context
            });
            const imageUrl = String(response.data?.image_url || '').trim();
            if (!this.isUsableImageUrl(imageUrl)) {
              throw new Error(String(response.data?.error || response.data?.message || '关键帧生成失败，未返回有效图片地址'));
            }
            return {
              imageUrl,
              usedPrompt: candidate,
              referenceImageUsed: String(response.data?.reference_image_used || '').trim(),
              generationMode: String(response.data?.generation_mode || '').trim(),
              requestedReferences: requestReferences
            };
          } catch (error) {
            const msg = String(
              error?.response?.data?.error ||
              error?.response?.data?.message ||
              error?.message ||
              '关键帧生成失败，请重试'
            ).trim();
            lastError = msg || lastError;
            if (attempt < maxAttempts && this.isRetryableFrameError(msg)) {
              await this.sleep(600 * attempt);
              continue;
            }
            throw error;
          }
        }
        throw new Error(lastError);
      };

      for (const candidate of candidates) {
        try {
          return await tryGenerate(candidate, retriesPerPrompt);
        } catch (error) {
          const text = String(
            error?.response?.data?.error ||
            error?.response?.data?.message ||
            error?.message ||
            ''
          ).trim();
          lastError = text || lastError;
        }
      }

      const enhancedCandidate = await this.enhancePromptText(candidates[0] || '', context);
      if (enhancedCandidate && !candidates.includes(enhancedCandidate)) {
        try {
          return await tryGenerate(enhancedCandidate, 2);
        } catch (error) {
          const text = String(
            error?.response?.data?.error ||
            error?.response?.data?.message ||
            error?.message ||
            ''
          ).trim();
          lastError = text || lastError;
        }
      }

      throw new Error(lastError);
    },
    buildContinuityStartFramePromptCandidates(shotIndex) {
      const shot = this.localShots[shotIndex] || {};
      const previousShot = shotIndex > 0 ? this.localShots[shotIndex - 1] : null;
      const currentPrompt = this.summarizeForFrame(
        this.sanitizeFramePromptText(
          this.stripBoundCharacterNamesFromText(this.resolveShotPlanPrompt(shot), shot)
        ),
        160
      );
      const currentStart = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(
          String(
            shot?.startFrame?.description ||
            shot?.startFrameGoal ||
            shot?.start_frame_goal ||
            ''
          ).trim(),
          shot
        )
      );
      const previousEnd = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(
          String(
            previousShot?.endFrame?.description ||
            previousShot?.endFrame?.enhanced_prompt ||
            previousShot?.targetState ||
            previousShot?.target_state ||
            previousShot?.endFrameGoal ||
            ''
          ).trim(),
          previousShot
        )
      );
      const environment = this.buildSceneVisualHintForFrame(shot);
      const action = this.buildActionVisualHintForFrame(shot, 'startFrame');
      const camera = this.buildCameraVisualHintForFrame(shot, 'startFrame');
      const primary = [
        currentPrompt || currentStart || action,
        currentStart && `当前镜头开场：${currentStart}`,
        previousEnd && `承接上一镜头结束状态：${previousEnd}`,
        environment && `environment: ${environment}`,
        action && `action: ${action}`,
        `camera: ${camera}`,
        '以上一镜头结束帧为连续性主参考，保持同一场景、同一角色、同一机位方向和动作惯性',
        '不要直接复制参考图，必须生成当前镜头自己的起始瞬间和第一拍调度',
        'same scene, same background, consistent character, smooth transition, subtle pose change',
        this.buildPremiumFrameStyleTags('startFrame'),
        'single frame'
      ].filter(Boolean).join('，');
      const compact = [
        currentPrompt || currentStart || action,
        currentStart && `start beat: ${currentStart}`,
        previousEnd && `follow previous end: ${previousEnd}`,
        `camera: ${camera}`,
        'reference previous end frame, not an exact copy',
        'same scene, smooth transition',
        this.buildPremiumFrameStyleTags('startFrame'),
        'single frame'
      ].filter(Boolean).join(', ');
      const safe = [
        environment && `environment: ${environment}`,
        action && `action: ${action}`,
        currentStart && `current opening: ${currentStart}`,
        'inherit previous-shot ending continuity but generate a new opening frame',
        'stable composition, subtle motion',
        this.buildPremiumFrameStyleTags('startFrame'),
        'single frame'
      ].filter(Boolean).join(', ');
      return [...new Set([primary, compact, safe].map((item) => String(item || '').trim()).filter(Boolean))];
    },
    buildContinuityStartFrameContext(shotIndex, previousEndUrl, referenceImages = []) {
      const shot = this.localShots[shotIndex] || {};
      const previousShot = shotIndex > 0 ? this.localShots[shotIndex - 1] : null;
      const detailedPlot = this.getShotDetailedPlot(shot);
      const previousEndDescription = this.sanitizeFramePromptText(
        this.stripBoundCharacterNamesFromText(
          String(
            previousShot?.endFrame?.description ||
            previousShot?.endFrame?.enhanced_prompt ||
            previousShot?.targetState ||
            previousShot?.target_state ||
            previousShot?.endFrameGoal ||
            ''
          ).trim(),
          previousShot
        )
      );
      return {
        prompt_type: 'frame',
        asset_type: 'scene',
        name: String(shot?.title || '').trim(),
        visual_style: '高质感国风奇幻动画电影感，完整单幅关键帧，主体明确，空间纵深强，体积光明显，强调开场建立感',
        scene_script: String(shot?.sceneNarrative || '').trim(),
        detailed_plot: detailedPlot,
        shot_deployment: String(shot?.shotDeployment || '').trim(),
        action_details: String(shot?.actionDetails || '').trim(),
        dialogue_details: detailedPlot || String(shot?.dialogueDetails || '').trim(),
        narration_text: this.resolveShotVoiceoverText(shot),
        continuity_rules: [
          this.buildContinuityRules(shot),
          '当前起始帧必须承接上一镜头结束帧，但不能直接复刻参考图，需要进入当前镜头自己的开场动作。'
        ].filter(Boolean).join('\n'),
        scene_hints: this.buildSceneFrameHints(shot),
        character_hints: this.buildCharacterFrameHints(shot),
        character_identity_rules: this.buildCharacterIdentityRules(shot),
        bound_character_names: this.resolveBoundCharacterAssetsForShot(shot)
          .map((item, idx) => String(item?.name || `角色${idx + 1}`).trim())
          .filter(Boolean),
        frame_key: 'startFrame',
        previous_shot_summary: this.buildShotNarrativeSummary(previousShot),
        previous_end_frame_description: previousEndDescription,
        previous_end_frame_image_url: previousEndUrl,
        reference_images: referenceImages,
      };
    },
    async syncShotStartFrameFromPreviousEnd(shotIndex) {
      if (shotIndex <= 0 || shotIndex >= this.localShots.length) {
        return { success: true, copied: false };
      }

      const prevIndex = shotIndex - 1;
      let previousEndUrl = this.normalizeImageUrl(this.localShots[prevIndex]?.endFrame?.image_url);

      if (!this.isUsableImageUrl(previousEndUrl)) {
        const previousEndResult = await this.generateFrameForShot(prevIndex, 'endFrame', { silent: true });
        if (!previousEndResult?.success) {
          return { success: false, error: `镜头${prevIndex + 1}结束帧不可用，无法建立镜头连续性` };
        }
        previousEndUrl = this.normalizeImageUrl(this.localShots[prevIndex]?.endFrame?.image_url);
      }

      if (!this.isUsableImageUrl(previousEndUrl)) {
        return { success: false, error: `镜头${prevIndex + 1}结束帧不可用，无法建立镜头连续性` };
      }

      const currentShot = this.localShots[shotIndex] || {};
      const currentStartFrame = currentShot.startFrame || {};
      const existingStartUrl = this.normalizeImageUrl(currentStartFrame.image_url);
      const existingReference = this.normalizeImageUrl(currentStartFrame.reference_image_used);
      const existingMode = String(currentStartFrame.generation_mode || '').trim().toLowerCase();

      if (
        this.isUsableImageUrl(existingStartUrl) &&
        existingReference === previousEndUrl &&
        existingMode.includes('continuity-reference-from-previous-end-frame')
      ) {
        return { success: true, copied: false, skipped: true, imageUrl: existingStartUrl };
      }

      const referenceImages = [...new Set([
        previousEndUrl,
        ...this.buildFrameReferenceImages(shotIndex, 'startFrame')
      ].map((item) => this.normalizeImageUrl(item)).filter((item) => this.isUsableImageUrl(item)))];
      const promptCandidates = this.buildContinuityStartFramePromptCandidates(shotIndex);
      const frameContext = this.buildContinuityStartFrameContext(shotIndex, previousEndUrl, referenceImages);

      try {
        const result = await this.requestFrameImage(promptCandidates, {
          context: frameContext,
          retriesPerPrompt: 2,
          referenceImages,
          preferImg2Img: true
        });
        const nextStartFrame = {
          ...(currentShot.startFrame || {}),
          image_url: result.imageUrl,
          enhanced_prompt: String(result.usedPrompt || promptCandidates[0] || currentShot.startFrame?.enhanced_prompt || '').trim(),
          reference_images: referenceImages,
          reference_image_used: this.normalizeImageUrl(result.referenceImageUsed) || previousEndUrl,
          generation_mode: 'continuity-reference-from-previous-end-frame'
        };

        this.localShots.splice(shotIndex, 1, {
          ...currentShot,
          startFrame: nextStartFrame,
          endFrame: { ...(currentShot.endFrame || {}) }
        });
        this.emitShots();
        return { success: true, copied: false, imageUrl: result.imageUrl };
      } catch (error) {
        const msg = String(
          error?.response?.data?.error ||
          error?.response?.data?.message ||
          error?.message ||
          `镜头${shotIndex + 1}起始帧参考生成失败`
        ).trim();
        return { success: false, error: msg || `镜头${shotIndex + 1}起始帧参考生成失败` };
      }
    },
    buildEndFrameLockedPrompt(shot = {}) {
      const shotPrompt = this.summarizeForFrame(
        this.sanitizeFramePromptText(
          this.stripBoundCharacterNamesFromText(String(shot?.prompt || '').trim(), shot)
        ),
        140
      );
      const endGoal = this.summarizeForFrame(
        this.sanitizeFramePromptText(
          this.stripBoundCharacterNamesFromText(
            this.ensureGradualTargetState(
              String(
                shot?.endFrame?.description ||
                shot?.targetState ||
                shot?.target_state ||
                shot?.endFrameGoal ||
                ''
              ).trim(),
              this.resolveShotMotionInstruction(shot)
            ),
            shot
          )
        ),
        100
      );
      const cameraHint = this.buildCameraVisualHintForFrame(shot, 'endFrame');
      return [
        shotPrompt,
        endGoal && `end state: ${endGoal}`,
        `camera: ${cameraHint}`,
        'slight motion change',
        'subtle motion',
        'same scene',
        'same background',
        'consistent composition',
        'same camera framing',
        'same character position',
        'smooth transition',
        'no abrupt jump',
        this.buildPremiumFrameStyleTags('endFrame'),
        'single frame'
      ].filter(Boolean).join(', ');
    },
    async requestEndFrameFromStartFrame(startFrameUrl, shot = {}, context = {}) {
      const baseStartUrl = this.normalizeImageUrl(startFrameUrl);
      if (!this.isUsableImageUrl(baseStartUrl)) {
        throw new Error('起始帧无效，无法生成结束帧');
      }
      const fixedPrompt = this.buildEndFrameLockedPrompt(shot);
      const response = await axios.post('/api/generate-scene', {
        description: fixedPrompt,
        reference_images: [baseStartUrl],
        prefer_img2img: true,
        context
      });
      const imageUrl = String(response.data?.image_url || '').trim();
      if (!this.isUsableImageUrl(imageUrl)) {
        throw new Error(String(response.data?.error || response.data?.message || '结束帧生成失败，未返回有效图片地址'));
      }
      return {
        imageUrl,
        usedPrompt: fixedPrompt,
        referenceImageUsed: String(response.data?.reference_image_used || '').trim(),
        generationMode: String(response.data?.generation_mode || '').trim()
      };
    },
    async generateFrameForShot(shotIndex, frameKey, { silent = false, allowSegmentStart = false, segmentStartIndex = -1 } = {}) {
      if (shotIndex < 0 || shotIndex >= this.localShots.length) {
        return { success: false, error: '镜头索引无效' };
      }

      const shot = this.localShots[shotIndex];
      const frame = shot?.[frameKey];
      if (!frame) return { success: false, error: '关键帧数据无效' };
      const bypassPrevContinuity = Boolean(allowSegmentStart && shotIndex === segmentStartIndex);

      if (frameKey === 'startFrame' && shotIndex > 0 && !bypassPrevContinuity) {
        return this.syncShotStartFrameFromPreviousEnd(shotIndex);
      }

      const existingUrl = String(frame.image_url || '').trim();
      if (this.isUsableImageUrl(existingUrl)) {
        return { success: true, skipped: true };
      }

      const isEndFrame = frameKey === 'endFrame';
      const fixedEndPrompt = this.buildEndFrameLockedPrompt(shot);

      if (isEndFrame) {
        if (shotIndex > 0 && !bypassPrevContinuity) {
          const continuityResult = await this.syncShotStartFrameFromPreviousEnd(shotIndex);
          if (!continuityResult?.success) {
            return { success: false, error: continuityResult?.error || '镜头连续性同步失败' };
          }
        }

        let startImageUrl = this.normalizeImageUrl(shot?.startFrame?.image_url);
        if (!this.isUsableImageUrl(startImageUrl)) {
          const startResult = await this.generateFrameForShot(shotIndex, 'startFrame', {
            silent: true,
            allowSegmentStart,
            segmentStartIndex
          });
          if (!startResult?.success) {
            return { success: false, error: '结束帧依赖起始帧，起始帧生成失败' };
          }
          startImageUrl = this.normalizeImageUrl((this.localShots[shotIndex] || {})?.startFrame?.image_url);
        }
        if (!this.isUsableImageUrl(startImageUrl)) {
          return { success: false, error: '结束帧依赖起始帧，未找到有效起始帧' };
        }

        const detailedPlot = this.getShotDetailedPlot(shot);
        const frameContext = {
          prompt_type: 'frame',
          asset_type: 'scene',
          name: String(shot?.title || '').trim(),
          visual_style: '高质感国风奇幻动画电影感，完整单幅关键帧，主体明确，空间纵深强，体积光明显，动作收束清楚',
          scene_script: String(shot?.sceneNarrative || '').trim(),
          detailed_plot: detailedPlot,
          shot_deployment: '',
          action_details: '',
          dialogue_details: detailedPlot,
          narration_text: this.resolveShotVoiceoverText(shot),
          continuity_rules: this.buildContinuityRules(shot),
          scene_hints: this.buildSceneFrameHints(shot),
          character_hints: this.buildCharacterFrameHints(shot),
          character_identity_rules: this.buildCharacterIdentityRules(shot),
          bound_character_names: this.resolveBoundCharacterAssetsForShot(shot)
            .map((item, idx) => String(item?.name || `角色${idx + 1}`).trim())
            .filter(Boolean),
          frame_key: frameKey,
          start_frame_image_url: startImageUrl,
          reference_images: [startImageUrl],
        };

        try {
          const result = await this.requestEndFrameFromStartFrame(startImageUrl, shot, frameContext);
          const modeText = String(result.generationMode || '').trim();
          const referenceUsed = this.normalizeImageUrl(result.referenceImageUsed);
          frame.image_url = result.imageUrl;
          frame.enhanced_prompt = fixedEndPrompt;
          frame.reference_images = [startImageUrl];
          frame.reference_image_used = referenceUsed || startImageUrl;
          frame.generation_mode = modeText || 'generated';

          this.localShots.splice(shotIndex, 1, {
            ...shot,
            startFrame: { ...(shot.startFrame || {}) },
            endFrame: { ...(shot.endFrame || {}) }
          });
          this.emitShots();
          return { success: true, skipped: false };
        } catch (error) {
          const msg = String(
            error?.response?.data?.error ||
            error?.response?.data?.message ||
            error?.message ||
            '结束帧生成失败，请重试'
          ).trim();
          if (!silent) alert(`结束帧生成失败：${msg || '未知错误'}`);
          return { success: false, error: msg || '结束帧生成失败，请重试' };
        }
      }

      const prompt = this.buildIndependentFramePrompt(shot, frameKey);
      if (!prompt) {
        return { success: false, error: `${frameKey === 'startFrame' ? '起始帧' : '结束帧'}描述不能为空` };
      }

      try {
        const promptCandidates = this.buildFramePromptCandidates(shot, frameKey);
        const referenceImages = this.buildFrameReferenceImages(shotIndex, frameKey);
        const detailedPlot = this.getShotDetailedPlot(shot);
        const frameContext = {
          prompt_type: 'frame',
          asset_type: 'scene',
          name: String(shot?.title || '').trim(),
          visual_style: `高质感国风奇幻动画电影感，完整单幅关键帧，主体明确，空间纵深强，体积光明显，${frameKey === 'startFrame' ? '开场建立感强' : '动作收束落点明确'}`,
          scene_script: String(shot?.sceneNarrative || '').trim(),
          detailed_plot: detailedPlot,
          shot_deployment: '',
          action_details: '',
          dialogue_details: detailedPlot,
          narration_text: this.resolveShotVoiceoverText(shot),
          continuity_rules: this.buildContinuityRules(shot),
          scene_hints: this.buildSceneFrameHints(shot),
          character_hints: this.buildCharacterFrameHints(shot),
          character_identity_rules: this.buildCharacterIdentityRules(shot),
          bound_character_names: this.resolveBoundCharacterAssetsForShot(shot)
            .map((item, idx) => String(item?.name || `角色${idx + 1}`).trim())
            .filter(Boolean),
          frame_key: frameKey,
          reference_images: referenceImages,
        };
        const result = await this.requestFrameImage(promptCandidates, {
          context: frameContext,
          retriesPerPrompt: 2,
          referenceImages,
          preferImg2Img: false
        });
        frame.image_url = result.imageUrl;
        if (String(result.usedPrompt || '').trim()) {
          frame.enhanced_prompt = String(result.usedPrompt).trim();
        } else if (!String(frame.enhanced_prompt || '').trim()) {
          frame.enhanced_prompt = prompt;
        }
        frame.reference_images = referenceImages;
        frame.reference_image_used = String(result.referenceImageUsed || '').trim();
        frame.generation_mode = String(result.generationMode || '').trim();
        this.localShots.splice(shotIndex, 1, {
          ...shot,
          startFrame: { ...(shot.startFrame || {}) },
          endFrame: { ...(shot.endFrame || {}) }
        });
        this.emitShots();
        return { success: true, skipped: false };
      } catch (error) {
        const msg = error?.response?.data?.error || error?.response?.data?.message || error?.message || '关键帧生成失败，请重试';
        const text = String(msg || '');
        const friendlyMsg = /OutputImageSensitiveContentDetected|SensitiveContent|内容安全|sensitive/i.test(text)
          ? '关键帧被内容安全策略拦截，请弱化暴力/血腥/裸露等表达后重试。'
          : text;
        if (!silent) alert(`关键帧生成失败：${friendlyMsg}`);
        return { success: false, error: friendlyMsg };
      }
    },
    buildContextForShot(shot) {
      const safeShot = shot || {};
      const detailedPlot = this.getShotDetailedPlot(safeShot);
      const storyContext = this.buildStoryContextForShot(safeShot);
      const sceneNarrative = String(
        safeShot?.sceneNarrative ||
        this.buildSceneNarrativeFromFields({
          sourceDescription: safeShot?.sourceDescription,
          shotSummary: safeShot?.shotSummary,
          detailedShotDescription: safeShot?.detailedShotDescription,
          detailedPlot,
          actionArc: safeShot?.actionArc || safeShot?.action_arc,
          emotionArc: safeShot?.emotionArc || safeShot?.emotion_arc,
          rhythmPlan: safeShot?.rhythmPlan || safeShot?.rhythm_plan,
          startFrameGoal: safeShot?.startFrameGoal || safeShot?.start_frame_goal,
          prevState: safeShot?.prevState || safeShot?.prev_state,
          motionInstruction: this.resolveShotMotionInstruction(safeShot),
          targetState: this.resolveShotTargetState(safeShot),
          visualAnchor: safeShot?.visualAnchor || safeShot?.visual_anchor,
          continuityHint: safeShot?.continuityHint || safeShot?.continuity_hint
        })
      ).trim();
      const parsedNarrative = this.parseSceneNarrative(sceneNarrative, {
        sourceDescription: safeShot?.sourceDescription,
        shotSummary: safeShot?.shotSummary,
        detailedShotDescription: safeShot?.detailedShotDescription,
        detailedPlot,
        actionArc: safeShot?.actionArc || safeShot?.action_arc,
        emotionArc: safeShot?.emotionArc || safeShot?.emotion_arc,
        rhythmPlan: safeShot?.rhythmPlan || safeShot?.rhythm_plan,
        startFrameGoal: safeShot?.startFrameGoal || safeShot?.start_frame_goal,
        prevState: safeShot?.prevState || safeShot?.prev_state,
        motionInstruction: this.resolveShotMotionInstruction(safeShot),
        targetState: this.resolveShotTargetState(safeShot),
        visualAnchor: safeShot?.visualAnchor || safeShot?.visual_anchor,
        continuityHint: safeShot?.continuityHint || safeShot?.continuity_hint
      });
      const currentIndex = this.localShots.findIndex((item) => item === safeShot);
      const previousShot = currentIndex > 0 ? this.localShots[currentIndex - 1] : null;
      const nextShot = currentIndex >= 0 && currentIndex < this.localShots.length - 1 ? this.localShots[currentIndex + 1] : null;
      const inheritedPrevState = String(
        parsedNarrative.prevState ||
        previousShot?.targetState ||
        previousShot?.target_state ||
        previousShot?.endFrame?.description ||
        safeShot?.prevState ||
        safeShot?.prev_state ||
        '承接上一镜头同场景基础状态'
      ).trim();
      const normalizedMotionInstruction = this.ensureMotionInstructionFromPrevState(
        inheritedPrevState,
        parsedNarrative.motionInstruction
      );
      const normalizedTargetState = this.ensureGradualTargetState(
        parsedNarrative.targetState,
        normalizedMotionInstruction
      );
      const normalizedVisualAnchor = this.ensureVisualAnchorWithPrevState(
        parsedNarrative.visualAnchor,
        inheritedPrevState,
        normalizedTargetState,
        parsedNarrative.sourceDescription
      );
      const normalizedContinuityHint = this.ensureContinuityHint(
        parsedNarrative.continuityHint,
        normalizedTargetState,
        inheritedPrevState,
        parsedNarrative.sourceDescription
      );
      return {
        shot_title: safeShot?.title || '',
        shot_prompt: this.resolveShotPlanPrompt(safeShot),
        shot_duration: safeShot?.duration || '5s',
        duration: safeShot?.duration || '5s',
        scene_script: sceneNarrative,
        scene_narrative: sceneNarrative,
        scene_description: String(parsedNarrative.sourceDescription || '').trim(),
        shot_summary: String(parsedNarrative.shotSummary || '').trim(),
        detailed_shot_description: String(parsedNarrative.detailedShotDescription || '').trim(),
        story_context: storyContext,
        previous_shot_summary: this.buildShotNarrativeSummary(previousShot),
        next_shot_summary: this.buildShotNarrativeSummary(nextShot),
        start_frame_description: String(safeShot?.startFrame?.description || parsedNarrative.startFrameGoal || '').trim(),
        end_frame_description: String(safeShot?.endFrame?.description || parsedNarrative.targetState || '').trim(),
        detailed_plot: detailedPlot,
        action_arc: (parsedNarrative.actionArc || []).join('；'),
        emotion_arc: (parsedNarrative.emotionArc || []).join('；'),
        rhythm_plan: String(parsedNarrative.rhythmPlan || '').trim(),
        prev_state: inheritedPrevState,
        start_frame_goal: String(parsedNarrative.startFrameGoal || '').trim(),
        motion_instruction: normalizedMotionInstruction,
        target_state: normalizedTargetState,
        visual_anchor: normalizedVisualAnchor,
        continuity_hint: normalizedContinuityHint,
        ShotSize: String(safeShot?.ShotSize || safeShot?.shotSize || '').trim(),
        Camera: String(safeShot?.Camera || safeShot?.camera || '').trim(),
        StartFrame: String(parsedNarrative.startFrameGoal || '').trim(),
        Action: String((parsedNarrative.actionArc || []).join('；')).trim(),
        Mood: String(safeShot?.mood || safeShot?.Mood || (parsedNarrative.emotionArc || [])[0] || '').trim(),
        dialogue_details: detailedPlot || String(safeShot?.dialogueDetails || '').trim(),
        narration_text: this.resolveShotVoiceoverText(safeShot),
        dialogue_beat_details: detailedPlot ? '' : String(safeShot?.dialogueBeatDetails || '').trim(),
        action_details: detailedPlot ? '' : String(safeShot?.actionDetails || '').trim(),
        shot_deployment: detailedPlot ? '' : String(safeShot?.shotDeployment || '').trim(),
        prompt_scaffold: this.buildVideoPromptScaffold(safeShot),
        continuity_rules: this.buildContinuityRules(safeShot),
        scene_hints: this.buildSceneFrameHints(safeShot),
        character_hints: this.buildCharacterFrameHints(safeShot),
        character_identity_rules: this.buildCharacterIdentityRules(safeShot),
        bound_character_names: this.resolveBoundCharacterAssetsForShot(safeShot)
          .map((item, idx) => String(item?.name || `角色${idx + 1}`).trim())
          .filter(Boolean),
        audio_language: 'zh-CN',
        dialogue_language: 'zh-CN',
        voice_language: 'zh-CN',
        audio_requirements: this.generateAudio
          ? 'mandarin speech, chinese dialogue, no english voice. 全程中文普通话配音，禁止英语旁白、英语对白、英语歌词与英文口播。'
          : '不生成音频',
        ratio: this.videoRatio,
        generate_audio: this.generateAudio,
        watermark: this.watermark,
        video_provider: String(this.videoProvider || 'openai').trim().toLowerCase() || 'openai',
        prompt: this.composeShotPrompt(safeShot)
      };
    },
    async generateFrame(frameKey) {
      if (!this.currentShot) return;
      this.loading = true;
      try {
        const result = await this.generateFrameForShot(this.selectedShotIndex, frameKey, {
          silent: true,
          allowSegmentStart: this.testSegmentMode,
          segmentStartIndex: this.selectedShotIndex
        });
        if (!result.success) {
          alert(`关键帧生成失败：${result.error || '未知错误'}`);
        }
      } catch (error) {
        console.error('生成关键帧失败:', error);
        alert(`关键帧生成失败：${error?.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },
    async generateStartFrame() {
      await this.generateFrame('startFrame');
    },
    async generateEndFrame() {
      await this.generateFrame('endFrame');
    },
    async generateAllFrames({ startIndex = 0, allowSegmentStart = false } = {}) {
      if (!this.localShots.length) {
        alert('暂无镜头可生成');
        return;
      }

      this.batchGeneratingFrames = true;
      let startGenerated = 0;
      let endDone = 0;
      let skipped = 0;
      let failed = 0;
      const failedItems = [];
      const total = this.localShots.length;
      const beginIndex = Math.max(0, Math.min(total - 1, Number(startIndex) || 0));
      this.batchProgressTotal = (total - beginIndex) * 2;
      this.batchProgressDone = 0;
      this.batchProgressPercent = 0;

      try {
        for (let i = beginIndex; i < total; i += 1) {
          this.selectedShotIndex = i;
          this.batchStatusText = `批量关键帧生成中 (${i + 1}/${total})`;

          const startResult = await this.generateFrameForShot(i, 'startFrame', {
            silent: true,
            allowSegmentStart,
            segmentStartIndex: beginIndex
          });
          if (startResult.success) {
            if (startResult.skipped) skipped += 1;
            else startGenerated += 1;
          } else {
            failed += 1;
            failedItems.push(`镜头${i + 1}-起始帧：${startResult.error || '生成失败'}`);
          }
          this.batchProgressDone += 1;
          this.batchProgressPercent = Math.max(0, Math.min(100, Math.round((this.batchProgressDone / this.batchProgressTotal) * 100)));
          this.batchStatusText = `批量关键帧生成中 (${i + 1}/${total}) · 起始帧进度 ${this.batchProgressDone}/${this.batchProgressTotal}`;
          this.emitShots();

          const endResult = await this.generateFrameForShot(i, 'endFrame', {
            silent: true,
            allowSegmentStart,
            segmentStartIndex: beginIndex
          });
          if (endResult.success) {
            if (endResult.skipped) skipped += 1;
            else endDone += 1;
          } else {
            failed += 1;
            failedItems.push(`镜头${i + 1}-结束帧：${endResult.error || '生成失败'}`);
          }
          this.batchProgressDone += 1;
          this.batchProgressPercent = Math.max(0, Math.min(100, Math.round((this.batchProgressDone / this.batchProgressTotal) * 100)));
          this.batchStatusText = `批量关键帧生成中 (${i + 1}/${total}) · 结束帧进度 ${this.batchProgressDone}/${this.batchProgressTotal}`;
          this.emitShots();
        }
      } finally {
        this.batchGeneratingFrames = false;
        this.batchStatusText = this.batchProgressTotal ? `关键帧生成完成 ${this.batchProgressDone}/${this.batchProgressTotal}` : '';
        this.batchProgressPercent = 100;
      }

      const failureSuffix = failedItems.length ? `\n失败详情：\n${failedItems.slice(0, 8).join('\n')}` : '';
      alert(`批量关键帧完成：起始帧新增 ${startGenerated}，结束帧新增 ${endDone}，跳过 ${skipped}，失败 ${failed}${failureSuffix}`);
    },
    async generateFramesFromCurrent() {
      if (this.selectedShotIndex < 0 || this.selectedShotIndex >= this.localShots.length) {
        alert('请先在表格中选择一个镜头');
        return;
      }
      await this.generateAllFrames({
        startIndex: this.selectedShotIndex,
        allowSegmentStart: true
      });
    },
    async generateVideoForShot(shotIndex, { silent = false, allowSegmentStart = false, segmentStartIndex = -1 } = {}) {
      if (shotIndex < 0 || shotIndex >= this.localShots.length) {
        return { success: false, error: '镜头索引无效' };
      }
      const bypassPrevContinuity = Boolean(allowSegmentStart && shotIndex === segmentStartIndex);

      if (shotIndex > 0 && !bypassPrevContinuity) {
        const continuityResult = await this.syncShotStartFrameFromPreviousEnd(shotIndex);
        if (!continuityResult?.success) {
          return { success: false, error: continuityResult?.error || '镜头连续性同步失败' };
        }
      }

      const shot = this.localShots[shotIndex];
      if (!this.isUsableImageUrl(shot?.startFrame?.image_url)) {
        return { success: false, error: '请先生成有效的起始帧（不能是占位图 URL）' };
      }

      shot.videoTask = {
        taskId: shot.videoTask?.taskId || '',
        status: 'submitting',
        message: '正在提交任务...',
        progress: 5
      };
      this.emitShots();

      try {
        const context = {
          ...this.buildContextForShot(shot),
          stitch_tail_seconds: 0.5,
          stitch_overlap_seconds: 0.5,
          stitch_transition: 'crossfade'
        };
        const response = await axios.post('/api/generate-video', {
          start_frame: shot.startFrame,
          end_frame: shot.endFrame,
          mode: this.videoMode,
          context
        });

        this.applyTaskUpdateToShot(shotIndex, {
          task_id: response.data?.task_id || '',
          status: response.data?.status || 'submitted',
          message: response.data?.message || '',
          progress: response.data?.progress,
          video_url: response.data?.video_url || '',
          provider: response.data?.provider || this.videoProvider,
          req_key: response.data?.req_key || '',
          query_url: response.data?.query_url || '',
          query_method: response.data?.query_method || '',
          raw_response: response.data?.raw_response
        });

        this.$emit('generated-event', {
          type: 'video_generated',
          payload: {
            mode: this.videoMode,
            status: response.data?.status || 'submitted',
            task_id: response.data?.task_id || '',
            video_url: response.data?.video_url || '',
            provider: response.data?.provider || this.videoProvider,
            req_key: response.data?.req_key || '',
            query_url: response.data?.query_url || '',
            query_method: response.data?.query_method || '',
            shot_index: shotIndex
          }
        });

        const submittedTaskId = String(response.data?.task_id || '').trim();
        const returnedVideoUrl = String(response.data?.video_url || '').trim();
        if (submittedTaskId && !returnedVideoUrl) this.pollVideoTask(submittedTaskId);
        return { success: true, skipped: false };
      } catch (error) {
        console.error('生成视频失败:', error);
        const detailMsg =
          error?.response?.data?.details?.error?.message ||
          error?.response?.data?.details?.message ||
          error?.response?.data?.details?.error ||
          '';
        const baseMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message || '未知错误';
        const msg = detailMsg && String(detailMsg).trim() ? `${baseMsg} | ${String(detailMsg).trim()}` : baseMsg;
      shot.videoTask = {
        taskId: shot.videoTask?.taskId || '',
        status: 'failed',
        message: `提交失败: ${msg}`,
        progress: Math.max(90, Number(shot.videoTask?.progress || 0)),
        provider: String(shot.videoTask?.provider || this.videoProvider || 'openai').trim().toLowerCase() || 'openai',
        reqKey: String(shot.videoTask?.reqKey || '').trim()
      };
      this.emitShots();
      if (!silent) alert(`视频生成失败：${msg}`);
      return { success: false, error: msg };
    }
    },
    async generateVideo() {
      if (!this.currentShot) return;
      this.loading = true;
      try {
        const result = await this.generateVideoForShot(this.selectedShotIndex, {
          silent: true,
          allowSegmentStart: this.testSegmentMode,
          segmentStartIndex: this.selectedShotIndex
        });
        if (!result.success) {
          alert(`视频生成失败：${result.error || '未知错误'}`);
        }
      } finally {
        this.loading = false;
      }
    },
    async generateAllVideos({ startIndex = 0, allowSegmentStart = false } = {}) {
      if (!this.localShots.length) {
        alert('暂无镜头可生成');
        return;
      }

      this.batchGeneratingVideos = true;
      let submitted = 0;
      let skipped = 0;
      let failed = 0;

      try {
        const total = this.localShots.length;
        const beginIndex = Math.max(0, Math.min(total - 1, Number(startIndex) || 0));
        for (let i = beginIndex; i < total; i += 1) {
          this.batchStatusText = `批量视频生成中 (${i + 1}/${total})`;
          const shot = this.localShots[i];
          const alreadyReady = Boolean(String(shot?.videoUrl || '').trim());
          const status = this.normalizeTaskStatus(shot?.videoTask?.status, {
            hasVideo: alreadyReady,
            hasTaskId: Boolean(shot?.videoTask?.taskId)
          });
          const alreadyProcessing = ['submitting', 'submitted', 'processing'].includes(status);
          if (alreadyReady || alreadyProcessing) {
            skipped += 1;
            continue;
          }

          const result = await this.generateVideoForShot(i, {
            silent: true,
            allowSegmentStart,
            segmentStartIndex: beginIndex
          });
          if (result.success) submitted += 1;
          else failed += 1;
        }
      } finally {
        this.batchGeneratingVideos = false;
        this.batchStatusText = '';
      }

      alert(`批量视频提交完成：成功 ${submitted}，跳过 ${skipped}，失败 ${failed}`);
    },
    async generateVideosFromCurrent() {
      if (this.selectedShotIndex < 0 || this.selectedShotIndex >= this.localShots.length) {
        alert('请先在表格中选择一个镜头');
        return;
      }
      await this.generateAllVideos({
        startIndex: this.selectedShotIndex,
        allowSegmentStart: true
      });
    },
    async fetchVideoTaskStatus(taskId, provider = '', reqKey = '', queryUrl = '', queryMethod = '') {
      const normalizedProvider = String(provider || '').trim().toLowerCase();
      const params = [];
      if (normalizedProvider) params.push(`provider=${encodeURIComponent(normalizedProvider)}`);
      const normalizedReqKey = String(reqKey || '').trim();
      if (normalizedReqKey) params.push(`req_key=${encodeURIComponent(normalizedReqKey)}`);
      const normalizedQueryUrl = String(queryUrl || '').trim();
      if (normalizedQueryUrl) params.push(`query_url=${encodeURIComponent(normalizedQueryUrl)}`);
      const normalizedQueryMethod = String(queryMethod || '').trim().toUpperCase();
      if (normalizedQueryMethod) params.push(`query_method=${encodeURIComponent(normalizedQueryMethod)}`);
      const query = params.length ? `?${params.join('&')}` : '';
      const response = await axios.get(`/api/generate-video/tasks/${encodeURIComponent(taskId)}${query}`);
      const data = response.data || {};
      const shotIndex = this.findShotIndexByTaskId(taskId);
      if (shotIndex === -1) return data;
      this.applyTaskUpdateToShot(shotIndex, {
        task_id: taskId,
        status: data?.status,
        message: data?.message,
        progress: data?.progress,
        video_url: data?.video_url,
        provider: data?.provider || normalizedProvider || this.localShots[shotIndex]?.videoTask?.provider || this.videoProvider,
        req_key: data?.req_key || normalizedReqKey || this.localShots[shotIndex]?.videoTask?.reqKey || '',
        query_url: data?.query_url || normalizedQueryUrl || this.localShots[shotIndex]?.videoTask?.queryUrl || '',
        query_method: data?.query_method || normalizedQueryMethod || this.localShots[shotIndex]?.videoTask?.queryMethod || '',
        raw_response: data?.raw_response
      });
      return data;
    },
    async refreshVideoTaskStatus() {
      const taskId = this.currentShot?.videoTask?.taskId;
      if (!taskId) return;
      this.taskRefreshing = true;
      const shotIndex = this.findShotIndexByTaskId(taskId);
      const targetIndex = shotIndex >= 0 ? shotIndex : this.selectedShotIndex;
      try {
        const provider = this.currentShot?.videoTask?.provider || this.videoProvider;
        const reqKey = this.currentShot?.videoTask?.reqKey || '';
        const queryUrl = this.currentShot?.videoTask?.queryUrl || '';
        const queryMethod = this.currentShot?.videoTask?.queryMethod || '';
        const data = await this.fetchVideoTaskStatus(taskId, provider, reqKey, queryUrl, queryMethod);
        const normalizedStatus = this.normalizeTaskStatus(data?.status || (data?.error ? 'error' : ''), {
          hasVideo: Boolean(data?.video_url || this.currentShot?.videoUrl),
          hasTaskId: Boolean(taskId)
        });
        if (normalizedStatus === 'failed' || data?.transient_error) {
          this.cancelTaskAndNotify(targetIndex, data?.message || '请检查模型配置与素材');
        }
      } catch (error) {
        console.error('刷新任务状态失败:', error);
        const msg = error?.response?.data?.error || error?.message || '未知错误';
        this.cancelTaskAndNotify(targetIndex, msg);
      } finally {
        this.taskRefreshing = false;
      }
    },
    async pollVideoTask(taskId) {
      for (let i = 0; i < 180; i += 1) {
        await new Promise((resolve) => setTimeout(resolve, 5000));
        const shotIndex = this.findShotIndexByTaskId(taskId);
        if (shotIndex === -1) return;
        try {
          const shot = this.localShots[shotIndex];
          const currentStatus = this.normalizeTaskStatus(shot?.videoTask?.status, {
            hasVideo: Boolean(shot?.videoUrl),
            hasTaskId: Boolean(shot?.videoTask?.taskId)
          });
          if (currentStatus === 'processing' || currentStatus === 'submitted' || currentStatus === 'submitting') {
            shot.videoTask.progress = Math.min(90, Number(shot?.videoTask?.progress || 0) + 6);
            this.emitShots();
          }
          const provider = shot?.videoTask?.provider || this.videoProvider;
          const reqKey = shot?.videoTask?.reqKey || '';
          const queryUrl = shot?.videoTask?.queryUrl || '';
          const queryMethod = shot?.videoTask?.queryMethod || '';
          const data = await this.fetchVideoTaskStatus(taskId, provider, reqKey, queryUrl, queryMethod);
          const status = this.normalizeTaskStatus(data?.status || (data?.error ? 'error' : ''), {
            hasVideo: Boolean(data?.video_url || shot?.videoUrl),
            hasTaskId: Boolean(taskId)
          });
          if (data?.transient_error) {
            this.cancelTaskAndNotify(shotIndex, data?.message || '任务查询出现临时错误');
            return;
          }
          if (status === 'succeeded') return;
          if (status === 'failed') {
            this.cancelTaskAndNotify(shotIndex, data?.message || '任务失败');
            return;
          }
        } catch (error) {
          const msg = error?.response?.data?.error || error?.message || '任务状态查询失败';
          this.cancelTaskAndNotify(shotIndex, msg);
          return;
        }
      }
    },
    handleSceneNarrativeChange({ preserveFramePrompts = false } = {}) {
      if (!this.currentShot) return;
      const parsed = this.parseSceneNarrative(this.currentShot.sceneNarrative, {
        sourceDescription: this.currentShot.sourceDescription,
        shotSummary: this.currentShot.shotSummary,
        detailedShotDescription: this.currentShot.detailedShotDescription,
        detailedPlot: this.currentShot.detailedPlot,
        actionArc: this.currentShot.actionArc,
        emotionArc: this.currentShot.emotionArc,
        rhythmPlan: this.currentShot.rhythmPlan,
        startFrameGoal: this.currentShot.startFrameGoal,
        prevState: this.currentShot.prevState || this.currentShot.prev_state,
        motionInstruction: this.currentShot.motionInstruction || this.currentShot.motion_instruction,
        targetState: this.currentShot.targetState || this.currentShot.target_state || this.currentShot.endFrameGoal,
        visualAnchor: this.currentShot.visualAnchor || this.currentShot.visual_anchor,
        continuityHint: this.currentShot.continuityHint || this.currentShot.continuity_hint
      });
      this.currentShot.sourceDescription = parsed.sourceDescription;
      this.currentShot.shotSummary = parsed.shotSummary;
      this.currentShot.detailedShotDescription = parsed.detailedShotDescription;
      this.currentShot.detailedPlot = parsed.detailedPlot;
      this.currentShot.actionArc = parsed.actionArc;
      this.currentShot.emotionArc = parsed.emotionArc;
      this.currentShot.rhythmPlan = parsed.rhythmPlan;
      this.currentShot.startFrameGoal = parsed.startFrameGoal;
      this.currentShot.prevState = parsed.prevState;
      this.currentShot.prev_state = parsed.prevState;
      this.currentShot.motionInstruction = parsed.motionInstruction;
      this.currentShot.motion_instruction = parsed.motionInstruction;
      this.currentShot.targetState = parsed.targetState;
      this.currentShot.target_state = parsed.targetState;
      this.currentShot.visualAnchor = parsed.visualAnchor;
      this.currentShot.visual_anchor = parsed.visualAnchor;
      this.currentShot.continuityHint = parsed.continuityHint;
      this.currentShot.continuity_hint = parsed.continuityHint;
      this.currentShot.endFrameGoal = parsed.targetState; // legacy alias
      this.currentShot.sceneNarrative = this.buildSceneNarrativeFromFields(parsed) || String(this.currentShot.sceneNarrative || '').trim();
      if (this.currentShot.startFrame) {
        const existingStartPrompt = String(this.currentShot.startFrame.enhanced_prompt || '').trim();
        if (!preserveFramePrompts || !existingStartPrompt) {
          this.currentShot.startFrame.enhanced_prompt = '';
        }
        if (!String(this.currentShot.startFrame.description || '').trim() && parsed.startFrameGoal) {
          this.currentShot.startFrame.description = parsed.startFrameGoal;
        }
      }
      if (this.currentShot.endFrame) {
        const existingEndPrompt = String(this.currentShot.endFrame.enhanced_prompt || '').trim();
        if (!preserveFramePrompts || !existingEndPrompt) {
          this.currentShot.endFrame.enhanced_prompt = '';
        }
        if (!String(this.currentShot.endFrame.description || '').trim() && parsed.targetState) {
          this.currentShot.endFrame.description = parsed.targetState;
        }
      }
      this.ensureShotPlanPrompt(this.currentShot);
      if (!preserveFramePrompts) {
        this.ensureShotFramePrompts(this.currentShot);
      } else {
        const keepStartPrompt = String(this.currentShot?.startFrame?.enhanced_prompt || '').trim();
        const keepEndPrompt = String(this.currentShot?.endFrame?.enhanced_prompt || '').trim();
        this.ensureShotFramePrompts(this.currentShot);
        if (keepStartPrompt) this.currentShot.startFrame.enhanced_prompt = keepStartPrompt;
        if (keepEndPrompt) this.currentShot.endFrame.enhanced_prompt = keepEndPrompt;
      }
      this.emitShots();
    },
    handleDetailedPlotChange() {
      if (!this.currentShot) return;
      this.currentShot.sceneNarrative = this.buildSceneNarrativeFromFields({
        sourceDescription: this.currentShot.sourceDescription,
        shotSummary: this.currentShot.shotSummary,
        detailedShotDescription: this.currentShot.detailedShotDescription,
        detailedPlot: this.currentShot.detailedPlot,
        actionArc: this.currentShot.actionArc,
        emotionArc: this.currentShot.emotionArc,
        rhythmPlan: this.currentShot.rhythmPlan,
        startFrameGoal: this.currentShot.startFrameGoal,
        prevState: this.currentShot.prevState || this.currentShot.prev_state,
        motionInstruction: this.currentShot.motionInstruction || this.currentShot.motion_instruction,
        targetState: this.currentShot.targetState || this.currentShot.target_state || this.currentShot.endFrameGoal,
        visualAnchor: this.currentShot.visualAnchor || this.currentShot.visual_anchor,
        continuityHint: this.currentShot.continuityHint || this.currentShot.continuity_hint
      });
      this.handleSceneNarrativeChange();
    },
    handleNarrativeFieldsChange() {
      if (!this.currentShot) return;
      this.currentShot.sceneNarrative = this.buildSceneNarrativeFromFields({
        sourceDescription: this.currentShot.sourceDescription,
        shotSummary: this.currentShot.shotSummary,
        detailedShotDescription: this.currentShot.detailedShotDescription,
        detailedPlot: this.currentShot.detailedPlot,
        actionArc: this.currentShot.actionArc,
        emotionArc: this.currentShot.emotionArc,
        rhythmPlan: this.currentShot.rhythmPlan,
        startFrameGoal: this.currentShot.startFrameGoal,
        prevState: this.currentShot.prevState || this.currentShot.prev_state,
        motionInstruction: this.currentShot.motionInstruction || this.currentShot.motion_instruction,
        targetState: this.currentShot.targetState || this.currentShot.target_state || this.currentShot.endFrameGoal,
        visualAnchor: this.currentShot.visualAnchor || this.currentShot.visual_anchor,
        continuityHint: this.currentShot.continuityHint || this.currentShot.continuity_hint
      });
      this.handleSceneNarrativeChange();
    },
    enforceShotStateFlow() {
      if (!Array.isArray(this.localShots) || !this.localShots.length) return;
      let previousTargetState = '';
      this.localShots.forEach((shot, index) => {
        const safeShot = shot || {};
        const sourceDescription = String(safeShot?.sourceDescription || '').trim();
        const inheritedPrevState = previousTargetState || this.resolveShotPrevState(safeShot);
        const prevState = String(
          inheritedPrevState ||
          safeShot?.startFrameGoal ||
          safeShot?.start_frame_goal ||
          '承接上一镜头同场景基础状态'
        ).trim();
        const motionInstruction = this.ensureMotionInstructionFromPrevState(
          prevState,
          this.resolveShotMotionInstruction(safeShot)
        );
        const targetState = this.ensureGradualTargetState(
          this.resolveShotTargetState(safeShot),
          motionInstruction
        );
        const visualAnchor = this.ensureVisualAnchorWithPrevState(
          this.resolveShotVisualAnchor(safeShot),
          prevState,
          targetState,
          sourceDescription
        );
        const continuityHint = this.ensureContinuityHint(
          this.resolveShotContinuityHint(safeShot),
          targetState,
          prevState,
          sourceDescription
        );

        safeShot.prevState = prevState;
        safeShot.prev_state = prevState;
        safeShot.motionInstruction = motionInstruction;
        safeShot.motion_instruction = motionInstruction;
        safeShot.targetState = targetState;
        safeShot.target_state = targetState;
        safeShot.visualAnchor = visualAnchor;
        safeShot.visual_anchor = visualAnchor;
        safeShot.continuityHint = continuityHint;
        safeShot.continuity_hint = continuityHint;
        safeShot.endFrameGoal = targetState;
        if (!safeShot.endFrame) safeShot.endFrame = { description: '', enhanced_prompt: '', image_url: '' };
        if (!String(safeShot.endFrame.description || '').trim() && targetState) {
          safeShot.endFrame.description = targetState;
        }
        previousTargetState = targetState || previousTargetState;
      });
    },
    emitShots() {
      this.enforceShotStateFlow();
      this.$emit('shots-updated', JSON.parse(JSON.stringify(this.localShots)));
    }
  }
};
</script>

<style scoped>
.workbench-phase {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: linear-gradient(180deg, #0d1f24, #0a171b);
  border-color: #2b4f57;
}

.wb-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wb-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.workflow-brief {
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(19, 48, 56, 0.88);
  border: 1px solid rgba(45, 212, 191, 0.22);
  color: #bfe6de;
  font-size: 13px;
  line-height: 1.5;
}

.wb-header h2 {
  margin: 0;
  color: #e9faf5;
  font-size: 20px;
}

.wb-header p {
  margin-top: 4px;
  font-size: 12px;
  color: #9cc0ba;
}

.wb-toolbar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.toolbar-check {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #3f6a72;
  background: #14333a;
  color: #bfe6de;
  font-size: 12px;
  user-select: none;
}

.toolbar-check input {
  margin: 0;
  accent-color: #34d399;
}

.batch-status {
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #3f6a72;
  background: #14333a;
  color: #bfe6de;
  font-size: 12px;
}

.batch-inline-progress {
  margin-top: 8px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
}

.link-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #3f6a72;
  background: #14333a;
  color: #bfe6de;
  font-size: 12px;
  user-select: none;
}

.link-toggle input {
  margin: 0;
  accent-color: #34d399;
}

.phase-tip {
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(20, 51, 58, 0.92);
  border: 1px solid #3f6a72;
  color: #bfe6de;
  font-size: 13px;
  line-height: 1.5;
}

.wb-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
}

.panel-dark {
  border: 1px solid #2f5861;
  background: linear-gradient(180deg, #123038, #0f242a);
  border-radius: 12px;
  padding: 12px;
  color: #d8f5ef;
}

.section-head,
.shot-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.section-head h3,
.section-head h4,
.shot-body h4 {
  margin: 0;
  color: #e8fbf8;
}

.section-head span,
.shot-body p {
  font-size: 12px;
  color: #9fc5bf;
}

.scene-wrap {
  max-height: 180px;
  overflow: auto;
  border: 1px solid #3d6a73;
  border-radius: 10px;
}

.scene-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.scene-table th,
.scene-table td {
  border-top: 1px solid #3d6a73;
  padding: 8px;
  text-align: left;
}

.scene-table th {
  color: #c5e7de;
  background: #1a3f47;
}

.scene-auto-tip {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #3f6a72;
  background: rgba(20, 51, 58, 0.85);
  color: #bfe6de;
  font-size: 13px;
}

.table-config-row {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #3d6a73;
  border-radius: 10px;
  background: rgba(15, 40, 46, 0.72);
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.config-group {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.config-group label {
  font-size: 12px;
  color: #bfe6de;
}

.config-group select {
  min-width: 130px;
  border: 1px solid #3f6a72;
  background: #14333a;
  color: #def8f2;
}

.config-checks {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  font-size: 12px;
  color: #bfe6de;
}

.config-checks label {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.config-checks input[type="checkbox"] {
  margin: 0;
  accent-color: #34d399;
}

.workbench-table-wrap {
  margin-top: 8px;
  border: 1px solid #3d6a73;
  border-radius: 10px;
  overflow: auto;
  max-height: 72vh;
}

.workbench-table {
  width: 100%;
  min-width: 1860px;
  border-collapse: collapse;
  font-size: 12px;
}

.workbench-table thead th {
  position: sticky;
  top: 0;
  z-index: 3;
  background: #1a3f47;
  color: #c5e7de;
  border-top: 1px solid #3d6a73;
}

.workbench-table th,
.workbench-table td {
  border-top: 1px solid #3d6a73;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

.workbench-table tbody tr {
  cursor: pointer;
}

.workbench-table tbody tr:hover {
  background: rgba(53, 88, 94, 0.26);
}

.workbench-table tbody tr.selected {
  background: rgba(45, 212, 191, 0.12);
}

.idx-col {
  font-size: 11px;
  color: #9fc5bf;
  white-space: nowrap;
}

.cell-title {
  color: #e8fbf8;
  font-weight: 600;
  line-height: 1.35;
}

.cell-duration {
  color: #d4f3ed;
  white-space: nowrap;
}

.narrative-preview {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.45;
  color: #d4f3ed;
}

.binding-preview {
  color: #d4f3ed;
  line-height: 1.45;
  font-size: 12px;
  word-break: break-word;
}

.binding-preview + .binding-preview {
  margin-top: 4px;
}

.workbench-table input[type="text"],
.workbench-table textarea {
  width: 100%;
  border: 1px solid #3f6a72;
  background: #14333a;
  color: #def8f2;
  border-radius: 8px;
}

.workbench-table textarea {
  min-height: 96px;
  resize: vertical;
  line-height: 1.45;
}

.frame-mini-box {
  width: 122px;
  height: 68px;
  border-radius: 8px;
  border: 1px solid #39656d;
  background: #0f252a;
  overflow: hidden;
  margin-bottom: 6px;
}

.frame-mini-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.video-mini-box {
  width: 200px;
  height: 112px;
  border-radius: 8px;
  border: 1px solid #39656d;
  background: #0f252a;
  overflow: hidden;
}

.video-mini-box video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.progress-track-mini {
  margin-top: 6px;
  height: 6px;
}

.frame-url-preview {
  font-size: 11px;
  color: #9fc5bf;
  line-height: 1.35;
  word-break: break-all;
}

.workbench-table td a {
  display: inline-block;
  margin-top: 6px;
  color: #7ee9d0;
  text-decoration: none;
}

.workbench-table td a:hover {
  text-decoration: underline;
}

.row-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.row-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-spinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(228, 250, 245, 0.35);
  border-top-color: #e4faf5;
  animation: btn-spin 0.8s linear infinite;
}

@keyframes btn-spin {
  to {
    transform: rotate(360deg);
  }
}

.danger-inline {
  background: #7f1d1d;
  color: #fecaca;
}

.danger-inline:hover {
  background: #991b1b;
}

.dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(4, 14, 18, 0.68);
  z-index: 40;
  display: grid;
  place-items: center;
  padding: 16px;
}

.dialog-card {
  width: min(900px, 100%);
  max-height: 88vh;
  overflow: auto;
  border-radius: 12px;
  border: 1px solid #2f5861;
  background: linear-gradient(180deg, #123038, #0f242a);
  color: #d8f5ef;
  padding: 12px;
}

.confirm-card {
  width: min(520px, 100%);
}

.dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.dialog-head h4 {
  margin: 0;
  color: #e8fbf8;
}

.dialog-head span {
  font-size: 12px;
  color: #9fc5bf;
}

.dialog-body {
  margin-top: 10px;
}

.dialog-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dialog-grid .form-group {
  margin-bottom: 0;
}

.dialog-grid .form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: #bfe6de;
}

.field-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.field-label-row label {
  margin-bottom: 0;
}

.dialog-grid .form-group input,
.dialog-grid .form-group textarea {
  width: 100%;
  border: 1px solid #3f6a72;
  background: #14333a;
  color: #def8f2;
  border-radius: 8px;
}

.dialog-grid .full-width {
  grid-column: 1 / -1;
}

.dialog-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.confirm-body {
  margin-top: 10px;
  color: #d4f3ed;
  line-height: 1.5;
}

.shot-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  max-height: 560px;
  overflow: auto;
}

.shot-card {
  border: 1px solid #38616a;
  border-radius: 10px;
  background: linear-gradient(180deg, #173b43, #123138);
  overflow: hidden;
  cursor: pointer;
}

.shot-card.selected {
  border-color: #2dd4bf;
  box-shadow: 0 0 0 1px rgba(45, 212, 191, 0.55);
}

.shot-head {
  padding: 8px 9px;
  font-size: 11px;
  border-bottom: 1px solid #2f5861;
}

.shot-thumb {
  aspect-ratio: 16 / 9;
  background: #0f252a;
}

.shot-thumb img,
.frame-preview-box img,
.video-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.frame-preview-row {
  margin-top: 2px;
}

.frame-preview-panel {
  border: 1px solid #39656d;
  border-radius: 10px;
  background: #14333a;
  padding: 10px;
}

.preview-label {
  font-size: 12px;
  color: #bfe6de;
  margin-bottom: 6px;
}

.frame-preview-box {
  aspect-ratio: 16 / 9;
  border-radius: 8px;
  overflow: hidden;
  background: #0f252a;
}

.shot-body {
  padding: 8px 9px 6px;
}

.shot-state {
  border-radius: 999px;
  font-size: 10px;
  padding: 2px 8px;
  border: 1px solid transparent;
}

.state-idle { color: #9bbeb9; border-color: #3f6a72; }
.state-processing { color: #facc15; border-color: #a16207; background: rgba(161, 98, 7, 0.24); }
.state-ready { color: #6ee7b7; border-color: #0f766e; background: rgba(15, 118, 110, 0.24); }
.state-failed { color: #fca5a5; border-color: #b91c1c; background: rgba(185, 28, 28, 0.24); }

.row2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  color: #bfe6de;
}

.full-row {
  margin-top: 10px;
}

.binding-card {
  margin-top: 10px;
  border: 1px solid #39656d;
  border-radius: 10px;
  background: #14333a;
  padding: 10px;
}

.binding-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.binding-head label {
  color: #bfe6de;
}

.binding-head span {
  color: #9fc5bf;
  font-size: 12px;
}

.binding-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.binding-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.binding-item {
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  border: 1px solid #3f6a72;
  border-radius: 8px;
  background: rgba(19, 58, 66, 0.56);
  padding: 6px 8px;
  color: #def8f2;
  font-size: 12px;
}

.binding-item input {
  margin: 0;
  accent-color: #2dd4bf;
}

.binding-name {
  color: #e8fbf8;
}

.binding-meta {
  color: #9fc5bf;
  font-size: 11px;
}

.binding-summary {
  margin-top: 8px;
  color: #bfe6de;
  font-size: 12px;
}

.video-card,
.video-preview,
.task-progress {
  border: 1px solid #39656d;
  border-radius: 10px;
  background: #14333a;
  padding: 10px;
}

.video-card {
  margin-top: 10px;
}

.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: #2d545a;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5a3, #34d399);
  transition: width 0.4s ease;
}

.thumb-empty,
.empty-inline,
.empty-panel {
  border: 1px dashed #3f6a72;
  border-radius: 8px;
  padding: 12px;
  color: #86aaa3;
  font-size: 13px;
  background: rgba(14, 36, 42, 0.4);
  display: grid;
  place-items: center;
}

.empty-panel {
  min-height: 200px;
}

.ghost {
  background: #1b3e46;
  border: 1px solid #3f6a72;
  color: #def8f2;
}

.ghost:hover {
  background: #214a54;
}

.danger {
  background: #7f1d1d;
  color: #fecaca;
}

.danger:hover {
  background: #991b1b;
}

.mini {
  padding: 4px 8px;
  font-size: 12px;
  background: #2a545b;
  color: #e4faf5;
}

.check-row {
  display: flex;
  gap: 16px;
  color: #bfe6de;
  margin: 8px 0;
}

.mt8 {
  margin-top: 8px;
}

@media (max-width: 1400px) {
  .wb-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .wb-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .row2,
  .shot-grid,
  .dialog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
