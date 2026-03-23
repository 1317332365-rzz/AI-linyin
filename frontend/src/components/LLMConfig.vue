<template>
  <div class="phase">
    <h2>LLM模型配置</h2>
    
    <!-- 流程选择 -->
    <div class="form-group">
      <label for="processSelect">流程选择</label>
      <select id="processSelect" v-model="selectedProcess">
        <option value="general">通用配置</option>
        <option value="script">剧本解析</option>
        <option value="character">角色生成</option>
        <option value="scene">场景生成</option>
        <option value="video">视频生成</option>
      </select>
    </div>
    
    <div class="config-section">
      <div class="form-group">
        <label for="sdkType">SDK 类型</label>
        <select id="sdkType" v-model="llmConfig.sdk_type">
          <option value="openai">OpenAI (通用)</option>
          <option value="dashscope">DashScope SDK (阿里云)</option>
          <option value="doubao">火山引擎 SDK (豆包)</option>
           <option value="grsai">GrsAI SDK (格拉斯AI)</option>

        </select>
      </div>
      <div class="form-group">
        <label for="model">模型名称</label>
        <input 
          type="text" 
          id="model" 
          v-model="llmConfig.model" 
          placeholder="例如：gemini-2.5-flash, gpt-4, claude-3..."
        />
      </div>
      <div class="form-group">
        <label for="apiKey">API Key</label>
        <input 
          type="text" 
          id="apiKey" 
          v-model="llmConfig.api_key" 
          placeholder="输入你的 API Key..."
        />
      </div>
      <div class="form-group">
        <label for="baseUrl">Base URL (可选)</label>
        <input 
          type="text" 
          id="baseUrl" 
          v-model="llmConfig.base_url" 
          placeholder="例如：https://api.openai.com/v1 或第三方 API 地址"
        />
      </div>
      <div class="form-group">
        <label for="temperature">Temperature</label>
        <input 
          type="number" 
          id="temperature" 
          v-model.number="llmConfig.temperature" 
          min="0" 
          max="1" 
          step="0.1"
        />
      </div>
      <div class="form-group">
        <label for="maxTokens">Max Tokens</label>
        <input 
          type="number" 
          id="maxTokens" 
          v-model.number="llmConfig.max_tokens" 
          min="100" 
          max="10000" 
          step="100"
        />
      </div>
      <div class="button-group">
        <button @click="updateLLMConfig" :disabled="loading">
          {{ loading ? '保存中...' : '保存配置' }}
        </button>
        <button @click="testLLMConnection" :disabled="loading || !llmConfig.api_key">
          {{ loading ? '测试中...' : '测试连接' }}
        </button>
      </div>
      <div v-if="configSaved" class="success-message">
        配置保存成功！
      </div>
      <div v-if="testResult" :class="['test-result', testResult.status]">
        {{ testResult.message }}
      </div>
    </div>
    
    <div class="config-info" style="margin-top: 20px;">
      <h3>配置说明</h3>
      <ul>
        <li><strong>流程选择</strong>：选择要配置的流程，每个流程可以有不同的模型配置</li>
        <li><strong>模型名称</strong>：直接输入模型名称，如 gpt-4、claude-3 等</li>
        <li><strong>API Key</strong>：对应模型的 API 密钥</li>
        <li><strong>Base URL</strong>：可选，用于配置第三方 API 服务（如阿里云百炼、智谱 AI 等）</li>
        <li><strong>Temperature</strong>：控制生成文本的随机性，值越高越随机</li>
        <li><strong>Max Tokens</strong>：控制生成文本的最大长度</li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LLMConfig',
  data() {
    return {
      selectedProcess: 'general',
      llmConfig: {
        model: 'gpt-4',
        api_key: '',
        base_url: '',
        temperature: 0.7,
        max_tokens: 1000,
        sdk_type: 'openai'
      },
      loading: false,
      configSaved: false,
      testResult: null
    };
  },
  watch: {
    selectedProcess: function(newProcess) {
      this.loadLLMConfig();
    }
  },
  mounted() {
    this.loadLLMConfig();
  },
  methods: {
    async loadLLMConfig() {
      try {
        const response = await axios.get(`/api/llm-config?process=${this.selectedProcess}`);
        this.llmConfig = response.data;
      } catch (error) {
        console.error('加载LLM配置失败:', error);
      }
    },
    async updateLLMConfig() {
      this.loading = true;
      this.configSaved = false;
      try {
        const response = await axios.post('/api/llm-config', {
          ...this.llmConfig,
          process: this.selectedProcess
        });
        this.llmConfig = response.data;
        this.configSaved = true;
        setTimeout(() => {
          this.configSaved = false;
        }, 3000);
      } catch (error) {
        console.error('更新LLM配置失败:', error);
        alert('更新配置失败，请重试');
      } finally {
        this.loading = false;
      }
    },
    async testLLMConnection() {
      this.loading = true;
      this.testResult = null;
      try {
        const response = await axios.post('/api/test-llm', {
          ...this.llmConfig,
          process: this.selectedProcess
        });
        this.testResult = response.data;
      } catch (error) {
        console.error('测试LLM连接失败:', error);
        this.testResult = {
          status: 'error',
          message: '测试失败：' + (error.response?.data?.error || error.message)
        };
      } finally {
        this.loading = false;
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

.phase :deep(label) {
  color: #bfe6de;
}

.phase :deep(input),
.phase :deep(select),
.phase :deep(textarea) {
  background: #0f252a;
  border-color: #3f6a72;
  color: #e8fbf8;
}

.phase :deep(input:focus),
.phase :deep(select:focus),
.phase :deep(textarea:focus) {
  outline-color: rgba(45, 212, 191, 0.35);
  border-color: #2dd4bf;
}

.config-section {
  background-color: #123038;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #2f5861;
  border-left: 4px solid #2dd4bf;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.success-message {
  margin-top: 15px;
  padding: 10px;
  background-color: rgba(15, 118, 110, 0.24);
  color: #6ee7b7;
  border-radius: 6px;
  border: 1px solid rgba(45, 212, 191, 0.45);
  text-align: center;
}

.test-result {
  margin-top: 15px;
  padding: 10px;
  border-radius: 6px;
  text-align: center;
}

.test-result.success {
  background-color: rgba(15, 118, 110, 0.24);
  color: #6ee7b7;
  border: 1px solid rgba(45, 212, 191, 0.45);
}

.test-result.error {
  background-color: rgba(185, 28, 28, 0.2);
  color: #fecaca;
  border: 1px solid rgba(248, 113, 113, 0.45);
}

.config-info {
  background-color: #123038;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #2f5861;
  border-left: 4px solid #34d399;
}

.config-info ul {
  margin-top: 10px;
  padding-left: 20px;
}

.config-info li {
  margin-bottom: 8px;
  color: #bfe6de;
}
</style>
