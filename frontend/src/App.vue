<template>
  <div class="app-root">
    <div v-if="!authReady" class="auth-loading-screen">正在检查登录状态...</div>
    <LoginPage v-else-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    <div v-else class="studio-shell">
    <aside class="studio-sidebar">
      <div class="brand-block">
        <div class="brand-icon">◎</div>
        <div>
          <h1>灵映台</h1>
          <p>STUDIO PRO</p>
        </div>
      </div>

      <button class="back-link" @click="currentProjectId = ''; selectProject()">← 返回项目列表</button>

      <div class="project-glance">
        <div class="project-glance-label">当前项目</div>
        <div class="project-glance-name">{{ currentProjectName || '未选择项目' }}</div>
        <div class="project-glance-meta">第 {{ currentEpisodeNo }} 集</div>
      </div>

      <nav class="phase-nav">
        <button
          v-for="(phase, index) in phases"
          :key="index"
          class="phase-item"
          :class="{ active: activePhaseIndex === index }"
          :data-tour="`phase-nav-${index}`"
          @click="goToPhase(index)"
        >
          <span class="phase-index">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="phase-title">{{ phase.title }}</span>
          <span class="phase-tag">Phase {{ String(index + 1).padStart(2, '0') }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">系统设置</div>
    </aside>

    <section class="studio-stage">
      <header class="stage-topbar">
        <div class="stage-title-block">
          <h2>{{ activePhaseTitle }}</h2>
          <span>{{ activePhaseIndex + 1 }} / {{ phases.length }} 完成</span>
        </div>

        <div class="stage-toolbar">
          <select v-model="currentProjectId" @change="selectProject" class="toolbar-field project-select">
            <option value="">选择项目</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }} | {{ project.script_title || '未命名剧本' }} 第{{ project.episode_no }}集
            </option>
          </select>

          <input
            v-model="currentProjectName"
            type="text"
            :disabled="!currentProjectId"
            class="toolbar-field"
            placeholder="项目名"
          />

          <input
            v-model="currentScriptTitle"
            type="text"
            :disabled="!currentProjectId"
            class="toolbar-field"
            placeholder="剧本名"
          />

          <div class="episode-control">
            <select v-model.number="currentEpisodeNo" :disabled="!currentProjectId" class="toolbar-field">
              <option v-for="episode in episodeOptions" :key="`ep-${episode}`" :value="episode">第 {{ episode }} 集</option>
            </select>
            <button class="secondary-btn" @click="addEpisode" :disabled="!currentProjectId">+ 新增</button>
          </div>

          <select v-model="videoProvider" :disabled="!currentProjectId" class="toolbar-field">
            <option value="openai">视频接口: OpenAI兼容</option>
            <option value="jimeng">视频接口: 即梦API</option>
            <option value="grsai">视频接口: GRSAI</option>
          </select>

          <button class="secondary-btn" data-tour="btn-save-project" @click="saveCurrentProject" :disabled="!currentProjectId || saving">
            {{ saving ? '保存中...' : '保存项目' }}
          </button>
          <button data-tour="btn-create-project" @click="openCreateModal">创建项目</button>
          <button class="secondary-btn" data-tour="btn-open-guide" @click="openOnboarding(true)">新手引导</button>
          <div class="user-chip">{{ currentUser || '当前工作台' }}</div>
          <button class="secondary-btn" @click="logout">退出登录</button>
        </div>
      </header>

      <main class="stage-content">
        <RouterView v-slot="{ Component }">
          <component :is="Component" v-bind="activeViewProps" v-on="activeViewListeners" />
        </RouterView>
      </main>
    </section>

    <div v-if="showCreateModal" class="modal-mask" @click.self="closeCreateModal">
      <div class="modal-card">
        <h3>创建新项目</h3>
        <div class="form-group">
          <label>项目名称</label>
          <input v-model="projectNameInput" type="text" placeholder="例如：仙侠短剧 S1" />
        </div>
        <div class="form-group">
          <label>剧本名称</label>
          <input v-model="projectScriptTitleInput" type="text" placeholder="例如：剑心追月" />
        </div>
        <div class="form-group">
          <label>起始集数</label>
          <select v-model.number="projectEpisodeInput">
            <option v-for="choice in createEpisodeChoices" :key="`create-ep-${choice}`" :value="choice">第 {{ choice }} 集</option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="createProject" :disabled="creating">{{ creating ? '创建中...' : '创建项目' }}</button>
          <button class="secondary-btn" @click="closeCreateModal" :disabled="creating">取消</button>
        </div>
      </div>
    </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios';
import introJs from 'intro.js';
import 'intro.js/minified/introjs.min.css';
import LoginPage from './components/LoginPage.vue';

const EMPTY_SCRIPT = { input: '', duration: '3min', result: null };
const ONBOARDING_DONE_KEY = 'cinegen_onboarding_done_v1';

