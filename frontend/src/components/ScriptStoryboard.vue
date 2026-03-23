<template>
  <div class="phase">
    <h2>{{ phaseTitle }}</h2>

    <div class="episode-banner">当前编辑：第 {{ currentEpisodeNo }} 集</div>
    <div class="workflow-brief">
      <strong>{{ workflowHeadline }}</strong>
      <p>{{ workflowDescription }}</p>
    </div>

    <div class="layout">
      <div class="panel input-panel">
        <template v-if="isScriptInputStage || isCombinedStage">
          <div class="form-group">
            <label for="script">输入本集剧本或故事大纲</label>
            <textarea id="script" v-model="script" placeholder="请描述本集剧情、人物冲突和关键情节"></textarea>
          </div>

          <div class="form-group">
            <label for="duration">目标时长</label>
            <select id="duration" v-model="targetDuration">
              <option value="30s">30 秒预告</option>
              <option value="3min">3 分钟短剧</option>
              <option value="5min">5 分钟短剧</option>
              <option value="custom">自定义</option>
            </select>
            <input
              v-if="targetDuration === 'custom'"
              type="text"
              v-model="customDuration"
              placeholder="例如：10min"
              style="margin-top: 10px;"
            />
          </div>

          <div class="button-row">
            <button data-tour="btn-parse-script" @click="parseScript" :disabled="loading || !canSubmit">
              {{ loading ? '解析中...' : parseButtonLabel }}
            </button>
            <button v-if="loading" class="secondary-btn" @click="cancelParse">
              取消
            </button>
          </div>
        </template>

        <template v-else>
          <div class="stage-summary-card">
            <h3>分镜阶段输入摘要</h3>
            <p><strong>目标时长：</strong>{{ resolveDurationText() || initialDuration }}</p>
            <p><strong>当前场次数：</strong>{{ sceneCount }}</p>
            <textarea :value="script" rows="10" readonly></textarea>
            <div class="button-row">
              <button data-tour="btn-parse-script" @click="parseScript" :disabled="loading || !canSubmit">
                {{ loading ? '解析中...' : parseButtonLabel }}
              </button>
              <button class="secondary-btn" @click="goToScriptInputStage">返回剧本阶段</button>
              <button v-if="loading" class="secondary-btn" @click="cancelParse">取消</button>
            </div>
          </div>
        </template>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="loading" class="loading-indicator">正在解析，已等待 {{ elapsedSeconds }}s</div>
      </div>

      <div class="panel result-panel">
        <div v-if="scriptResult" class="result">
          <h3>{{ resultTitle }}</h3>
          <div v-if="scriptResult._meta && scriptResult._meta.used_fallback" class="error-message" style="margin-bottom: 12px;">
            当前结果使用了后端兜底规则：{{ scriptResult._meta.error || '未知错误' }}
          </div>
          <div v-if="storyPackage" class="story-package-card">
            <div class="table-header">
              <h4>故事设计包</h4>
              <span>{{ storyPackage.genre || '东方动漫风剧情短片' }}</span>
            </div>
            <p v-if="storyPackage.logline"><strong>一句话剧情：</strong>{{ storyPackage.logline }}</p>
            <p v-if="storyPackage.theme"><strong>主题：</strong>{{ storyPackage.theme }}</p>
            <p v-if="storyPackage.visual_strategy"><strong>视觉策略：</strong>{{ storyPackage.visual_strategy }}</p>
            <div v-if="storyCharacters.length" class="plan-list">
              <h5>角色圣经</h5>
              <ul>
                <li v-for="(item, index) in storyCharacters" :key="`char-${index}`">
                  {{ formatStoryCharacter(item) }}
                </li>
              </ul>
            </div>
            <div v-if="storyBeats.length" class="plan-list">
              <h5>剧情节拍表</h5>
              <ul>
                <li v-for="(item, index) in storyBeats" :key="`beat-${index}`">
                  {{ formatStoryBeat(item, index) }}
                </li>
              </ul>
            </div>
          </div>

          <div v-if="isScriptInputStage && sceneRows.length" class="stage-summary-card result-jump-card">
            <h4>分镜已生成</h4>
            <p>当前结果包含 {{ sceneCount }} 个场次，可以进入下一阶段逐条确认 shot plan。</p>
            <div class="button-row">
              <button @click="goToStoryboardStage">进入分镜阶段</button>
            </div>
          </div>

          <div class="table-wrap" v-if="(isStoryboardStage || isCombinedStage) && sceneRows.length">
            <div class="table-header">
              <h4>{{ storyboardTableTitle }}</h4>
              <button class="secondary-btn" data-tour="btn-load-all-scenes" @click="loadAllScenesToShots">{{ syncShotsButtonLabel }}</button>
            </div>
            <table class="scene-table">
              <thead>
                <tr>
                  <th>场次</th>
                  <th>场景描述</th>
                  <th>镜头概述</th>
                  <th>详细分镜</th>
                  <th>镜头部署</th>
                  <th>时长</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(scene, index) in sceneRows" :key="`row-${index}`">
                  <td>{{ scene.scene_id || index + 1 }}</td>
                  <td>{{ scene.description || '-' }}</td>
                  <td>{{ scene.shot_description || '-' }}</td>
                  <td>{{ scene.detailed_shot_description || scene.shot_description || '-' }}</td>
                  <td>{{ sceneShotPlanSummary(scene) }}</td>
                  <td>{{ scene.duration || '5s' }}</td>
                  <td>
                    <button class="mini-btn" @click="loadSingleSceneToShots(scene)">同步为镜头草稿</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-for="scene in ((isStoryboardStage || isCombinedStage) ? scriptResult.scenes : [])" :key="scene.scene_id" class="scene-item">
            <div v-if="!scene._editing" class="scene-view">
              <div class="scene-header">
                <h4>场次 {{ scene.scene_id }}: {{ scene.description }}</h4>
                <button class="icon-btn edit-btn" @click="editScene(scene)" title="编辑">✎</button>
              </div>
              <p>时间: {{ scene.time }} | 氛围: {{ scene.mood }}</p>
              <p>镜头: {{ scene.shot_description }}</p>
              <p v-if="scene.detailed_shot_description">详细分镜: {{ scene.detailed_shot_description }}</p>
              <p v-if="scene.staging_notes">镜头部署摘要: {{ scene.staging_notes }}</p>
              <div v-if="Array.isArray(scene.shot_plan) && scene.shot_plan.length" class="plan-list">
                <h5>镜头部署节拍</h5>
                <ul>
                  <li v-for="(planItem, planIndex) in scene.shot_plan" :key="`plan-${scene.scene_id}-${planIndex}`">
                    {{ formatShotPlanItem(planItem, planIndex) }}
                  </li>
                </ul>
              </div>
              <p v-if="Array.isArray(scene.character_actions) && scene.character_actions.length">动作: {{ scene.character_actions.join(', ') }}</p>
              <p v-if="Array.isArray(scene.dialogue) && scene.dialogue.length">对话: {{ scene.dialogue.join(', ') }}</p>
              <p v-if="scene.dialogue_details">对白细节: {{ scene.dialogue_details }}</p>
              <p>时长: {{ scene.duration }}</p>
              <div v-if="scene.prompt" class="prompt">
                <h5>提示词</h5>
                <p>{{ scene.prompt }}</p>
              </div>
            </div>
            <div v-else class="scene-edit">
              <div class="form-row">
                <div class="form-group half">
                  <label>场次 ID</label>
                  <input v-model="scene.scene_id" type="text" />
                </div>
                <div class="form-group half">
                  <label>时长</label>
                  <input v-model="scene.duration" type="text" />
                </div>
              </div>
              <div class="form-group">
                <label>场景描述</label>
                <input v-model="scene.description" type="text" />
              </div>
              <div class="form-row">
                <div class="form-group half">
                  <label>时间</label>
                  <input v-model="scene.time" type="text" />
                </div>
                <div class="form-group half">
                  <label>氛围</label>
                  <input v-model="scene.mood" type="text" />
                </div>
              </div>
              <div class="form-group">
                <label>镜头描述</label>
                <textarea v-model="scene.shot_description" rows="2"></textarea>
              </div>
              <div class="form-group">
                <label>详细分镜描述</label>
                <textarea v-model="scene.detailed_shot_description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>镜头部署摘要</label>
                <textarea v-model="scene.staging_notes" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>对白细节</label>
                <textarea v-model="scene.dialogue_details" rows="2"></textarea>
              </div>
              <div class="form-group">
                <label>提示词</label>
                <textarea v-model="scene.prompt" rows="3"></textarea>
              </div>
              <div class="button-row">
                <button @click="saveSceneEdit(scene)" class="small-btn">保存</button>
                <button @click="cancelSceneEdit(scene)" class="small-btn secondary-btn">取消</button>
              </div>
            </div>
          </div>
        </div>

        <div class="editor">
          <h3>返回 JSON（可编辑）</h3>
          <textarea v-model="rawResultText" class="json-editor" placeholder="生成后可在此直接修改 JSON"></textarea>
          <div class="button-row">
            <button @click="applyEditedResult" :disabled="!rawResultText.trim()">应用修改</button>
            <button v-if="scriptResult" class="secondary-btn" @click="resetEditedResult">重置</button>
          </div>
          <div v-if="editError" class="error-message">{{ editError }}</div>
        </div>

        <div v-if="history && history.length" class="history">
          <h3>本集生成记录</h3>
          <div class="history-list">
            <div v-for="item in history" :key="item.id" class="history-item">
              <div class="history-main">
                <div class="history-title">{{ item.title }}</div>
                <div class="history-meta">{{ item.createdAt }}</div>
              </div>
              <button class="secondary-btn" @click="loadHistory(item)">载入</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ScriptStoryboard',
  props: {
    currentEpisodeNo: {
      type: Number,
      default: 1
    },
    initialScript: {
      type: String,
      default: ''
    },
    initialDuration: {
      type: String,
      default: '3min'
    },
    initialResult: {
      type: Object,
      default: null
    },
    history: {
      type: Array,
      default: () => []
    },
    workflowStage: {
      type: String,
      default: 'script-storyboard'
    }
  },
  data() {
    return {
      script: '',
      scriptResult: null,
      targetDuration: '3min',
      customDuration: '',
      loading: false,
      errorMessage: '',
      editError: '',
      rawResultText: '',
      elapsedSeconds: 0,
      timerId: null,
      abortController: null
    };
  },
  computed: {
    isCombinedStage() {
      return this.workflowStage === 'script-storyboard';
    },
    isScriptInputStage() {
      return this.workflowStage === 'script-input';
    },
    isStoryboardStage() {
      return this.workflowStage === 'storyboard';
    },
    phaseTitle() {
      if (this.isCombinedStage) return 'Phase 01: 剧本与分镜';
      return this.isStoryboardStage ? 'Phase 02: 分镜' : 'Phase 01: 剧本';
    },
    workflowHeadline() {
      if (this.isCombinedStage) {
        return '当前阶段同时负责剧本解析和分镜确认，先生成故事设计包，再检查 shot plan 与场次结构。';
      }
      return this.isStoryboardStage
        ? '当前阶段聚焦镜头拆解：检查每场戏的 shot plan、时长和动作节拍。'
        : '当前阶段聚焦剧情改编：把剧本或小说片段整理成可拍摄的故事设计包。';
    },
    workflowDescription() {
      if (this.isCombinedStage) {
        return '在这个页面完成剧本输入、分镜确认和镜头草稿同步，后续再进入“资产与选角”和“导演工作台”。';
      }
      return this.isStoryboardStage
        ? '确认分镜后，把场次同步为镜头草稿，下一步进入“场景风格生成”和“角色库选择”。'
        : '先输入剧本、梗概或小说片段，系统会产出故事设计包、场次结构和基础分镜。';
    },
    parseButtonLabel() {
      if (this.isCombinedStage) return '生成本集分镜脚本';
      return this.isStoryboardStage ? '重生成分镜脚本' : '生成剧情与分镜基础';
    },
    resultTitle() {
      if (this.isCombinedStage) return '解析结果';
      return this.isStoryboardStage ? '分镜确认区' : '剧情与分镜结果';
    },
    storyboardTableTitle() {
      if (this.isCombinedStage) return '本集分镜表';
      return this.isStoryboardStage ? '镜头草稿同步表' : '本集分镜表';
    },
    syncShotsButtonLabel() {
      if (this.isCombinedStage) return '一键载入导演工作台';
      return this.isStoryboardStage ? '同步全部镜头草稿' : '生成后同步镜头草稿';
    },
    sceneCount() {
      return this.sceneRows.length;
    },
    canSubmit() {
      return this.script.trim().length > 0;
    },
    storyPackage() {
      const value = this.scriptResult?.story_package;
      return value && typeof value === 'object' ? value : null;
    },
    storyCharacters() {
      return Array.isArray(this.storyPackage?.character_bible) ? this.storyPackage.character_bible.slice(0, 6) : [];
    },
    storyBeats() {
      return Array.isArray(this.storyPackage?.beat_sheet) ? this.storyPackage.beat_sheet.slice(0, 8) : [];
    },
    sceneRows() {
      const rows = this.scriptResult?.scenes;
      return Array.isArray(rows) ? rows : [];
    }
  },
  watch: {
    initialScript: {
      immediate: true,
      handler(newVal) {
        this.script = newVal || '';
      }
    },
    initialDuration: {
      immediate: true,
      handler(newVal) {
        this.applyDuration(newVal || '3min');
      }
    },
    initialResult: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.scriptResult = newVal;
          this.rawResultText = JSON.stringify(newVal, null, 2);
        } else {
          this.scriptResult = null;
          this.rawResultText = '';
        }
      }
    }
  },
  beforeUnmount() {
    this.stopTimer();
    if (this.abortController) {
      this.abortController.abort();
    }
  },
  methods: {
    resolveDurationText() {
      return this.targetDuration === 'custom' ? this.customDuration.trim() : this.targetDuration;
    },
    getParseTimeoutMs(durationText) {
      const text = String(durationText || '').trim().toLowerCase();
      if (!text) {
        return 120000;
      }
      if (text === '30s') {
        return 120000;
      }
      if (text === '3min') {
        return 300000;
      }
      if (text === '5min') {
        return 420000;
      }

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
    applyDuration(value) {
      if (['30s', '3min', '5min'].includes(value)) {
        this.targetDuration = value;
        this.customDuration = '';
        return;
      }
      this.targetDuration = 'custom';
      this.customDuration = value || '';
    },
    startTimer() {
      this.elapsedSeconds = 0;
      if (this.timerId) {
        clearInterval(this.timerId);
      }
      this.timerId = setInterval(() => {
        this.elapsedSeconds += 1;
      }, 1000);
    },
    stopTimer() {
      if (this.timerId) {
        clearInterval(this.timerId);
        this.timerId = null;
      }
    },
    goToStoryboardStage() {
      if (this.$route?.name === 'storyboard') return;
      void this.$router.push({ name: 'storyboard' });
    },
    goToScriptInputStage() {
      if (this.$route?.name === 'script-input') return;
      void this.$router.push({ name: 'script-input' });
    },
    validateScriptRequest() {
      const scriptText = this.script.trim();
      if (!scriptText) {
        return {
          ok: false,
          scriptText: '',
          durationText: '',
          errorMessage: '请输入剧本内容'
        };
      }
      if (this.targetDuration === 'custom' && !this.customDuration.trim()) {
        return {
          ok: false,
          scriptText: '',
          durationText: '',
          errorMessage: '请输入自定义时长'
        };
      }
      return {
        ok: true,
        scriptText,
        durationText: this.resolveDurationText(),
        errorMessage: ''
      };
    },
    emitScriptUpdate(result, scriptText, durationText) {
      this.scriptResult = result && typeof result === 'object' ? result : null;
      this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : '';
      this.$emit('script-updated', {
        script: scriptText || this.script.trim(),
        duration: durationText || this.resolveDurationText() || this.initialDuration || '3min',
        result: this.scriptResult
      });
    },
    async parseScript() {
      const { ok, scriptText, durationText, errorMessage } = this.validateScriptRequest();
      if (!ok) {
        this.errorMessage = errorMessage;
        return;
      }

      this.errorMessage = '';
      this.editError = '';
      this.loading = true;
      const parseTimeoutMs = this.getParseTimeoutMs(durationText);
      this.abortController = new AbortController();
      this.startTimer();
      try {
        const response = await axios.post('/api/parse-script', {
          script: scriptText,
          duration: durationText
        }, {
          signal: this.abortController.signal,
          timeout: parseTimeoutMs
        });
        this.scriptResult = response.data;
        this.rawResultText = JSON.stringify(response.data, null, 2);
        this.$emit('script-generated', {
          episode_no: this.currentEpisodeNo,
          script: scriptText,
          duration: durationText,
          result: response.data
        });
        if (this.isScriptInputStage) {
          this.goToStoryboardStage();
        }
      } catch (error) {
        if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
          this.errorMessage = '已取消解析';
        } else if (error.code === 'ECONNABORTED') {
          const timeoutSec = Math.round(parseTimeoutMs / 1000);
          this.errorMessage = `解析超时（${timeoutSec}s），请稍后重试或缩短时长`;
        } else {
          console.error('解析剧本失败:', error);
          this.errorMessage = '解析失败，请检查模型配置或后端服务';
        }
      } finally {
        this.loading = false;
        this.stopTimer();
        this.abortController = null;
      }
    },
    cancelParse() {
      if (this.abortController) {
        this.abortController.abort();
      }
    },
    applyEditedResult() {
      this.editError = '';
      try {
        const parsed = JSON.parse(this.rawResultText);
        this.emitScriptUpdate(parsed, this.script.trim(), this.resolveDurationText());
      } catch (e) {
        this.editError = 'JSON 格式错误，请检查后重试';
      }
    },
    resetEditedResult() {
      if (this.scriptResult) {
        this.rawResultText = JSON.stringify(this.scriptResult, null, 2);
      }
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
    sceneShotPlanSummary(scene) {
      const explicitNotes = String(scene?.staging_notes || '').trim();
      if (explicitNotes) {
        const oneLine = explicitNotes.replace(/\s+/g, ' ').trim();
        return oneLine.length > 40 ? `${oneLine.slice(0, 40)}...` : oneLine;
      }
      const plan = Array.isArray(scene?.shot_plan) ? scene.shot_plan : [];
      if (!plan.length) return '-';
      const first = this.formatShotPlanItem(plan[0], 0);
      return first.length > 40 ? `${first.slice(0, 40)}...` : first;
    },
    buildSceneStagingNotes(scene) {
      const explicitNotes = String(scene?.staging_notes || '').trim();
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
      const explicit = String(scene?.action_details || '').trim();
      if (explicit) return explicit;
      const actions = Array.isArray(scene?.character_actions) ? scene.character_actions : [];
      return actions.map((item) => String(item || '').trim()).filter(Boolean).join('\n');
    },
    ensureGradualTargetState(targetState = '', motionInstruction = '') {
      let text = String(targetState || '').trim();
      const motion = String(motionInstruction || '').trim();
      if (!text) {
        return motion
          ? `承接“${motion.slice(0, 28)}”，动作幅度逐渐减弱并稳定，环境反馈缓慢收束。`
          : '';
      }
      text = text
        .replace(/突然静止/g, '动作幅度逐渐减弱并趋于稳定')
        .replace(/瞬间静止/g, '动作幅度逐渐减弱并趋于稳定')
        .replace(/突然爆炸/g, '能量持续抬升后向外扩散')
        .replace(/瞬间爆炸/g, '能量持续抬升后向外扩散')
        .replace(/突然/g, '逐渐')
        .replace(/瞬间/g, '逐步')
        .replace(/立刻/g, '随动作推进')
        .replace(/马上/g, '随动作推进');
      if (!/(逐渐|逐步|缓慢|持续|收束|趋于|回落)/.test(text)) {
        text = `${text}，并逐渐收束到稳定状态`;
      }
      if (motion) {
        const anchor = motion.slice(0, 20);
        if (anchor && !text.includes(anchor)) {
          text = `承接“${anchor}”，${text}`;
        }
      }
      return text.replace(/，+/g, '，').trim();
    },
    ensureMotionInstructionFromPrevState(prevState = '', motionInstruction = '') {
      const prev = String(prevState || '').trim();
      let motion = String(motionInstruction || '').trim();
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
      if (prev) {
        const anchor = prev.slice(0, 20);
        if (anchor && !motion.includes(anchor) && !motion.includes('承接')) {
          motion = `承接“${anchor}”，${motion}`;
        }
      }
      return motion.replace(/，+/g, '，').trim();
    },
    inferSpatialAnchor(text = '') {
      return String(text || '')
        .split(/[，。；\n]/)
        .map((item) => String(item || '').trim())
        .find((item) => item) || '';
    },
    ensureVisualAnchorWithPrevState(visualAnchor = '', prevState = '', targetState = '', sourceDescription = '') {
      const parts = [];
      const explicit = String(visualAnchor || '').trim();
      const prev = String(prevState || '').trim();
      const target = String(targetState || '').trim();
      const space = this.inferSpatialAnchor(sourceDescription);
      if (explicit) parts.push(explicit);
      if (space) parts.push(`同一空间锚点：${space}`);
      if (prev) parts.push(`承接上一镜头目标状态：${prev.slice(0, 42)}`);
      if (target) parts.push(`当前镜头状态收束：${target.slice(0, 42)}`);
      return [...new Set(parts.filter(Boolean))].join('；').trim();
    },
    ensureContinuityHint(continuityHint = '', targetState = '', prevState = '', sourceDescription = '') {
      let hint = String(continuityHint || '').trim();
      const target = String(targetState || '').trim();
      const prev = String(prevState || '').trim();
      const space = this.inferSpatialAnchor(sourceDescription);
      if (!hint) {
        const direction = target || '动作能量持续推进后收束';
        hint = `下一镜头变化方向：继承当前状态并沿“${direction.slice(0, 34)}”继续演化。`;
      }
      const extras = [];
      if (!hint.includes('下一镜头')) {
        const direction = target || '动作能量持续推进后收束';
        extras.push(`下一镜头变化方向：沿“${direction.slice(0, 34)}”继续演化`);
      }
      if (!hint.includes('空间')) {
        extras.push(`空间连续：保持同一地点（${space || '当前场景'}），仅允许机位或景别平滑变化`);
      }
      if (!hint.includes('物理') && !hint.includes('过渡')) {
        extras.push('物理连续：风场、能量、姿态变化必须有过渡，禁止突变');
      }
      if (prev && !hint.includes('继承')) {
        extras.push(`状态继承基线：${prev.slice(0, 30)}`);
      }
      return [...new Set([hint, ...extras].filter(Boolean))]
        .join('。')
        .replace(/。+/g, '。')
        .replace(/。$/, '')
        .concat('。');
    },
    formatDialogueBeatItem(item, index = 0) {
      if (!item || typeof item !== 'object') return String(item || '').trim();
      const beatId = String(item.beat_id || item.id || index + 1).trim();
      const speaker = String(item.speaker || item.role || `角色${index + 1}`).trim();
      const line = String(item.line || item.dialogue || '').trim();
      const tone = String(item.tone || '').trim();
      const reaction = String(item.reaction || '').trim();
      const parts = [];
      if (speaker || line) parts.push(`${speaker}${line ? `：${line}` : ''}`);
      if (tone) parts.push(`语气:${tone}`);
      if (reaction) parts.push(`反应:${reaction}`);
      const content = parts.join(' | ').trim();
      return content ? `${beatId}. ${content}` : '';
    },
    formatStoryCharacter(item) {
      if (!item || typeof item !== 'object') return String(item || '').trim();
      const name = String(item.name || '人物').trim();
      const role = String(item.role || '').trim();
      const goal = String(item.goal || '').trim();
      const tension = String(item.tension || '').trim();
      return [name, role && `角色:${role}`, goal && `目标:${goal}`, tension && `张力:${tension}`]
        .filter(Boolean)
        .join(' | ');
    },
    formatStoryBeat(item, index = 0) {
      if (!item || typeof item !== 'object') return String(item || '').trim();
      const beatId = String(item.beat_id || index + 1).trim();
      const label = String(item.label || '剧情节拍').trim();
      const summary = String(item.summary || '').trim();
      const conflict = String(item.conflict || '').trim();
      return `${beatId}. ${label}${summary ? `：${summary}` : ''}${conflict ? ` | 冲突:${conflict}` : ''}`;
    },
    buildSceneDialogueBeatDetails(scene) {
      const explicit = String(scene?.dialogue_beat_details || '').trim();
      if (explicit) return explicit;
      const beats = Array.isArray(scene?.dialogue_beats) ? scene.dialogue_beats : [];
      return beats
        .slice(0, 6)
        .map((item, index) => this.formatDialogueBeatItem(item, index))
        .filter(Boolean)
        .join('\n');
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
        scene?.start_frame_goal ||
        scene?.StartFrame ||
        '承接上一镜头同场景基础状态'
      ).trim();
      const motionInstruction = String(
        safeBeat?.motion_instruction ||
        safeBeat?.motionInstruction ||
        safeBeat?.action ||
        blocking ||
        sceneActionLine ||
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
      const shotSummary = lensSummary || sceneShotSummary || `镜头 ${beatId}`;
      const detailedShotDescription = [
        shotSummary && `镜头设计：${shotSummary}`,
        blocking && `当前动作：${blocking}`,
        dialogue && `对白重点：${dialogue}`,
        transition && `镜头衔接：${transition}`
      ].filter(Boolean).join('，') || blocking || shotSummary || sourceDescription;
      const detailedPlot = [
        shotDeployment ? `分镜调度：\n${shotDeployment}` : '',
        actionDetails ? `动作细节：\n${actionDetails}` : '',
        dialogueDetails ? `对白细节：\n${dialogueDetails}` : '',
        dialogueBeatDetails ? `对白节拍：\n${dialogueBeatDetails}` : ''
      ].filter(Boolean).join('\n\n');

      return {
        sceneNo,
        title: `场次 ${sceneNo} · 镜头 ${beatId}`,
        duration: duration || scene?.duration || '5s',
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        detailedPlot,
        dialogueDetails,
        dialogueBeatDetails,
        actionDetails,
        shotDeployment,
        prevState,
        prev_state: prevState,
        motionInstruction: normalizedMotionInstruction,
        motion_instruction: normalizedMotionInstruction,
        targetState,
        target_state: targetState,
        visualAnchor,
        visual_anchor: visualAnchor,
        continuityHint,
        continuity_hint: continuityHint,
        startFrame: {
          description: [shotSummary, blocking].filter(Boolean).join('，') || detailedShotDescription,
          enhanced_prompt: '',
          image_url: ''
        },
        endFrame: {
          description: '',
          enhanced_prompt: '',
          image_url: ''
        },
        videoUrl: '',
        videoTask: {
          taskId: '',
          status: '',
          message: ''
        }
      };
    },
    buildShotFromScene(scene, fallbackIndex = 1) {
      const sceneNo = scene?.scene_id || fallbackIndex;
      const sourceDescription = String(scene?.description || '').trim();
      const shotSummary = String(scene?.shot_description || '').trim();
      const detailedShotDescription = String(scene?.detailed_shot_description || shotSummary || sourceDescription || '').trim();
      const dialogueDetails = String(
        scene?.dialogue_details ||
        (Array.isArray(scene?.dialogue_beats)
          ? scene.dialogue_beats
            .map((beat, index) => {
              const speaker = String(beat?.speaker || `角色${index + 1}`).trim();
              const line = String(beat?.line || beat?.dialogue || '').trim();
              const tone = String(beat?.tone || '').trim();
              return line ? `${speaker}：${line}${tone ? `（${tone}）` : ''}` : '';
            })
            .filter(Boolean)
            .join('；')
          : '') ||
        (Array.isArray(scene?.dialogue) ? scene.dialogue.join('；') : '') ||
        ''
      ).trim();
      const shotDeployment = this.buildSceneStagingNotes(scene);
      const actionDetails = this.buildSceneActionDetails(scene);
      const dialogueBeatDetails = this.buildSceneDialogueBeatDetails(scene);
      const prevState = String(
        scene?.prev_state ||
        scene?.previous_state ||
        scene?.start_frame_goal ||
        scene?.StartFrame ||
        '承接上一镜头同场景基础状态'
      ).trim();
      const motionInstruction = String(
        scene?.motion_instruction ||
        scene?.motionInstruction ||
        scene?.Action ||
        scene?.action ||
        actionDetails.split('\n').find((line) => String(line || '').trim()) ||
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
      const detailedPlot = [
        shotDeployment ? `分镜调度：\n${shotDeployment}` : '',
        actionDetails ? `动作细节：\n${actionDetails}` : '',
        dialogueDetails ? `对白细节：\n${dialogueDetails}` : '',
        dialogueBeatDetails ? `对白节拍：\n${dialogueBeatDetails}` : ''
      ].filter(Boolean).join('\n\n');
      return {
        sceneNo,
        title: `场次 ${sceneNo}`,
        duration: scene?.duration || '5s',
        sourceDescription,
        shotSummary,
        detailedShotDescription,
        detailedPlot,
        dialogueDetails,
        dialogueBeatDetails,
        actionDetails,
        shotDeployment,
        prevState,
        prev_state: prevState,
        motionInstruction: normalizedMotionInstruction,
        motion_instruction: normalizedMotionInstruction,
        targetState,
        target_state: targetState,
        visualAnchor,
        visual_anchor: visualAnchor,
        continuityHint,
        continuity_hint: continuityHint,
        startFrame: {
          description: detailedShotDescription,
          enhanced_prompt: '',
          image_url: ''
        },
        endFrame: {
          description: '',
          enhanced_prompt: '',
          image_url: ''
        },
        videoUrl: '',
        videoTask: {
          taskId: '',
          status: '',
          message: ''
        }
      };
    },
    buildShotsFromScene(scene, fallbackIndex = 1) {
      const sceneNo = scene?.scene_id || fallbackIndex;
      const plan = Array.isArray(scene?.shot_plan) ? scene.shot_plan.filter((item) => item !== undefined && item !== null) : [];
      if (plan.length) {
        return this.enforceStateFlowAcrossShots(
          plan.map((beat, beatIndex) => this.buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex))
        );
      }
      return this.enforceStateFlowAcrossShots([this.buildShotFromScene(scene, fallbackIndex)]);
    },
    enforceStateFlowAcrossShots(shots = []) {
      let previousTargetState = '';
      return (Array.isArray(shots) ? shots : []).map((item) => {
        const shot = item && typeof item === 'object' ? { ...item } : {};
        const prevState = String(
          shot.prevState ||
          shot.prev_state ||
          previousTargetState ||
          shot.startFrameGoal ||
          shot.start_frame_goal ||
          shot.startFrame?.description ||
          '承接上一镜头同场景基础状态'
        ).trim();
        const motionInstruction = this.ensureMotionInstructionFromPrevState(
          prevState,
          shot.motionInstruction || shot.motion_instruction
        );
        const targetState = this.ensureGradualTargetState(
          shot.targetState || shot.target_state,
          motionInstruction
        );
        const visualAnchor = this.ensureVisualAnchorWithPrevState(
          shot.visualAnchor || shot.visual_anchor,
          prevState,
          targetState,
          shot.sourceDescription
        );
        const continuityHint = this.ensureContinuityHint(
          shot.continuityHint || shot.continuity_hint,
          targetState,
          prevState,
          shot.sourceDescription
        );
        shot.prevState = prevState;
        shot.prev_state = prevState;
        shot.motionInstruction = motionInstruction;
        shot.motion_instruction = motionInstruction;
        shot.targetState = targetState;
        shot.target_state = targetState;
        shot.visualAnchor = visualAnchor;
        shot.visual_anchor = visualAnchor;
        shot.continuityHint = continuityHint;
        shot.continuity_hint = continuityHint;
        if (!shot.endFrame) shot.endFrame = { description: '', enhanced_prompt: '', image_url: '' };
        if (!String(shot.endFrame.description || '').trim() && targetState) {
          shot.endFrame.description = targetState;
        }
        previousTargetState = targetState || previousTargetState;
        return shot;
      });
    },
    loadSingleSceneToShots(scene) {
      const shots = this.buildShotsFromScene(scene, 1);
      this.$emit('load-scenes-as-shots', shots);
    },
    loadAllScenesToShots() {
      const shots = this.enforceStateFlowAcrossShots(
        this.sceneRows.reduce((acc, scene, index) => acc.concat(this.buildShotsFromScene(scene, index + 1)), [])
      );
      this.$emit('load-scenes-as-shots', shots);
    },
    editScene(scene) {
      scene._editing = true;
      scene._original = JSON.parse(JSON.stringify(scene));
    },
    saveSceneEdit(scene) {
      delete scene._editing;
      delete scene._original;
      this.rawResultText = JSON.stringify(this.scriptResult, null, 2);
      this.emitScriptUpdate(this.scriptResult, this.script.trim(), this.resolveDurationText());
    },
    cancelSceneEdit(scene) {
      Object.assign(scene, scene._original);
      delete scene._editing;
      delete scene._original;
    },
    loadHistory(item) {
      this.$emit('history-selected', item);
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

.layout {
  display: grid;
  grid-template-columns: minmax(320px, 420px) 1fr;
  gap: 16px;
}

.episode-banner {
  margin-bottom: 12px;
  background: rgba(45, 212, 191, 0.14);
  border: 1px solid #2dd4bf;
  color: #8ff5de;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 600;
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

.panel {
  background-color: #123038;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid #2f5861;
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

.panel :deep(input::placeholder),
.panel :deep(textarea::placeholder) {
  color: #8fb1ac;
}

.panel :deep(input:focus),
.panel :deep(select:focus),
.panel :deep(textarea:focus) {
  outline-color: rgba(45, 212, 191, 0.35);
  border-color: #2dd4bf;
}

.input-panel textarea {
  min-height: 200px;
}

.stage-summary-card {
  padding: 14px;
  border-radius: 10px;
  background: #163840;
  border: 1px solid #2f5861;
}

.stage-summary-card h3,
.stage-summary-card h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #e8fbf8;
}

.stage-summary-card p {
  margin: 0 0 10px;
  color: #bfe6de;
  line-height: 1.5;
}

.stage-summary-card textarea {
  width: 100%;
  min-height: 180px;
  resize: vertical;
}

.result-jump-card {
  margin-top: 14px;
}

.button-row {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.secondary-btn {
  background-color: #1b3e46;
  color: #def8f2;
}

.error-message {
  margin-top: 10px;
  padding: 10px;
  background-color: rgba(185, 28, 28, 0.2);
  color: #fecaca;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid rgba(248, 113, 113, 0.45);
}

.loading-indicator {
  margin-top: 10px;
  padding: 10px;
  background-color: #163840;
  border-radius: 6px;
  font-size: 14px;
  color: #bfe6de;
  border: 1px solid #2f5861;
}

.table-wrap {
  margin-bottom: 14px;
  border: 1px solid #2f5861;
  border-radius: 8px;
  overflow: hidden;
}

.story-package-card {
  margin-bottom: 14px;
  border: 1px solid #2f5861;
  border-radius: 8px;
  padding: 12px;
  background: #102a31;
}

.story-package-card p {
  margin: 8px 0;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: #173b43;
}

.table-header h4 {
  color: #e8fbf8;
}

.scene-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.scene-table th,
.scene-table td {
  border-top: 1px solid #2f5861;
  text-align: left;
  padding: 8px;
  vertical-align: top;
  color: #d8f5ef;
}

.scene-table th {
  background: #1a3f47;
  color: #c5e7de;
}

.mini-btn {
  padding: 4px 8px;
  font-size: 12px;
}

.editor {
  margin-top: 20px;
}

.result {
  margin-top: 16px;
  padding: 12px;
  background-color: #163840;
  border: 1px solid #2f5861;
  border-radius: 8px;
  color: #e8fbf8;
}

.result h3,
.result h4,
.result h5 {
  color: #e8fbf8;
}

.scene-item {
  background-color: #17363d;
  border: 1px solid #2f5861;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
}

.scene-view h4,
.scene-view p {
  color: #d8f5ef;
}

.plan-list {
  margin: 8px 0;
  padding: 8px;
  border: 1px solid #2f5861;
  border-radius: 6px;
  background: #122f35;
}

.plan-list h5 {
  margin: 0 0 6px;
  color: #c7ece5;
}

.plan-list ul {
  margin: 0;
  padding-left: 18px;
  color: #c7ece5;
}

.plan-list li {
  margin: 4px 0;
}

.json-editor {
  width: 100%;
  min-height: 220px;
  margin-top: 10px;
  border: 1px solid #3f6a72;
  border-radius: 8px;
  padding: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 13px;
  background: #0f252a;
  color: #d8f5ef;
}

.history {
  margin-top: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #163840;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #2f5861;
}

.history-title {
  font-weight: 600;
  color: #e8fbf8;
}

.history-meta {
  font-size: 12px;
  color: #9fc5bf;
  margin-top: 4px;
}

.prompt {
  margin-top: 8px;
  padding: 8px;
  background-color: #163840;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid #2f5861;
}

.prompt h5 {
  margin-bottom: 4px;
  color: #7be6d2;
}

.scene-view {
  position: relative;
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.75;
  margin-right: 0;
  color: #9fc5bf;
}

.icon-btn:hover {
  opacity: 1;
}

.scene-edit {
  background-color: #163840;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #2f5861;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-group.half {
  flex: 1;
}

.small-btn {
  padding: 5px 10px;
  font-size: 12px;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
