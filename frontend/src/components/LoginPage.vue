<template>
  <div class="login-shell">
    <div class="ambient ambient-left"></div>
    <div class="ambient ambient-right"></div>

    <div class="login-card">
      <section class="welcome-panel">
        <div class="brand-row">
          <div class="brand-dot">智</div>
          <div>
            <h1>智作工作台</h1>
            <p>{{ isRegisterMode ? '邮箱注册新工作台' : '邮箱登录工作台' }}</p>
          </div>
        </div>

        <h2>{{ isRegisterMode ? '创建你的邮箱账户' : '继续进入你的项目空间' }}</h2>
        <p class="welcome-copy">
          {{ isRegisterMode
            ? '使用邮箱创建新账户。注册完成后会自动登录，并直接进入独立工作空间。'
            : '使用邮箱登录后，继续访问当前账户下的剧本、资产、导演工作台和导出记录。' }}
        </p>

        <div class="feature-list">
          <div class="feature-item">
            <span class="feature-index">01</span>
            <span>每个邮箱对应独立项目与工作空间</span>
          </div>
          <div class="feature-item">
            <span class="feature-index">02</span>
            <span>移动端和 Web 端可使用同一邮箱账户</span>
          </div>
        </div>
      </section>

      <section class="form-panel">
        <div class="mode-switch" role="tablist" aria-label="认证模式">
          <button
            type="button"
            class="mode-chip"
            :class="{ active: !isRegisterMode }"
            @click="switchMode('login')"
          >
            登录
          </button>
          <button
            type="button"
            class="mode-chip"
            :class="{ active: isRegisterMode }"
            @click="switchMode('register')"
          >
            注册
          </button>
        </div>

        <form class="login-form" @submit.prevent="submitAuth">
          <label for="auth-email">邮箱地址</label>
          <input
            id="auth-email"
            v-model.trim="email"
            type="email"
            inputmode="email"
            autocomplete="email"
            placeholder="请输入邮箱地址"
            required
          />

          <label for="auth-password">密码</label>
          <input
            id="auth-password"
            v-model="password"
            type="password"
            :autocomplete="isRegisterMode ? 'new-password' : 'current-password'"
            placeholder="请输入至少 6 位密码"
            required
          />

          <template v-if="isRegisterMode">
            <label for="auth-confirm-password">确认密码</label>
            <input
              id="auth-confirm-password"
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="请再次输入密码"
              required
            />
          </template>

          <label v-else class="remember-row">
            <input v-model="rememberPassword" type="checkbox" />
            <span>记住密码</span>
          </label>

          <button type="submit" class="submit-btn" :disabled="loading">
            {{ submitText }}
          </button>
        </form>

        <p class="switch-copy">
          {{ isRegisterMode ? '已经有邮箱账户？' : '还没有邮箱账户？' }}
          <button
            type="button"
            class="text-link"
            :disabled="loading"
            @click="switchMode(isRegisterMode ? 'login' : 'register')"
          >
            {{ isRegisterMode ? '返回登录' : '立即注册' }}
          </button>
        </p>

        <p class="helper-text">
          {{ isRegisterMode
            ? '注册成功后将自动登录'
            : '项目列表按当前邮箱独立隔离。' }}
        </p>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
const REMEMBER_FLAG_KEY = 'cinegen_remember_password';
const REMEMBER_EMAIL_KEY = 'cinegen_remember_email';
const REMEMBER_PASSWORD_KEY = 'cinegen_remember_password_value';
const AUTH_ERROR_MAP = {
  Unauthorized: '登录状态已失效，请重新操作',
  'Username is required': '请输入邮箱地址',
  'Please enter a valid username': '请输入正确的邮箱地址',
  'Username already exists': '该邮箱已注册',
  'Invalid email or password': '邮箱或密码错误',
  'Email already exists': '该邮箱已注册',
  'Email is required': '请输入邮箱地址',
  'Please enter a valid email address': '请输入正确的邮箱地址',
  'Password is required': '请输入密码',
  'Password must be at least 6 characters': '密码至少 6 位',
  'Password must be 128 characters or fewer': '密码不能超过 128 位'
};

