<template>
  <div class="phase">
    <h2>{{ phaseTitle }}</h2>
    <div class="episode-banner">当前导出：第 {{ currentEpisodeNo }} 集</div>
    <div class="workflow-brief">
      <strong>{{ workflowHeadline }}</strong>
      <p>{{ workflowDescription }}</p>
    </div>

    <div class="layout">
      <section class="panel shot-editor-panel">
        <div class="panel-header">
          <h3>{{ shotListTitle }}</h3>
          <div class="panel-actions">
            <button @click="addShot">新增镜头</button>
            <button class="secondary-btn" @click="toggleSelectAllForFinal" :disabled="!localShots.length">
              {{ allSelectedForFinal ? '取消全选' : '入片全选' }}
            </button>
            <button class="secondary-btn" @click="syncFinalEditTextFromShots">重建成片文案</button>
          </div>
        </div>

        <div v-if="!localShots.length" class="empty-state">暂无镜头，请先在导演工作台生成镜头。</div>

        <div v-else class="shot-table-wrap">
          <table class="shot-table">
            <thead>
              <tr>
                <th>#</th>
                <th>标题</th>
                <th>时长</th>
                <th>视频链接</th>
                <th>入片</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(shot, index) in localShots"
                :key="`export-shot-${index}`"
                :class="{ selected: selectedShotIndex === index }"
                @click="selectShot(index)"
              >
                <td>{{ index + 1 }}</td>
                <td>
                  <input v-model="shot.title" type="text" placeholder="镜头标题" @input="emitShotsUpdated" />
                </td>
                <td>
                  <input v-model="shot.duration" type="text" placeholder="5s" @input="emitShotsUpdated" />
                </td>
                <td>
                  <input v-model="shot.videoUrl" type="text" placeholder="https://..." @input="emitShotsUpdated" />
                </td>
                <td class="center-col">
                  <input type="checkbox" v-model="shot.includeInFinal" @change="emitShotsUpdated" />
                </td>
                <td>
                  <div class="row-actions">
                    <button class="mini" @click.stop="moveShot(index, -1)" :disabled="index === 0">上移</button>
                    <button class="mini" @click.stop="moveShot(index, 1)" :disabled="index === localShots.length - 1">下移</button>
                    <button class="mini danger" @click.stop="removeShot(index)">删除</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="summary-row">
          <span>入片镜头数：{{ activeShots.length }}</span>
          <span>预计成片时长：{{ estimatedDurationSec }} 秒</span>
        </div>
      </section>

      <section class="panel preview-panel">
        <h3>{{ previewTitle }}</h3>

        <div v-if="selectedShot" class="preview-card">
          <div class="form-group">
            <label>当前镜头备注（可用于剪辑说明）</label>
            <input v-model="selectedShot.notes" type="text" placeholder="例如：加快 1.2 倍，保留人声" @input="emitShotsUpdated" />
          </div>

          <div class="preview-box">
            <video
              v-if="selectedShot.videoUrl"
              ref="previewPlayer"
              controls
              playsinline
              :src="selectedShot.videoUrl"
              style="width: 100%;"
            ></video>
            <img v-else-if="selectedShot.startFrame?.image_url" :src="selectedShot.startFrame.image_url" alt="preview frame" />
            <div v-else class="empty-preview">当前镜头没有可预览视频</div>
          </div>

          <a
            v-if="selectedShot.videoUrl"
            :href="selectedShot.videoUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="video-link"
          >打开当前镜头视频链接</a>
        </div>

        <div class="form-group" style="margin-top: 14px;">
          <label>{{ finalEditLabel }}</label>
          <textarea
            v-model="finalEditText"
            rows="12"
            placeholder="可在这里直接编辑最终成片说明、镜头顺序、音效和字幕要求"
          ></textarea>
        </div>

        <div class="form-group" style="margin-top: 12px;">
          <label>旁白文案（可直接编辑）</label>
          <textarea
            v-model="narrationText"
            rows="8"
            placeholder="可点击“生成旁白文案”自动生成，也可手动修改"
          ></textarea>
          <div class="export-actions" style="margin-top: 8px;">
            <button class="secondary-btn" @click="generateNarration" :disabled="generatingNarration || !activeShots.length">
              {{ generatingNarration ? '正在生成旁白...' : '生成旁白文案' }}
            </button>
            <button class="secondary-btn" @click="applyNarrationToFinalEdit" :disabled="!narrationText.trim()">旁白写入成片文案</button>
          </div>
        </div>

        <div class="export-actions">
          <button data-tour="btn-export-video" @click="exportFinalVideo" :disabled="exportingVideo || !activeShots.length">
            {{ exportingVideo ? exportRunningLabel : exportPrimaryLabel }}
          </button>
          <button v-if="isOutputStage" @click="downloadFinalJson">{{ isCombinedStage ? '导出成片 JSON' : '导出漫剧 JSON' }}</button>
          <button v-if="isOutputStage" class="secondary-btn" @click="downloadFinalTxt">{{ isCombinedStage ? '导出成片文案 TXT' : '导出漫剧文案 TXT' }}</button>
        </div>

        <div v-if="exportingVideo || exportVideoProgress > 0" class="export-video-progress">
          <div class="progress-header">
            <span>{{ exportVideoStatus || '正在处理导出任务' }}</span>
            <span>{{ exportVideoProgress }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${exportVideoProgress}%` }"></div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Export',
  props: {
    shots: {
      type: Array,
      default: () => []
    },
    assets: {
      type: Array,
      default: () => []
    },
    currentEpisodeNo: {
      type: Number,
      default: 1
    },
    workflowStage: {
      type: String,
      default: 'export-stage'
    }
  },
  data() {
    return {
      localShots: [],
      selectedShotIndex: -1,
      finalEditText: '',
      narrationText: '',
      generatingNarration: false,
      exportingVideo: false,
      exportVideoProgress: 0,
      exportVideoStatus: ''
    };
  },
  computed: {
    isCombinedStage() {
      return this.workflowStage === 'export-stage';
    },
    isMontageStage() {
      return this.isCombinedStage || this.workflowStage === 'montage';
    },
    isOutputStage() {
      return this.isCombinedStage || this.workflowStage === 'output';
    },
    phaseTitle() {
      if (this.isCombinedStage) return 'Phase 04: 成片与导出';
      return this.workflowStage === 'output' ? 'Phase 08: 漫剧输出' : 'Phase 07: 镜头拼接';
    },
    workflowHeadline() {
      if (this.isCombinedStage) {
        return '当前阶段同时处理镜头拼接、成片文案编辑和最终导出。';
      }
      return this.workflowStage === 'output'
        ? '当前阶段整理最终漫剧输出稿，确认成片文案、导出格式和交付内容。'
        : '当前阶段只做镜头拼接，检查镜头顺序、入片范围和时长总量。';
    },
    workflowDescription() {
      if (this.isCombinedStage) {
        return '在这里决定哪些镜头入片、调整顺序、编辑剪辑说明，并直接导出最终 MP4、JSON 和 TXT。';
      }
      return this.workflowStage === 'output'
        ? '这里输出最终 MP4、JSON 和 TXT。建议先在上一阶段完成镜头拼接，再进入本阶段导出。'
        : '这里先决定哪些镜头入片、先后顺序如何排列，以及每个镜头的剪辑备注。';
    },
    shotListTitle() {
      if (this.isCombinedStage) return '成片镜头清单';
      return this.workflowStage === 'output' ? '漫剧成片清单' : '镜头拼接清单';
    },
    previewTitle() {
      if (this.isCombinedStage) return '成片预览与最终编辑';
      return this.workflowStage === 'output' ? '漫剧输出与最终编辑' : '拼接预览与剪辑说明';
    },
    finalEditLabel() {
      if (this.isCombinedStage) return '最终成片文案（可直接编辑）';
      return this.workflowStage === 'output' ? '漫剧输出文案（可直接编辑）' : '拼接说明（可直接编辑）';
    },
    exportPrimaryLabel() {
      if (this.isCombinedStage) return '导出成片视频 MP4';
      return this.workflowStage === 'output' ? '导出漫剧视频 MP4' : '导出拼接预览 MP4';
    },
    exportRunningLabel() {
      if (this.isCombinedStage) return '正在导出视频...';
      return this.workflowStage === 'output' ? '正在导出漫剧...' : '正在导出拼接预览...';
    },
    selectedShot() {
      if (this.selectedShotIndex < 0 || this.selectedShotIndex >= this.localShots.length) {
        return null;
      }
      return this.localShots[this.selectedShotIndex];
    },
    activeShots() {
      return this.localShots.filter((shot) => shot.includeInFinal !== false);
    },
    allSelectedForFinal() {
      return this.localShots.length > 0 && this.localShots.every((shot) => shot.includeInFinal !== false);
    },
    estimatedDurationSec() {
      return this.activeShots.reduce((total, shot) => total + this.parseDurationToSeconds(shot.duration), 0);
    }
  },
  watch: {
    shots: {
      immediate: true,
      deep: true,
      handler() {
        this.rebuildLocalShotsFromProps();
      }
    },
    selectedShotIndex() {
      this.tryPlayPreview();
    },
    'selectedShot.videoUrl': function () {
      this.tryPlayPreview();
    }
  },
  methods: {
    normalizeShot(rawShot) {
      const safe = rawShot && typeof rawShot === 'object' ? JSON.parse(JSON.stringify(rawShot)) : {};
      return {
        ...safe,
        title: safe.title || '',
        duration: safe.duration || '5s',
        videoUrl: typeof safe.videoUrl === 'string' ? safe.videoUrl.trim() : '',
        includeInFinal: safe.includeInFinal !== false,
        notes: safe.notes || '',
        startFrame: {
          description: safe.startFrame?.description || '',
          enhanced_prompt: safe.startFrame?.enhanced_prompt || '',
          image_url: safe.startFrame?.image_url || ''
        },
        endFrame: {
          description: safe.endFrame?.description || '',
          enhanced_prompt: safe.endFrame?.enhanced_prompt || '',
          image_url: safe.endFrame?.image_url || ''
        },
        videoTask: {
          taskId: safe.videoTask?.taskId || '',
          status: safe.videoTask?.status || '',
          message: safe.videoTask?.message || '',
          progress: Number.isFinite(Number(safe.videoTask?.progress)) ? Number(safe.videoTask.progress) : 0
        }
      };
    },
    rebuildLocalShotsFromProps() {
      const previousSelected = this.selectedShot?.title || '';
      this.localShots = (Array.isArray(this.shots) ? this.shots : []).map(this.normalizeShot);

      if (!this.localShots.length) {
        this.selectedShotIndex = -1;
        this.finalEditText = '';
        this.narrationText = '';
        return;
      }

      const matchedIndex = this.localShots.findIndex((shot) => shot.title === previousSelected);
      if (matchedIndex >= 0) {
        this.selectedShotIndex = matchedIndex;
      } else if (this.selectedShotIndex < 0 || this.selectedShotIndex >= this.localShots.length) {
        this.selectedShotIndex = 0;
      }

      if (!this.finalEditText.trim()) {
        this.syncFinalEditTextFromShots();
      }
    },
    parseDurationToSeconds(rawDuration) {
      const text = String(rawDuration || '').trim().toLowerCase();
      if (!text) return 5;

      const numericMatch = text.match(/\d+(\.\d+)?/);
      if (!numericMatch) return 5;
      const value = Number(numericMatch[0]);
      if (!Number.isFinite(value) || value <= 0) return 5;

      if (text.includes('min') || text.includes('分钟') || text.endsWith('m')) {
        return Math.round(value * 60);
      }
      return Math.round(value);
    },
    tryPlayPreview() {
      this.$nextTick(() => {
        const player = this.$refs.previewPlayer;
        if (!player) return;
        if (typeof player.load === 'function') {
          player.load();
        }
      });
    },
    addShot() {
      this.localShots.push(
        this.normalizeShot({
          title: `镜头 ${this.localShots.length + 1}`,
          duration: '5s',
          includeInFinal: true
        })
      );
      this.selectedShotIndex = this.localShots.length - 1;
      this.emitShotsUpdated();
    },
    toggleSelectAllForFinal() {
      if (!this.localShots.length) return;
      const nextValue = !this.allSelectedForFinal;
      this.localShots = this.localShots.map((shot) => ({
        ...shot,
        includeInFinal: nextValue
      }));
      this.emitShotsUpdated();
    },
    removeShot(index) {
      const shot = this.localShots[index];
      const ok = window.confirm(`确认删除镜头「${shot?.title || `#${index + 1}`}」吗？`);
      if (!ok) return;

      this.localShots.splice(index, 1);
      if (!this.localShots.length) {
        this.selectedShotIndex = -1;
      } else if (this.selectedShotIndex >= this.localShots.length) {
        this.selectedShotIndex = this.localShots.length - 1;
      }
      this.emitShotsUpdated();
    },
    moveShot(index, offset) {
      const nextIndex = index + offset;
      if (nextIndex < 0 || nextIndex >= this.localShots.length) return;

      const cloned = [...this.localShots];
      const [moved] = cloned.splice(index, 1);
      cloned.splice(nextIndex, 0, moved);
      this.localShots = cloned;
      this.selectedShotIndex = nextIndex;
      this.emitShotsUpdated();
    },
    selectShot(index) {
      this.selectedShotIndex = index;
    },
    emitShotsUpdated() {
      this.$emit('shots-updated', JSON.parse(JSON.stringify(this.localShots)));
    },
    buildFinalEditText() {
      const lines = [];
      lines.push(`第 ${this.currentEpisodeNo} 集 成片导出稿`);
      lines.push(`总镜头: ${this.activeShots.length} | 预计时长: ${this.estimatedDurationSec}s`);
      lines.push('');
      this.activeShots.forEach((shot, index) => {
        lines.push(`${index + 1}. ${shot.title || `镜头 ${index + 1}`} [${shot.duration || '5s'}]`);
        if (shot.notes) {
          lines.push(`   备注: ${shot.notes}`);
        }
        if (shot.videoUrl) {
          lines.push(`   视频: ${shot.videoUrl}`);
        }
      });
      lines.push('');
      lines.push('剪辑说明:');
      lines.push('- 在此补充转场、字幕、配乐、音效与节奏要求。');
      lines.push('');
      lines.push('【旁白文案】');
      if (this.narrationText.trim()) {
        lines.push(this.narrationText.trim());
      } else {
        lines.push('（可点击“生成旁白文案”自动生成）');
      }
      lines.push('【/旁白文案】');
      return lines.join('\n');
    },
    syncFinalEditTextFromShots() {
      this.finalEditText = this.buildFinalEditText();
    },
    buildNarrationDraftFromShots() {
      const lines = [];
      this.activeShots.forEach((shot, index) => {
        const title = String(shot?.title || `镜头 ${index + 1}`).trim();
        const duration = String(shot?.duration || '5s').trim();
        const summary = String(shot?.shotSummary || shot?.notes || '').trim();
        const detail = String(
          shot?.detailedPlot ||
          shot?.detailedShotDescription ||
          shot?.dialogueDetails ||
          ''
        ).trim();
        const body = [summary, detail].filter(Boolean).join('，');
        lines.push(`第${index + 1}段（${duration}）：${title}${body ? `，${body}` : ''}`.trim());
      });
      if (!lines.length) return '';
      return [
        `第 ${this.currentEpisodeNo} 集旁白草稿`,
        '要求：中文口播、句子短、每段对应一个镜头、禁止英文、避免镜头术语。',
        '',
        ...lines
      ].join('\n');
    },
    parseMarkerRange(text, beginMarker, endMarker) {
      const start = text.indexOf(beginMarker);
      const end = text.indexOf(endMarker);
      if (start < 0 || end < start) return null;
      return { start, end: end + endMarker.length };
    },
    applyNarrationToFinalEdit() {
      const narration = this.narrationText.trim();
      if (!narration) return;
      const beginMarker = '【旁白文案】';
      const endMarker = '【/旁白文案】';
      const block = `${beginMarker}\n${narration}\n${endMarker}`;
      const source = String(this.finalEditText || '').trim();
      if (!source) {
        this.finalEditText = this.buildFinalEditText();
        return;
      }
      const range = this.parseMarkerRange(source, beginMarker, endMarker);
      if (!range) {
        this.finalEditText = `${source}\n\n${block}`;
        return;
      }
      this.finalEditText = `${source.slice(0, range.start).trimEnd()}\n${block}\n${source.slice(range.end).trimStart()}`.trim();
    },
    async generateNarration() {
      if (!this.activeShots.length) {
        alert('没有可用于旁白生成的入片镜头');
        return;
      }
      this.generatingNarration = true;
      try {
        const draft = this.buildNarrationDraftFromShots();
        if (!draft) {
          this.narrationText = '';
          return;
        }
        const response = await axios.post('/api/enhance-prompt', {
          prompt: `请将以下镜头信息改写为可直接配音的中文旁白文案：\n${draft}`,
          context: {
            prompt_type: 'narration_script',
            output_format: 'voiceover_text',
            episode_no: this.currentEpisodeNo,
            shot_count: this.activeShots.length,
            language: 'zh-CN'
          }
        });
        const aiText = String(response?.data?.enhanced_prompt || '').trim();
        this.narrationText = aiText || draft;
      } catch (error) {
        // 接口异常时回退本地生成，保证功能可用
        const fallback = this.buildNarrationDraftFromShots();
        this.narrationText = fallback;
        const message = String(error?.response?.data?.error || error?.message || '生成失败').trim();
        alert(`旁白生成失败，已使用本地草稿：${message}`);
      } finally {
        this.generatingNarration = false;
      }
    },
    downloadBlob(blob, filename) {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
    downloadFinalJson() {
      const payload = {
        episode_no: this.currentEpisodeNo,
        exported_at: new Date().toISOString(),
        shots: this.activeShots,
        final_edit_text: this.finalEditText,
        narration_text: this.narrationText,
        assets_count: Array.isArray(this.assets) ? this.assets.length : 0
      };
      this.downloadBlob(
        new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }),
        `episode-${this.currentEpisodeNo}-final-cut.json`
      );
    },
    downloadFinalTxt() {
      const text = this.finalEditText.trim() || this.buildFinalEditText();
      this.downloadBlob(
        new Blob([text], { type: 'text/plain;charset=utf-8' }),
        `episode-${this.currentEpisodeNo}-final-cut.txt`
      );
    },
    parseFilenameFromDisposition(dispositionHeader, fallbackName) {
      if (!dispositionHeader) return fallbackName;
      const utf8Match = dispositionHeader.match(/filename\\*=UTF-8''([^;]+)/i);
      if (utf8Match && utf8Match[1]) {
        try {
          return decodeURIComponent(utf8Match[1]);
        } catch (_) {
          return utf8Match[1];
        }
      }
      const plainMatch = dispositionHeader.match(/filename="?([^";]+)"?/i);
      if (plainMatch && plainMatch[1]) {
        return plainMatch[1];
      }
      return fallbackName;
    },
    async exportFinalVideo() {
      if (!this.activeShots.length) {
        alert('没有可导出的入片镜头');
        return;
      }

      this.exportingVideo = true;
      this.exportVideoProgress = 8;
      this.exportVideoStatus = '正在提交导出任务...';

      let fakeProgressTimer = null;
      try {
        fakeProgressTimer = setInterval(() => {
          if (this.exportVideoProgress < 90) {
            this.exportVideoProgress += 4;
          }
        }, 1200);

        const requestPayload = {
          episode_no: this.currentEpisodeNo,
          shots: this.activeShots,
          final_edit_text: this.finalEditText,
          narration_text: this.narrationText
        };
        const requestConfig = {
          responseType: 'blob',
          timeout: 0,
        };

        let response;
        try {
          response = await axios.post('/api/export-video', requestPayload, requestConfig);
        } catch (error) {
          const msg = String(error?.message || '').toLowerCase();
          const noResponse = !error?.response;
          const host = String(window?.location?.hostname || '').trim();
          const canDirectRetry = noResponse && msg.includes('network') && (host === 'localhost' || host === '127.0.0.1');
          if (!canDirectRetry) throw error;

          this.exportVideoStatus = '代理连接中断，正在直连后端重试...';
          const directUrls = [`http://${host}:5000/api/export-video`];
          if (window.location.protocol === 'https:') {
            directUrls.push(`https://${host}:5000/api/export-video`);
          }

          let lastError = error;
          let directResponse = null;
          for (const directUrl of directUrls) {
            try {
              directResponse = await axios.post(directUrl, requestPayload, requestConfig);
              break;
            } catch (directErr) {
              lastError = directErr;
            }
          }
          if (!directResponse) throw lastError;
          response = directResponse;
        }

        this.exportVideoProgress = 100;
        this.exportVideoStatus = '导出完成，正在下载...';

        const fallbackName = `episode-${this.currentEpisodeNo}-final.mp4`;
        const filename = this.parseFilenameFromDisposition(response.headers['content-disposition'], fallbackName);
        this.downloadBlob(response.data, filename);
      } catch (error) {
        let message = error?.message || '导出失败';
        const responseBlob = error?.response?.data;

        if (responseBlob instanceof Blob) {
          message = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => {
              try {
                const parsed = JSON.parse(reader.result);
                resolve(parsed?.error || message);
              } catch (_) {
                resolve(message);
              }
            };
            reader.onerror = () => resolve(message);
            reader.readAsText(responseBlob);
          });
        } else if (error?.response?.data?.error) {
          message = error.response.data.error;
        }

        if (String(message).toLowerCase().includes('network error')) {
          message = '网络连接中断（可能是前端代理超时或连接被重置），请重试；如仍失败请重启前端开发服务后再导出';
        }

        this.exportVideoStatus = `导出失败：${message}`;
        this.exportVideoProgress = Math.max(this.exportVideoProgress, 90);
        alert(`导出成片视频失败：${message}`);
      } finally {
        if (fakeProgressTimer) {
          clearInterval(fakeProgressTimer);
        }
        setTimeout(() => {
          this.exportingVideo = false;
          if (this.exportVideoProgress >= 100) {
            this.exportVideoProgress = 0;
            this.exportVideoStatus = '';
          }
        }, 800);
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

.layout {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 16px;
}

.panel {
  background: #123038;
  border: 1px solid #2f5861;
  border-radius: 12px;
  padding: 14px;
}

.panel :deep(label) {
  color: #bfe6de;
}

.panel :deep(input),
.panel :deep(textarea),
.panel :deep(select) {
  background: #0f252a;
  border-color: #3f6a72;
  color: #e8fbf8;
}

.panel :deep(input:focus),
.panel :deep(textarea:focus),
.panel :deep(select:focus) {
  outline-color: rgba(45, 212, 191, 0.35);
  border-color: #2dd4bf;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.secondary-btn {
  background: #1b3e46;
  color: #def8f2;
}

.empty-state {
  padding: 12px;
  border-radius: 8px;
  background: #163840;
  color: #9fc5bf;
  border: 1px dashed #3f6a72;
}

.shot-table-wrap {
  max-height: 430px;
  overflow: auto;
  border: 1px solid #2f5861;
  border-radius: 8px;
}

.shot-table {
  width: 100%;
  border-collapse: collapse;
}

.shot-table th,
.shot-table td {
  border-top: 1px solid #2f5861;
  padding: 8px;
  text-align: left;
  vertical-align: middle;
  color: #d8f5ef;
}

.shot-table th {
  background: #1a3f47;
  color: #c5e7de;
}

.shot-table tbody tr.selected {
  background: rgba(45, 212, 191, 0.12);
}

.shot-table input[type='text'] {
  min-width: 120px;
}

.center-col {
  text-align: center;
}

.row-actions {
  display: flex;
  gap: 6px;
}

button.mini {
  padding: 4px 8px;
  font-size: 12px;
}

button.mini.danger {
  background: #b91c1c;
}

.summary-row {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  color: #bfe6de;
  font-size: 13px;
}

.preview-card {
  border: 1px solid #2f5861;
  border-radius: 8px;
  padding: 10px;
  background: #163840;
}

.preview-box {
  border-radius: 8px;
  overflow: hidden;
  background: #0f252a;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-box img {
  width: 100%;
  object-fit: cover;
}

.empty-preview {
  color: #9fc5bf;
  font-size: 13px;
}

.video-link {
  display: inline-block;
  margin-top: 8px;
  color: #7be6d2;
  text-decoration: underline;
  font-size: 12px;
}

.export-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.export-video-progress {
  margin-top: 12px;
  border: 1px solid #2f5861;
  background: #163840;
  border-radius: 8px;
  padding: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #bfe6de;
  margin-bottom: 6px;
}

.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: #2d545a;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #0ea5a3, #34d399);
  transition: width 0.35s ease;
}

@media (max-width: 1080px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .panel-header,
  .summary-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