export default {
  name: 'App',
  components: {
    LoginPage
  },
  data() {
    return {
      phases: [
        { title: '剧本与分镜', routeName: 'script-storyboard' },
        { title: '资产与选角', routeName: 'assets-casting' },
        { title: '导演工作台', routeName: 'director-workbench' },
        { title: '成片与导出', routeName: 'export-stage' },
        { title: '模型配置', routeName: 'llm-config' }
      ],
      projects: [],
      currentProjectId: '',
      showCreateModal: false,
      projectNameInput: '',
      projectScriptTitleInput: '',
      projectEpisodeInput: 1,
      currentProjectName: '',
      currentScriptTitle: '',
      currentEpisodeNo: 1,
      videoProvider: 'openai',
      assets: [],
      shots: [],
      lastScript: { ...EMPTY_SCRIPT },
      scriptHistory: [],
      generatedData: [],
      episodeScripts: {},
      episodeShots: {},
      creating: false,
      saving: false,
      saveQueued: false,
      autoSaveTimer: null,
      authReady: false,
      isAuthenticated: false,
      authToken: '',
      currentUser: '',
      authInterceptorId: null,
      authExpiredNotified: false,
      introInstance: null,
      workingStateRevision: 0
    };
  },
  computed: {
    createEpisodeChoices() {
      return Array.from({ length: 24 }, (_, i) => i + 1);
    },
    episodeOptions() {
      const set = new Set();
      Object.keys(this.episodeScripts || {}).forEach((key) => {
        set.add(this.normalizeEpisodeNo(key));
      });
      Object.keys(this.episodeShots || {}).forEach((key) => {
        set.add(this.normalizeEpisodeNo(key));
      });
      set.add(this.normalizeEpisodeNo(this.currentEpisodeNo));
      if (!set.size) {
        set.add(1);
      }
      return [...set].sort((a, b) => a - b);
    },
    currentEpisodeKey() {
      return String(this.normalizeEpisodeNo(this.currentEpisodeNo));
    },
    activePhaseIndex() {
      const routeName = String(this.$route?.name || '');
      const index = this.phases.findIndex((phase) => phase.routeName === routeName);
      return index >= 0 ? index : 0;
    },
    activePhaseTitle() {
      return this.phases[this.activePhaseIndex]?.title || this.phases[0]?.title || '';
    },
    storyboardScenes() {
      const scenes = this.lastScript?.result?.scenes;
      return Array.isArray(scenes) ? scenes : [];
    },
    activeViewProps() {
      const routeName = String(this.$route?.name || '');
      if (routeName === 'script-storyboard') {
        return {
          currentEpisodeNo: this.currentEpisodeNo,
          initialScript: this.lastScript.input,
          initialDuration: this.lastScript.duration,
          initialResult: this.lastScript.result,
          history: this.scriptHistory,
          workflowStage: routeName
        };
      }
      if (routeName === 'assets-casting') {
        return {
          assets: this.assets,
          storyboardScenes: this.storyboardScenes,
          storyPackage: this.lastScript?.result?.story_package || null,
          scriptInput: this.lastScript?.input || '',
          scriptDuration: this.lastScript?.duration || '3min',
          workflowStage: routeName
        };
      }
      if (routeName === 'director-workbench') {
        return {
          assets: this.assets,
          shots: this.shots,
          storyboardScenes: this.storyboardScenes,
          videoProvider: this.videoProvider,
          currentEpisodeNo: this.currentEpisodeNo,
          workflowStage: routeName
        };
      }
      if (routeName === 'export-stage') {
        return {
          shots: this.shots,
          assets: this.assets,
          currentEpisodeNo: this.currentEpisodeNo,
          workflowStage: routeName
        };
      }
      return {};
    },
    activeViewListeners() {
      const routeName = String(this.$route?.name || '');
      if (routeName === 'script-storyboard') {
        return {
          'script-generated': this.onScriptGenerated,
          'script-updated': this.onScriptUpdated,
          'history-selected': this.onHistorySelected,
          'load-scenes-as-shots': this.onLoadScenesAsShots
        };
      }
      if (routeName === 'assets-casting') {
        return {
          'asset-added': this.onAssetAdded,
          'asset-deleted': this.onAssetDeleted,
          'script-updated': this.onScriptUpdated
        };
      }
      if (routeName === 'director-workbench') {
        return {
          'shots-updated': this.onShotsUpdated,
          'generated-event': this.onGeneratedEvent
        };
      }
      if (routeName === 'export-stage') {
        return {
          'shots-updated': this.onShotsUpdated
        };
      }
      return {};
    }
  },
  watch: {
    currentProjectName() {
      this.autoSave();
    },
    currentScriptTitle() {
      this.autoSave();
    },
    currentEpisodeNo() {
      this.ensureEpisodeState(this.currentEpisodeNo);
      this.syncWorkingStateFromEpisode();
      this.autoSave();
    },
    videoProvider() {
      this.autoSave();
    }
  },
  mounted() {
    this.setupAuthInterceptor();
    this.initializeAuth();
  },
  beforeUnmount() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer);
      this.autoSaveTimer = null;
    }
    if (this.introInstance) {
      this.introInstance.exit();
      this.introInstance = null;
    }
    if (this.authInterceptorId !== null) {
      axios.interceptors.response.eject(this.authInterceptorId);
      this.authInterceptorId = null;
    }
  },
  methods: {
    goToPhase(index) {
      void this.navigateToPhase(index);
    },
    async navigateToPhase(index) {
      const phase = this.phases[index];
      if (!phase?.routeName) return;
      if (this.$route?.name === phase.routeName) return;
      try {
        await this.$router.push({ name: phase.routeName });
      } catch (error) {
        // Ignore navigation duplicate errors.
      }
    },
    maybeShowOnboarding() {
      const alreadyDone = localStorage.getItem(ONBOARDING_DONE_KEY) === '1';
      if (!alreadyDone) {
        this.openOnboarding(true);
      }
    },
    async openOnboarding(reset = false) {
      if (this.introInstance) {
        this.introInstance.exit();
        this.introInstance = null;
      }
      if (reset) {
        await this.navigateToPhase(0);
      }
      this.$nextTick(() => {
        setTimeout(() => this.startIntroFlow(), 80);
      });
    },
    startIntroFlow() {
      const segments = [
        {
          phase: 0,
          steps: [
            { selector: '[data-tour="btn-create-project"]', intro: '先创建项目，后续分镜、资产和镜头都会保存到这个项目里。' },
            { selector: '[data-tour="btn-save-project"]', intro: '关键改动后点击保存，避免意外刷新导致内容丢失。' },
            { selector: '[data-tour="phase-nav-0"]', intro: '第 1 阶段：剧本拆解为分镜。' },
            { selector: '[data-tour="btn-parse-script"]', intro: '输入剧本后点击这里生成分镜脚本。' },
            { selector: '[data-tour="btn-load-all-scenes"]', intro: '分镜确认后，一键载入导演工作台生成镜头。' }
          ]
        },
        {
          phase: 2,
          steps: [
            { selector: '[data-tour="phase-nav-2"]', intro: '第 3 阶段：导演工作台。' },
            { selector: '[data-tour="btn-generate-all-frames"]', intro: '先批量生成前后关键帧。' },
            { selector: '[data-tour="btn-generate-all-videos"]', intro: '再一键提交全部镜头视频任务。' }
          ]
        },
        {
          phase: 3,
          steps: [
            { selector: '[data-tour="phase-nav-3"]', intro: '第 4 阶段：成片与导出。' },
            { selector: '[data-tour="btn-export-video"]', intro: '最后导出成片视频 MP4。' },
            { selector: '[data-tour="btn-open-guide"]', intro: '后续可随时点击“新手引导”再次查看。' }
          ]
        }
      ];

      void this.startIntroSegment(segments, 0);
    },
    async startIntroSegment(segments, segmentIndex) {
      if (!Array.isArray(segments) || segmentIndex >= segments.length) {
        this.finishOnboarding(true);
        return;
      }

      const segment = segments[segmentIndex];
      const targetPhase = Number(segment?.phase);
      if (Number.isFinite(targetPhase) && targetPhase >= 0 && targetPhase < this.phases.length) {
        await this.navigateToPhase(targetPhase);
      }

      this.$nextTick(() => {
        const steps = [];
        (segment?.steps || []).forEach((step) => {
          const element = document.querySelector(step.selector);
          if (!element) return;
          steps.push({ element, intro: step.intro });
        });

        if (!steps.length) {
          void this.startIntroSegment(segments, segmentIndex + 1);
          return;
        }

        const instance = introJs();
        instance.setOptions({
          steps,
          nextLabel: '下一步',
          prevLabel: '上一步',
          doneLabel: segmentIndex >= segments.length - 1 ? '完成' : '继续',
          skipLabel: '跳过',
          showBullets: true,
          showProgress: true,
          overlayOpacity: 0.62,
          scrollToElement: true,
          tooltipClass: 'zz-intro-tooltip',
          highlightClass: 'zz-intro-highlight'
        });
        instance.oncomplete(() => {
          this.introInstance = null;
          void this.startIntroSegment(segments, segmentIndex + 1);
        });
        instance.onexit(() => this.finishOnboarding(true));
        this.introInstance = instance;
        instance.start();
      });
    },
    finishOnboarding(markDone = true) {
      if (markDone) {
        localStorage.setItem(ONBOARDING_DONE_KEY, '1');
      }
      this.introInstance = null;
    },
    setupAuthInterceptor() {
      this.authInterceptorId = axios.interceptors.response.use(
        (response) => response,
        (error) => {
          const status = Number(error?.response?.status || 0);
          const url = String(error?.config?.url || '');
          const code = String(error?.response?.data?.code || '').trim().toUpperCase();
          const message = String(
            error?.response?.data?.error ||
            error?.response?.data?.message ||
            ''
          ).trim().toLowerCase();
          const isAuthEndpoint =
            url.includes('/api/auth/login') ||
            url.includes('/api/auth/register') ||
            url.includes('/api/auth/status') ||
            url.includes('/api/auth/logout');
          const isAuthSessionError =
            code === 'AUTH_REQUIRED' ||
            message === 'unauthorized' ||
            message === 'invalid token' ||
            message === 'token expired' ||
            message === 'token invalid';
          if (status === 401 && this.isAuthenticated && !isAuthEndpoint && isAuthSessionError) {
            this.handleAuthExpired();
          }
          return Promise.reject(error);
        }
      );
    },
    applyAuthTokenHeader(token) {
      const normalized = String(token || '').trim();
      if (normalized) {
        axios.defaults.headers.common.Authorization = `Bearer ${normalized}`;
      } else {
        delete axios.defaults.headers.common.Authorization;
      }
    },
    getProjectStorageKey(username = this.currentUser) {
      const normalized = String(username || '').trim() || 'guest';
      return `cinegen_current_project:${normalized}`;
    },
    getStoredCurrentProjectId(username = this.currentUser) {
      return String(localStorage.getItem(this.getProjectStorageKey(username)) || '').trim();
    },
    setStoredCurrentProjectId(projectId, username = this.currentUser) {
      const normalizedId = String(projectId || '').trim();
      const key = this.getProjectStorageKey(username);
      if (!normalizedId) {
        localStorage.removeItem(key);
        return '';
      }
      localStorage.setItem(key, normalizedId);
      return normalizedId;
    },
    clearStoredCurrentProjectId(username = this.currentUser) {
      localStorage.removeItem(this.getProjectStorageKey(username));
    },
    clearAuthState() {
      if (this.introInstance) {
        this.introInstance.exit();
        this.introInstance = null;
      }
      this.authToken = '';
      this.currentUser = '';
      this.isAuthenticated = false;
      this.authExpiredNotified = false;
      this.authReady = true;
      this.applyAuthTokenHeader('');
      localStorage.removeItem('cinegen_auth_token');
      localStorage.removeItem('cinegen_auth_user');
    },
    async initializeAuth() {
      const token = String(localStorage.getItem('cinegen_auth_token') || '').trim();
      const cachedUser = String(localStorage.getItem('cinegen_auth_user') || '').trim();
      if (!token) {
        this.authReady = true;
        return;
      }

      this.applyAuthTokenHeader(token);
      try {
        const response = await axios.get('/api/auth/status');
        const account = String(response.data?.email || response.data?.username || cachedUser || '').trim();
        this.authToken = token;
        this.currentUser = account;
        this.isAuthenticated = true;
        this.authExpiredNotified = false;
        this.authReady = true;
        localStorage.setItem('cinegen_auth_user', account);
        await this.loadProjects();
        this.maybeShowOnboarding();
      } catch (error) {
        this.clearAuthState();
      }
    },
    async handleLoginSuccess(payload) {
      const token = String(payload?.token || '').trim();
      const account = String(payload?.email || payload?.username || '').trim();
      if (!token) {
        alert('登录失败：未收到有效 token');
        return;
      }
      this.authToken = token;
      this.currentUser = account;
      this.isAuthenticated = true;
      this.authExpiredNotified = false;
      this.authReady = true;
      localStorage.setItem('cinegen_auth_token', token);
      localStorage.setItem('cinegen_auth_user', account);
      this.applyAuthTokenHeader(token);
      await this.loadProjects();
      this.maybeShowOnboarding();
    },
    async logout(options = {}) {
      const silent = Boolean(options.silent);
      const token = String(this.authToken || '').trim();
      if (token) {
        try {
          await axios.post('/api/auth/logout');
        } catch (error) {
          // Ignore logout failure and clear local auth state anyway.
        }
      }
      this.clearAuthState();
      this.currentProjectId = '';
      this.projects = [];
      this.resetWorkingState();
      if (silent) return;
    },
    handleAuthExpired() {
      if (this.authExpiredNotified) {
        return;
      }
      this.authExpiredNotified = true;
      this.logout({ silent: true });
      alert('登录已过期，请重新登录');
    },
    openCreateModal() {
      this.showCreateModal = true;
      if (!this.projectNameInput.trim()) {
        this.projectNameInput = `项目 ${this.projects.length + 1}`;
      }
      this.projectEpisodeInput = 1;
    },
    closeCreateModal() {
      this.showCreateModal = false;
    },
    normalizeEpisodeNo(value) {
      const parsed = Number(value);
      return parsed > 0 ? parsed : 1;
    },
    normalizeVideoProvider(value) {
      const normalized = String(value || '').trim().toLowerCase();
      if (normalized === 'jimeng') return 'jimeng';
      if (normalized === 'grsai') return 'grsai';
      return 'openai';
    },
    hashText(text) {
      const source = String(text || '');
      let hash = 0;
      for (let i = 0; i < source.length; i += 1) {
        hash = ((hash << 5) - hash + source.charCodeAt(i)) | 0;
      }
      return Math.abs(hash).toString(36);
    },
    classifyAssetKind(asset) {
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
        /场景|鍦烘櫙|环境|鍦烘櫙/.test(promptText)
      ) {
        return 'scene';
      }
      return '';
    },
    normalizeAssetEntry(asset, index = 0) {
      const safe = asset && typeof asset === 'object' ? { ...asset } : {};
      const assetKind = this.classifyAssetKind(safe);
      if (assetKind) {
        safe.asset_kind = assetKind;
      }
      const explicitId = String(safe.id || safe.asset_id || '').trim();
      if (explicitId) {
        safe.id = explicitId;
        return safe;
      }
      const seed = [
        String(safe.type || '').trim(),
        String(safe.name || '').trim(),
        String(safe.image_url || '').trim(),
        String(safe.prompt || '').trim(),
        String(index)
      ].join('|');
      safe.id = `asset_${this.hashText(seed)}`;
      return safe;
    },
    normalizeAssetList(list) {
      if (!Array.isArray(list)) return [];
      return list.map((item, index) => this.normalizeAssetEntry(item, index));
    },
    pruneRemovedAssetBindings(removedAsset) {
      const removedId = String(removedAsset?.id || '').trim();
      const removedName = String(removedAsset?.name || '').trim();
      const removedKind = this.classifyAssetKind(removedAsset);
      if (!removedId && !removedName) return;

      const pruneShotList = (list) => {
        if (!Array.isArray(list)) return [];
        return list.map((shot) => {
          const safeShot = shot && typeof shot === 'object' ? { ...shot } : {};
          const ids = Array.isArray(safeShot.boundCharacterAssetIds)
            ? safeShot.boundCharacterAssetIds.map((item) => String(item || '').trim()).filter(Boolean)
            : [];
          const names = Array.isArray(safeShot.boundCharacterNames)
            ? safeShot.boundCharacterNames.map((item) => String(item || '').trim()).filter(Boolean)
            : [];
          const sceneIds = Array.isArray(safeShot.boundSceneAssetIds)
            ? safeShot.boundSceneAssetIds.map((item) => String(item || '').trim()).filter(Boolean)
            : [];
          const sceneNames = Array.isArray(safeShot.boundSceneNames)
            ? safeShot.boundSceneNames.map((item) => String(item || '').trim()).filter(Boolean)
            : [];

          if (!removedKind || removedKind === 'character') {
            safeShot.boundCharacterAssetIds = ids.filter((id) => id !== removedId);
            safeShot.boundCharacterNames = names.filter((name) => name !== removedName);
          }
          if (!removedKind || removedKind === 'scene') {
            safeShot.boundSceneAssetIds = sceneIds.filter((id) => id !== removedId);
            safeShot.boundSceneNames = sceneNames.filter((name) => name !== removedName);
          }
          return safeShot;
        });
      };

      this.shots = pruneShotList(this.shots);
      Object.keys(this.episodeShots || {}).forEach((key) => {
        this.episodeShots[key] = pruneShotList(this.episodeShots[key]);
      });
    },
    ensureEpisodeState(episodeNo) {
      const key = String(this.normalizeEpisodeNo(episodeNo));
      if (!this.episodeScripts[key] || typeof this.episodeScripts[key] !== 'object') {
        this.episodeScripts[key] = { script: { ...EMPTY_SCRIPT }, history: [] };
      }
      if (!Array.isArray(this.episodeScripts[key].history)) {
        this.episodeScripts[key].history = [];
      }
      if (!this.episodeScripts[key].script || typeof this.episodeScripts[key].script !== 'object') {
        this.episodeScripts[key].script = { ...EMPTY_SCRIPT };
      }
      if (!Array.isArray(this.episodeShots[key])) {
        this.episodeShots[key] = [];
      }
      return key;
    },
    addEpisode() {
      if (!this.currentProjectId) return;
      const current = this.episodeOptions;
      const next = (current[current.length - 1] || 1) + 1;
      this.ensureEpisodeState(next);
      this.currentEpisodeNo = next;
      this.pushGeneratedEvent('episode_created', { episode: next });
      this.autoSave();
    },
    syncWorkingStateFromEpisode() {
      const key = this.ensureEpisodeState(this.currentEpisodeNo);
      const episodeState = this.episodeScripts[key];
      this.lastScript = {
        input: String(episodeState.script?.input || ''),
        duration: String(episodeState.script?.duration || '3min'),
        result: episodeState.script?.result || null
      };
      this.scriptHistory = Array.isArray(episodeState.history) ? [...episodeState.history] : [];
      this.shots = Array.isArray(this.episodeShots[key]) ? [...this.episodeShots[key]] : [];
    },
    saveWorkingStateToEpisode() {
      const key = this.ensureEpisodeState(this.currentEpisodeNo);
      this.episodeScripts[key] = {
        script: { ...this.lastScript },
        history: Array.isArray(this.scriptHistory) ? [...this.scriptHistory] : []
      };
      this.episodeShots[key] = Array.isArray(this.shots) ? [...this.shots] : [];
    },
    resetWorkingState() {
      this.assets = [];
      this.shots = [];
      this.scriptHistory = [];
      this.generatedData = [];
      this.lastScript = { ...EMPTY_SCRIPT };
      this.videoProvider = 'openai';
      this.episodeScripts = { '1': { script: { ...EMPTY_SCRIPT }, history: [] } };
      this.episodeShots = { '1': [] };
      this.currentProjectName = '';
      this.currentScriptTitle = '';
      this.currentEpisodeNo = 1;
      this.workingStateRevision = 0;
    },
    pushGeneratedEvent(type, payload = {}) {
      const event = {
        id: `g_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
        type,
        createdAt: new Date().toISOString(),
        payload
      };
      this.generatedData = [event, ...this.generatedData].slice(0, 300);
    },
    applyProject(project) {
      this.currentProjectName = project.name || '';
      this.currentScriptTitle = project.script_title || '';
      this.currentEpisodeNo = this.normalizeEpisodeNo(project.episode_no);
      this.videoProvider = this.normalizeVideoProvider(project.video_provider);
      this.assets = this.normalizeAssetList(project.assets);
      this.generatedData = Array.isArray(project.generated_data) ? project.generated_data : [];

      const legacyScript = project.script && typeof project.script === 'object' ? project.script : { ...EMPTY_SCRIPT };
      const legacyHistory = Array.isArray(project.history) ? project.history : [];
      const legacyShots = Array.isArray(project.shots) ? project.shots : [];

      const incomingEpisodeScripts = project.episode_scripts && typeof project.episode_scripts === 'object'
        ? project.episode_scripts
        : {};
      const incomingEpisodeShots = project.episode_shots && typeof project.episode_shots === 'object'
        ? project.episode_shots
        : {};

      this.episodeScripts = {};
      Object.keys(incomingEpisodeScripts).forEach((key) => {
        const value = incomingEpisodeScripts[key] || {};
        this.episodeScripts[key] = {
          script: value.script && typeof value.script === 'object' ? value.script : { ...EMPTY_SCRIPT },
          history: Array.isArray(value.history) ? value.history : []
        };
      });

      this.episodeShots = {};
      Object.keys(incomingEpisodeShots).forEach((key) => {
        this.episodeShots[key] = Array.isArray(incomingEpisodeShots[key]) ? incomingEpisodeShots[key] : [];
      });

      if (!Object.keys(this.episodeScripts).length) {
        const fallbackKey = String(this.currentEpisodeNo);
        this.episodeScripts[fallbackKey] = {
          script: {
            input: String(legacyScript.input || ''),
            duration: String(legacyScript.duration || '3min'),
            result: legacyScript.result || null
          },
          history: legacyHistory
        };
      }

      if (!Object.keys(this.episodeShots).length) {
        this.episodeShots[String(this.currentEpisodeNo)] = legacyShots;
      }

      this.syncWorkingStateFromEpisode();
      this.workingStateRevision = 0;
    },
    buildProjectPayload() {
      this.saveWorkingStateToEpisode();
      const currentKey = this.currentEpisodeKey;
      const currentEpisodeScriptState = this.episodeScripts[currentKey] || { script: { ...EMPTY_SCRIPT }, history: [] };

      return {
        name: this.currentProjectName.trim() || '未命名项目',
        script_title: this.currentScriptTitle.trim(),
        episode_no: this.normalizeEpisodeNo(this.currentEpisodeNo),
        video_provider: this.normalizeVideoProvider(this.videoProvider),
        assets: this.assets,
        shots: this.episodeShots[currentKey] || [],
        history: currentEpisodeScriptState.history || [],
        generated_data: this.generatedData,
        script: currentEpisodeScriptState.script || { ...EMPTY_SCRIPT },
        episode_scripts: this.episodeScripts,
        episode_shots: this.episodeShots
      };
    },
    async loadProjects() {
      if (!this.isAuthenticated) return;
      try {
        const response = await axios.get('/api/projects');
        this.projects = Array.isArray(response.data) ? response.data : [];

        const cachedId = this.getStoredCurrentProjectId();
        const defaultId = this.projects[0]?.id || '';
        const targetId = this.projects.some((p) => p.id === cachedId) ? cachedId : defaultId;

        if (targetId) {
          this.currentProjectId = targetId;
          await this.selectProject();
        } else {
          this.resetWorkingState();
        }
      } catch (error) {
        console.error('加载项目失败:', error);
      }
    },
    async createProject() {
      this.creating = true;
      try {
        const payload = {
          name: this.projectNameInput.trim() || `项目 ${this.projects.length + 1}`,
          script_title: this.projectScriptTitleInput.trim(),
          episode_no: this.normalizeEpisodeNo(this.projectEpisodeInput)
        };
        const response = await axios.post('/api/projects', payload);
        const created = response.data;
        this.projects = [created, ...this.projects];
        this.currentProjectId = created.id;
        this.setStoredCurrentProjectId(created.id);
        this.applyProject(created);
        this.projectNameInput = '';
        this.projectScriptTitleInput = '';
        this.projectEpisodeInput = 1;
        this.showCreateModal = false;
      } catch (error) {
        console.error('创建项目失败:', error);
        alert('创建项目失败，请重试');
      } finally {
        this.creating = false;
      }
    },
    async selectProject() {
      if (!this.currentProjectId) {
        this.clearStoredCurrentProjectId();
        this.resetWorkingState();
        return;
      }

      try {
        const response = await axios.get(`/api/projects/${this.currentProjectId}`);
        this.applyProject(response.data);
        this.setStoredCurrentProjectId(this.currentProjectId);
      } catch (error) {
        console.error('加载项目详情失败:', error);
        alert('加载项目失败，请刷新重试');
      }
    },
    async saveCurrentProject() {
      if (!this.currentProjectId) return;
      if (this.saving) {
        this.saveQueued = true;
        return;
      }
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer);
        this.autoSaveTimer = null;
      }
      this.saving = true;
      this.saveQueued = false;
      const requestRevision = this.workingStateRevision;
      try {
        const response = await axios.put(`/api/projects/${this.currentProjectId}`, this.buildProjectPayload());
        const updated = response.data;
        if (requestRevision !== this.workingStateRevision) {
          return;
        }
        const index = this.projects.findIndex((p) => p.id === updated.id);
        if (index !== -1) {
          this.projects.splice(index, 1, {
            ...this.projects[index],
            ...updated,
            assets: this.assets,
            shots: this.shots,
            episode_scripts: this.episodeScripts,
            episode_shots: this.episodeShots,
            script: this.lastScript,
            history: this.scriptHistory,
            generated_data: this.generatedData
          });
        } else {
          this.projects.unshift({
            ...updated,
            assets: this.assets,
            shots: this.shots,
            episode_scripts: this.episodeScripts,
            episode_shots: this.episodeShots,
            script: this.lastScript,
            history: this.scriptHistory,
            generated_data: this.generatedData
          });
        }
      } catch (error) {
        console.error('保存项目失败:', error);
      } finally {
        this.saving = false;
        if (this.saveQueued) {
          this.saveQueued = false;
          void this.saveCurrentProject();
        }
      }
    },
    autoSave() {
      if (!this.currentProjectId) return;
      this.workingStateRevision += 1;
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer);
      }
      this.autoSaveTimer = setTimeout(() => {
        this.autoSaveTimer = null;
        if (this.saving) {
          this.saveQueued = true;
          return;
        }
        void this.saveCurrentProject();
      }, 600);
    },
    onAssetAdded(asset) {
      this.assets.push(this.normalizeAssetEntry(asset, this.assets.length));
      this.pushGeneratedEvent('asset_generated', {
        name: asset?.name || '',
        asset_type: asset?.type || '',
        image_url: asset?.image_url || ''
      });
      this.autoSave();
    },
    onAssetDeleted(index) {
      if (index >= 0 && index < this.assets.length) {
        const target = this.assets[index];
        if (!window.confirm(`确认删除资产「${target?.name || `#${index + 1}`}」吗？`)) {
          return;
        }
        this.assets.splice(index, 1);
        this.pruneRemovedAssetBindings(target);
        this.saveWorkingStateToEpisode();
        this.autoSave();
      }
    },
    onShotsUpdated(newShots) {
      this.shots = Array.isArray(newShots) ? newShots : [];
      this.saveWorkingStateToEpisode();
      this.autoSave();
    },
    onLoadScenesAsShots(newShots) {
      this.shots = Array.isArray(newShots) ? newShots : [];
      this.saveWorkingStateToEpisode();
      void this.navigateToPhase(2);
      this.pushGeneratedEvent('storyboard_loaded_to_shots', {
        episode: this.currentEpisodeNo,
        shots_count: this.shots.length
      });
      this.autoSave();
    },
    onScriptGenerated(payload) {
      const entry = {
        id: `h_${Date.now()}`,
        title: `第${this.currentEpisodeNo}集 - ${(payload.script || '').slice(0, 24) || '未命名剧本'}`,
        createdAt: new Date().toLocaleString(),
        script: payload.script,
        duration: payload.duration,
        result: payload.result
      };

      this.scriptHistory = [entry, ...this.scriptHistory].slice(0, 30);
      this.lastScript = {
        input: payload.script,
        duration: payload.duration,
        result: payload.result
      };
      this.pushGeneratedEvent('script_generated', {
        episode: this.currentEpisodeNo,
        duration: payload.duration,
        scenes_count: Array.isArray(payload?.result?.scenes) ? payload.result.scenes.length : 0
      });
      this.saveWorkingStateToEpisode();
      this.autoSave();
    },
    onScriptUpdated(payload) {
      const input = String(payload?.script || '').trim();
      const duration = String(payload?.duration || '').trim();
      this.lastScript = {
        ...this.lastScript,
        input: input || this.lastScript.input,
        duration: duration || this.lastScript.duration,
        result: payload.result
      };
      this.saveWorkingStateToEpisode();
      this.autoSave();
    },
    onHistorySelected(item) {
      this.lastScript = {
        input: item.script || '',
        duration: item.duration || '3min',
        result: item.result || null
      };
      this.saveWorkingStateToEpisode();
      this.autoSave();
    },
    onGeneratedEvent(event) {
      this.pushGeneratedEvent(event?.type || 'unknown', event?.payload || {});
      this.autoSave();
    }
  }
};
</script>

<style scoped>
.app-root {
  min-height: 100vh;
}

.auth-loading-screen {
  min-height: 100vh;
  display: grid;
  place-items: center;
  color: #d8f5ef;
  background: radial-gradient(circle at 20% 10%, #17414a, #0b1f25 50%, #060f14);
}

.studio-shell {
  min-height: 100vh;
  width: 100%;
  display: grid;
  grid-template-columns: 248px 1fr;
  gap: 14px;
  padding: 14px;
  background: radial-gradient(circle at 15% 0%, #12343a, #0a1f25 48%, #061015);
}

.studio-sidebar {
  background: linear-gradient(180deg, #10262b, #0c1d22);
  border: 1px solid #2a454b;
  border-radius: 14px;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  color: #e8f7f1;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1a3a3f, #245058);
  border: 1px solid #356069;
  display: grid;
  place-items: center;
  color: #f0fdfa;
  font-size: 18px;
}

.brand-block h1 {
  margin: 0;
  letter-spacing: 0.8px;
  font-size: 14px;
}

.brand-block p {
  margin: 0;
  color: #8fb1ac;
  font-size: 10px;
  letter-spacing: 1px;
}

.back-link {
  width: 100%;
  justify-content: flex-start;
  background: transparent;
  color: #9dc2bb;
  border: 1px solid #2a454b;
  margin-bottom: 14px;
}

.project-glance {
  border: 1px solid #2a454b;
  border-radius: 10px;
  padding: 10px;
  background: #0d1b20;
  margin-bottom: 14px;
}

.project-glance-label {
  font-size: 11px;
  color: #6d918a;
}

.project-glance-name {
  margin-top: 6px;
  font-size: 16px;
  color: #f2fffb;
  font-weight: 700;
  word-break: break-all;
}

.project-glance-meta {
  margin-top: 6px;
  font-size: 12px;
  color: #34d399;
}

.phase-nav {
  display: grid;
  gap: 8px;
  margin-top: 4px;
}

.phase-item {
  width: 100%;
  display: grid;
  grid-template-columns: 42px 1fr auto;
  gap: 8px;
  align-items: center;
  background: #0d1b20;
  border: 1px solid #2a454b;
  color: #cfe7e2;
  padding: 10px;
  border-radius: 10px;
  text-align: left;
}

.phase-item .phase-index {
  font-size: 11px;
  color: #93b8b1;
}

.phase-item .phase-title {
  font-size: 13px;
}

.phase-item .phase-tag {
  font-size: 10px;
  color: #6d918a;
}

.phase-item.active {
  border-color: #2dd4bf;
  background: linear-gradient(90deg, rgba(45, 212, 191, 0.25), rgba(18, 52, 58, 0.72));
  box-shadow: 0 0 0 1px rgba(45, 212, 191, 0.35) inset;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #2a454b;
  font-size: 12px;
  color: #6d918a;
}

.studio-stage {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stage-topbar {
  border-radius: 14px;
  border: 1px solid #2a454b;
  background: linear-gradient(180deg, #10262b, #0e2024);
  padding: 12px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.stage-title-block {
  min-width: 220px;
}

.stage-title-block h2 {
  margin: 0;
  color: #f2fffb;
  font-size: 20px;
}

.stage-title-block span {
  color: #8fb1ac;
  font-size: 12px;
}

.stage-toolbar {
  display: grid;
  grid-template-columns: minmax(180px, 260px) minmax(120px, 180px) minmax(120px, 180px) minmax(160px, 220px) auto auto auto auto auto;
  gap: 8px;
  width: 100%;
  align-items: center;
}

.toolbar-field {
  height: 38px;
  border-radius: 8px;
  border: 1px solid #356069;
  background: #12252b;
  color: #e8f7f1;
  padding: 0 10px;
}

.episode-control {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px;
}

.stage-content {
  min-height: calc(100vh - 130px);
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(3, 16, 18, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
  padding: 16px;
}

.modal-card {
  width: min(520px, 100%);
  background: #12252b;
  border-radius: 14px;
  border: 1px solid #356069;
  padding: 18px;
  color: #e8f7f1;
}

.modal-card h3 {
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.secondary-btn {
  background: #1b3740;
  color: #dff7f1;
}

.user-chip {
  height: 38px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #356069;
  background: #12252b;
  color: #ccefe8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

:deep(.introjs-tooltip) {
  background: #113038;
  color: #e8fbf8;
  border: 1px solid #3f6a72;
  border-radius: 10px;
}

:deep(.introjs-button) {
  background: #1b3e46;
  border: 1px solid #3f6a72;
  color: #e8fbf8;
  text-shadow: none;
  box-shadow: none;
}

:deep(.introjs-overlay) {
  background: radial-gradient(circle at 30% 10%, rgba(23, 78, 89, 0.56), rgba(6, 15, 20, 0.86)) !important;
  backdrop-filter: blur(1.5px);
}

:deep(.zz-intro-highlight) {
  border-radius: 10px !important;
  box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.62), 0 0 28px rgba(20, 184, 166, 0.38) !important;
}

:deep(.introjs-tooltip.zz-intro-tooltip) {
  min-width: 290px;
  max-width: 420px;
  padding: 14px 14px 12px;
  border-radius: 12px;
  border: 1px solid #3f6a72;
  background: linear-gradient(180deg, #153a43, #112d34);
  box-shadow: 0 18px 48px rgba(5, 16, 20, 0.45);
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-tooltiptext) {
  color: #d9f6f1;
  line-height: 1.65;
  font-size: 13px;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-progress) {
  margin-top: 8px;
  margin-bottom: 10px;
  background: #244c54;
  border-radius: 999px;
  overflow: hidden;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-progressbar) {
  background: linear-gradient(90deg, #14b8a6, #34d399);
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-bullets ul li a) {
  background: #355f67;
  width: 9px;
  height: 9px;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-bullets ul li a.active) {
  background: #34d399;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-tooltipbuttons) {
  border-top: 1px solid rgba(98, 146, 157, 0.42);
  padding-top: 10px;
  margin-top: 2px;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-button) {
  border-radius: 8px;
  font-size: 12px;
  padding: 6px 12px;
  border: 1px solid #3f6a72;
  background: #1b3e46;
  color: #e8fbf8;
  text-shadow: none;
  box-shadow: none;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-button:hover) {
  background: #22505b;
  border-color: #5d8f99;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-button:focus-visible) {
  outline: 2px solid rgba(52, 211, 153, 0.72);
  outline-offset: 1px;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-disabled) {
  opacity: 0.45;
  pointer-events: none;
}

:deep(.introjs-tooltip.zz-intro-tooltip .introjs-skipbutton) {
  color: #99c3bc;
}

:deep(.introjs-arrow.top),
:deep(.introjs-arrow.top-middle),
:deep(.introjs-arrow.top-right) {
  border-bottom-color: #153a43 !important;
}

:deep(.introjs-arrow.bottom),
:deep(.introjs-arrow.bottom-middle),
:deep(.introjs-arrow.bottom-right) {
  border-top-color: #112d34 !important;
}

:deep(.introjs-arrow.left),
:deep(.introjs-arrow.left-middle) {
  border-right-color: #13343d !important;
}

:deep(.introjs-arrow.right),
:deep(.introjs-arrow.right-middle) {
  border-left-color: #13343d !important;
}

@media (max-width: 1380px) {
  .stage-toolbar {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 980px) {
  .studio-shell {
    grid-template-columns: 1fr;
  }

  .studio-sidebar {
    order: 2;
  }

  .stage-topbar {
    flex-direction: column;
    align-items: stretch;
  }

  .stage-toolbar,
  .episode-control {
    grid-template-columns: 1fr;
  }
}
</style>