export default {
  name: 'LoginPage',
  emits: ['login-success'],
  data() {
    return {
      mode: 'login',
      email: '',
      password: '',
      confirmPassword: '',
      rememberPassword: false,
      loading: false,
      errorMessage: ''
    };
  },
  computed: {
    isRegisterMode() {
      return this.mode === 'register';
    },
    submitText() {
      if (this.loading) {
        return this.isRegisterMode ? '注册中...' : '登录中...';
      }
      return this.isRegisterMode ? '创建邮箱账户' : '进入工作台';
    }
  },
  mounted() {
    const remember = localStorage.getItem(REMEMBER_FLAG_KEY) === '1';
    const savedEmail = localStorage.getItem(REMEMBER_EMAIL_KEY) || '';
    const savedPassword = localStorage.getItem(REMEMBER_PASSWORD_KEY) || '';

    this.rememberPassword = remember;
    if (savedEmail) {
      this.email = savedEmail;
    }
    if (remember && savedPassword) {
      this.password = savedPassword;
    }
  },
  watch: {
    rememberPassword(newValue) {
      if (newValue) {
        localStorage.setItem(REMEMBER_FLAG_KEY, '1');
        localStorage.setItem(REMEMBER_EMAIL_KEY, this.normalizeEmail(this.email));
        localStorage.setItem(REMEMBER_PASSWORD_KEY, this.password || '');
      } else {
        localStorage.setItem(REMEMBER_FLAG_KEY, '0');
        localStorage.removeItem(REMEMBER_PASSWORD_KEY);
      }
    },
    email(newValue) {
      if (this.rememberPassword) {
        localStorage.setItem(REMEMBER_EMAIL_KEY, this.normalizeEmail(newValue));
      }
    },
    password(newValue) {
      if (this.rememberPassword && !this.isRegisterMode) {
        localStorage.setItem(REMEMBER_PASSWORD_KEY, newValue || '');
      }
    }
  },
  methods: {
    normalizeEmail(value) {
      return String(value || '').trim().toLowerCase();
    },
    formatAuthError(error, fallback) {
      const message = String(error?.response?.data?.error || error?.message || '').trim();
      return AUTH_ERROR_MAP[message] || message || fallback;
    },
    switchMode(mode) {
      if (this.loading || this.mode === mode) {
        return;
      }
      this.mode = mode;
      this.errorMessage = '';
      this.confirmPassword = '';
      if (mode === 'register') {
        this.rememberPassword = false;
      }
    },
    validateForm() {
      const email = this.normalizeEmail(this.email);
      const password = String(this.password || '');

      if (!email || !password) {
        return '请输入邮箱和密码';
      }
      if (!EMAIL_RE.test(email)) {
        return '请输入正确的邮箱地址';
      }
      if (this.isRegisterMode) {
        if (password.length < 6) {
          return '密码至少 6 位';
        }
        if (password !== String(this.confirmPassword || '')) {
          return '两次输入的密码不一致';
        }
      }
      return '';
    },
    async submitAuth() {
      const validationError = this.validateForm();
      if (validationError) {
        this.errorMessage = validationError;
        return;
      }

      const email = this.normalizeEmail(this.email);
      const password = String(this.password || '');

      this.errorMessage = '';
      this.loading = true;
      try {
        const response = await axios.post(
          this.isRegisterMode ? '/api/auth/register' : '/api/auth/login',
          { email, password }
        );

        if (!this.isRegisterMode && this.rememberPassword) {
          localStorage.setItem(REMEMBER_FLAG_KEY, '1');
          localStorage.setItem(REMEMBER_EMAIL_KEY, email);
          localStorage.setItem(REMEMBER_PASSWORD_KEY, password);
        } else {
          localStorage.setItem(REMEMBER_FLAG_KEY, this.rememberPassword ? '1' : '0');
          localStorage.setItem(REMEMBER_EMAIL_KEY, email);
          localStorage.removeItem(REMEMBER_PASSWORD_KEY);
        }

        this.$emit('login-success', response.data || {});
        this.confirmPassword = '';
        if (!this.rememberPassword) {
          this.password = '';
        }
      } catch (error) {
        this.errorMessage = this.formatAuthError(
          error,
          this.isRegisterMode ? '注册失败，请重试' : '登录失败，请重试'
        );
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-shell {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  overflow: hidden;
  padding: 28px;
  background:
    radial-gradient(circle at 14% 16%, rgba(63, 170, 151, 0.24), transparent 28%),
    radial-gradient(circle at 82% 78%, rgba(45, 212, 191, 0.18), transparent 26%),
    linear-gradient(180deg, #071417 0%, #0a1e22 52%, #061115 100%);
}

.ambient {
  position: absolute;
  border-radius: 999px;
  filter: blur(22px);
  pointer-events: none;
}

.ambient-left {
  top: 72px;
  left: -90px;
  width: 260px;
  height: 260px;
  background: rgba(37, 148, 130, 0.18);
}

.ambient-right {
  right: -80px;
  bottom: 60px;
  width: 240px;
  height: 240px;
  background: rgba(107, 230, 216, 0.16);
}

.login-card {
  position: relative;
  z-index: 1;
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(360px, 420px);
  gap: 22px;
  border-radius: 28px;
  border: 1px solid rgba(79, 124, 130, 0.45);
  background: rgba(9, 24, 29, 0.88);
  box-shadow: 0 32px 90px rgba(3, 12, 15, 0.42);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

.welcome-panel {
  padding: 34px 34px 30px;
  background:
    linear-gradient(135deg, rgba(24, 78, 83, 0.56), rgba(9, 22, 27, 0.28)),
    radial-gradient(circle at 85% 18%, rgba(112, 231, 217, 0.16), transparent 28%);
  color: #effdfa;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-dot {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #f4fffd;
  border: 1px solid rgba(132, 221, 209, 0.35);
  background: linear-gradient(135deg, rgba(26, 87, 91, 0.96), rgba(19, 58, 62, 0.96));
}

.brand-row h1 {
  margin: 0;
  font-size: 20px;
}

.brand-row p {
  margin: 4px 0 0;
  color: #9ed6cd;
  font-size: 13px;
}

.welcome-panel h2 {
  margin: 26px 0 0;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.06;
}

.welcome-copy {
  margin: 16px 0 0;
  max-width: 520px;
  color: #afdfd7;
  line-height: 1.75;
  font-size: 15px;
}

.feature-list {
  margin-top: 24px;
  display: grid;
  gap: 12px;
}

.feature-item {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(124, 205, 194, 0.14);
  background: rgba(7, 21, 24, 0.44);
  color: #ddfaf5;
}

.feature-index {
  font-size: 12px;
  font-weight: 700;
  color: #76ddcc;
  letter-spacing: 0.1em;
}

.form-panel {
  padding: 26px;
  background: linear-gradient(180deg, rgba(8, 20, 23, 0.98), rgba(10, 25, 28, 0.92));
  color: #ecfcf8;
}

.mode-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}

.mode-chip {
  height: 42px;
  border-radius: 999px;
  border: 1px solid #315e67;
  background: #0d2429;
  color: #9fd2cb;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.mode-chip.active {
  border-color: transparent;
  background: linear-gradient(135deg, #238d7d, #17695f);
  color: #f1fdfa;
  box-shadow: 0 16px 36px rgba(23, 105, 95, 0.26);
}

.login-form {
  display: grid;
  gap: 10px;
}

.login-form label {
  font-size: 13px;
  color: #c5eee7;
}

.login-form input {
  height: 46px;
  border-radius: 12px;
  border: 1px solid #35656e;
  background: rgba(12, 31, 35, 0.92);
  color: #edfffb;
  padding: 0 14px;
  outline: none;
}

.login-form input::placeholder {
  color: #7da9a2;
}

.login-form input:focus {
  border-color: #65d7c4;
  box-shadow: 0 0 0 3px rgba(101, 215, 196, 0.12);
}

.remember-row {
  margin-top: 6px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  user-select: none;
  font-size: 13px;
  color: #bfe6de;
}

.remember-row input[type='checkbox'] {
  width: 15px;
  height: 15px;
  margin: 0;
}

.submit-btn {
  margin-top: 10px;
  height: 46px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #249681, #1b6e63);
  color: #f3fffd;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 18px 34px rgba(22, 110, 99, 0.28);
}

.submit-btn:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}

.switch-copy {
  margin: 16px 0 0;
  color: #97c8c1;
  font-size: 13px;
}

.text-link {
  margin-left: 6px;
  padding: 0;
  border: none;
  background: transparent;
  color: #74dcca;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.text-link:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}

.helper-text {
  margin-top: 12px;
  color: #8dbab3;
  font-size: 12px;
  line-height: 1.7;
}

.error-text {
  margin-top: 14px;
  color: #ffd7d7;
  background: rgba(140, 33, 33, 0.24);
  border: 1px solid rgba(248, 113, 113, 0.42);
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
}

@media (max-width: 880px) {
  .login-shell {
    padding: 18px;
  }

  .login-card {
    grid-template-columns: 1fr;
  }

  .welcome-panel {
    padding-bottom: 22px;
  }
}
</style>
