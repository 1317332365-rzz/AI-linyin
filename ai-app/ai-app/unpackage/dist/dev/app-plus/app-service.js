if (typeof Promise !== "undefined" && !Promise.prototype.finally) {
  Promise.prototype.finally = function(callback) {
    const promise = this.constructor;
    return this.then(
      (value) => promise.resolve(callback()).then(() => value),
      (reason) => promise.resolve(callback()).then(() => {
        throw reason;
      })
    );
  };
}
;
if (typeof uni !== "undefined" && uni && uni.requireGlobal) {
  const global = uni.requireGlobal();
  ArrayBuffer = global.ArrayBuffer;
  Int8Array = global.Int8Array;
  Uint8Array = global.Uint8Array;
  Uint8ClampedArray = global.Uint8ClampedArray;
  Int16Array = global.Int16Array;
  Uint16Array = global.Uint16Array;
  Int32Array = global.Int32Array;
  Uint32Array = global.Uint32Array;
  Float32Array = global.Float32Array;
  Float64Array = global.Float64Array;
  BigInt64Array = global.BigInt64Array;
  BigUint64Array = global.BigUint64Array;
}
;
if (uni.restoreGlobal) {
  uni.restoreGlobal(Vue, weex, plus, setTimeout, clearTimeout, setInterval, clearInterval);
}
(function(vue) {
  "use strict";
  const _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  const _sfc_main$a = {
    name: "u--input",
    props: {
      value: {
        type: [String, Number],
        default: ""
      },
      modelValue: {
        type: [String, Number],
        default: ""
      },
      type: {
        type: String,
        default: "text"
      },
      password: {
        type: Boolean,
        default: false
      },
      placeholder: {
        type: String,
        default: ""
      },
      disabled: {
        type: Boolean,
        default: false
      },
      maxlength: {
        type: [Number, String],
        default: 140
      },
      focus: {
        type: Boolean,
        default: false
      },
      cursorSpacing: {
        type: [Number, String],
        default: 24
      },
      confirmType: {
        type: String,
        default: "done"
      },
      customStyle: {
        type: [String, Object],
        default: ""
      }
    },
    computed: {
      innerValue() {
        if (this.modelValue !== "" && this.modelValue !== void 0 && this.modelValue !== null) {
          return String(this.modelValue);
        }
        return String(this.value || "");
      },
      nativeType() {
        return this.password ? "text" : this.type;
      },
      wrapStyle() {
        if (!this.customStyle) {
          return "";
        }
        if (typeof this.customStyle === "string") {
          return this.customStyle;
        }
        return this.customStyle;
      }
    },
    methods: {
      handleInput(event) {
        const nextValue = event && event.detail ? event.detail.value : "";
        this.$emit("input", nextValue);
        this.$emit("update:modelValue", nextValue);
        this.$emit("change", nextValue);
      },
      handleFocus(event) {
        this.$emit("focus", event);
      },
      handleBlur(event) {
        this.$emit("blur", event);
      },
      handleConfirm(event) {
        this.$emit("confirm", event);
      }
    }
  };
  function _sfc_render$9(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock(
      "view",
      {
        class: vue.normalizeClass(["u-input-wrap", { disabled: $props.disabled }]),
        style: vue.normalizeStyle($options.wrapStyle)
      },
      [
        vue.createElementVNode("input", {
          class: "u-input-inner",
          value: $options.innerValue,
          type: $options.nativeType,
          password: $props.password,
          placeholder: $props.placeholder,
          disabled: $props.disabled,
          maxlength: $props.maxlength,
          focus: $props.focus,
          "cursor-spacing": $props.cursorSpacing,
          "confirm-type": $props.confirmType,
          onInput: _cache[0] || (_cache[0] = (...args) => $options.handleInput && $options.handleInput(...args)),
          onFocus: _cache[1] || (_cache[1] = (...args) => $options.handleFocus && $options.handleFocus(...args)),
          onBlur: _cache[2] || (_cache[2] = (...args) => $options.handleBlur && $options.handleBlur(...args)),
          onConfirm: _cache[3] || (_cache[3] = (...args) => $options.handleConfirm && $options.handleConfirm(...args))
        }, null, 40, ["value", "type", "password", "placeholder", "disabled", "maxlength", "focus", "cursor-spacing", "confirm-type"])
      ],
      6
      /* CLASS, STYLE */
    );
  }
  const __easycom_0$1 = /* @__PURE__ */ _export_sfc(_sfc_main$a, [["render", _sfc_render$9], ["__scopeId", "data-v-94c12ece"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/uni_modules/uview-ui/components/u--input/u--input.vue"]]);
  function resolveEasycom(component, easycom) {
    return typeof component === "string" ? easycom : component;
  }
  const _sfc_main$9 = {
    name: "UButton",
    props: {
      type: {
        type: String,
        default: "default"
      },
      loading: {
        type: Boolean,
        default: false
      },
      disabled: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      handleClick(event) {
        if (this.disabled || this.loading) {
          return;
        }
        this.$emit("click", event);
      }
    }
  };
  function _sfc_render$8(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("button", {
      class: vue.normalizeClass(["u-button", [`u-button--${$props.type}`, { "u-button--disabled": $props.disabled, "u-button--loading": $props.loading }]]),
      disabled: $props.disabled || $props.loading,
      onClick: _cache[0] || (_cache[0] = (...args) => $options.handleClick && $options.handleClick(...args))
    }, [
      $props.loading ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "u-button__loading"
      })) : vue.createCommentVNode("v-if", true),
      vue.renderSlot(_ctx.$slots, "default", {}, void 0, true)
    ], 10, ["disabled"]);
  }
  const __easycom_0 = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["render", _sfc_render$8], ["__scopeId", "data-v-80ba9a3f"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/uni_modules/uview-ui/components/u-button/u-button.vue"]]);
  const APP_CONFIG = {
    apiBaseUrl: "http://47.96.145.239/api"
  };
  const STORAGE_KEYS = {
    authToken: "cinegen_mobile_auth_token",
    authUser: "cinegen_mobile_auth_user",
    currentProjectId: "cinegen_mobile_current_project_id",
    projectCache: "cinegen_mobile_current_project_cache",
    studioView: "cinegen_mobile_studio_view"
  };
  const DEFAULT_BASE_URL = APP_CONFIG.apiBaseUrl;
  function safeGet(key) {
    try {
      return uni.getStorageSync(key);
    } catch (error) {
      return "";
    }
  }
  function safeSet(key, value) {
    try {
      uni.setStorageSync(key, value);
    } catch (error) {
    }
  }
  function safeRemove(key) {
    try {
      uni.removeStorageSync(key);
    } catch (error) {
    }
  }
  function toTrimmedString(value) {
    return String(value || "").trim();
  }
  function resolveUserScope(username = "") {
    return toTrimmedString(username) || toTrimmedString(safeGet(STORAGE_KEYS.authUser)) || "guest";
  }
  function scopedKey(baseKey, username = "") {
    return `${baseKey}:${resolveUserScope(username)}`;
  }
  function normalizeBaseUrl(value) {
    let url = toTrimmedString(value);
    if (!url) {
      return DEFAULT_BASE_URL;
    }
    if (!/^https?:\/\//i.test(url)) {
      url = `http://${url}`;
    }
    return url.replace(/\/+$/, "");
  }
  function getBaseUrl() {
    return normalizeBaseUrl(DEFAULT_BASE_URL);
  }
  function getAuthToken() {
    return toTrimmedString(safeGet(STORAGE_KEYS.authToken));
  }
  function getCurrentUser() {
    return toTrimmedString(safeGet(STORAGE_KEYS.authUser));
  }
  function saveAuthSession(payload = {}) {
    const token = toTrimmedString(payload.token);
    const username = toTrimmedString(payload.email || payload.username);
    safeSet(STORAGE_KEYS.authToken, token);
    safeSet(STORAGE_KEYS.authUser, username);
  }
  function clearAuthSession() {
    safeRemove(STORAGE_KEYS.authToken);
    safeRemove(STORAGE_KEYS.authUser);
  }
  function getCurrentProjectId(username = "") {
    return toTrimmedString(safeGet(scopedKey(STORAGE_KEYS.currentProjectId, username)));
  }
  function setCurrentProjectId(projectId, username = "") {
    const normalized = toTrimmedString(projectId);
    const key = scopedKey(STORAGE_KEYS.currentProjectId, username);
    if (!normalized) {
      safeRemove(key);
      return "";
    }
    safeSet(key, normalized);
    return normalized;
  }
  function saveProjectCache(project, username = "") {
    const key = scopedKey(STORAGE_KEYS.projectCache, username);
    if (!project || typeof project !== "object") {
      safeRemove(key);
      return null;
    }
    const normalized = JSON.parse(JSON.stringify(project));
    safeSet(key, JSON.stringify(normalized));
    if (normalized.id) {
      setCurrentProjectId(normalized.id, username);
    }
    return normalized;
  }
  function getProjectCache(username = "") {
    const raw = toTrimmedString(safeGet(scopedKey(STORAGE_KEYS.projectCache, username)));
    if (!raw) {
      return null;
    }
    try {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : null;
    } catch (error) {
      return null;
    }
  }
  function saveStudioView(payload = {}, username = "") {
    const key = scopedKey(STORAGE_KEYS.studioView, username);
    const mainTab = toTrimmedString(payload.mainTab);
    const createTab = toTrimmedString(payload.createTab);
    if (!mainTab && !createTab) {
      safeRemove(key);
      return null;
    }
    const value = {
      mainTab: mainTab || "create",
      createTab: createTab || "project"
    };
    safeSet(key, JSON.stringify(value));
    return value;
  }
  function getStudioView(username = "") {
    const raw = toTrimmedString(safeGet(scopedKey(STORAGE_KEYS.studioView, username)));
    if (!raw) {
      return null;
    }
    try {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : null;
    } catch (error) {
      return null;
    }
  }
  function isObject(value) {
    return value && typeof value === "object" && !Array.isArray(value);
  }
  function encodeParams(params = {}) {
    const items = [];
    Object.keys(params || {}).forEach((key) => {
      const value = params[key];
      if (value === void 0 || value === null || value === "") {
        return;
      }
      items.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
    });
    return items.join("&");
  }
  function buildHeaders(extraHeader = {}, method = "GET", withAuth = true) {
    const header = { ...extraHeader };
    const token = withAuth ? getAuthToken() : "";
    if (token) {
      header.Authorization = `Bearer ${token}`;
    }
    if (!header["Content-Type"] && method !== "GET") {
      header["Content-Type"] = "application/json";
    }
    return header;
  }
  function buildRequestUrl(url = "") {
    const baseUrl = getBaseUrl().replace(/\/+$/, "");
    let requestPath = String(url || "").trim();
    if (!requestPath) {
      return baseUrl;
    }
    if (!requestPath.startsWith("/")) {
      requestPath = `/${requestPath}`;
    }
    if (baseUrl.endsWith("/api") && requestPath.startsWith("/api/")) {
      requestPath = requestPath.slice(4);
    }
    return `${baseUrl}${requestPath}`;
  }
  function translateErrorMessage(message = "", statusCode = 0) {
    const text = String(message || "").trim();
    const translatedMap = {
      Unauthorized: "登录状态已失效，请重新登录",
      "Invalid email or password": "邮箱或密码错误",
      "Email already exists": "该邮箱已注册",
      "Email is required": "请输入邮箱地址",
      "Please enter a valid email address": "请输入正确的邮箱地址",
      "Password is required": "请输入密码",
      "Password must be at least 6 characters": "密码至少 6 位",
      "Password must be 128 characters or fewer": "密码不能超过 128 位"
    };
    if (translatedMap[text]) {
      return translatedMap[text];
    }
    if (statusCode === 401 && !text) {
      return "登录状态已失效，请重新登录";
    }
    return text;
  }
  function normalizeError({ statusCode = 0, data = null, message = "" } = {}) {
    const payloadMessage = isObject(data) && (data.error || data.message || data.detail) || message || (statusCode ? `请求失败 (${statusCode})` : "网络请求失败");
    return {
      statusCode,
      data,
      message: translateErrorMessage(payloadMessage, statusCode) || "请求失败"
    };
  }
  function shouldClearAuthBy401(statusCode = 0, data = null, withAuth = true) {
    if (!withAuth || Number(statusCode) !== 401 || !isObject(data)) {
      return false;
    }
    const message = String(data.error || data.message || data.detail || "").trim().toLowerCase();
    return message === "unauthorized";
  }
  function requestRaw(options = {}) {
    const {
      url = "",
      method = "GET",
      data = null,
      params = null,
      header = {},
      timeout = 6e4,
      responseType = "text",
      withAuth = true
    } = options;
    const queryString = params ? encodeParams(params) : "";
    const fullUrl = `${buildRequestUrl(url)}${queryString ? `?${queryString}` : ""}`;
    return new Promise((resolve, reject) => {
      uni.request({
        url: fullUrl,
        method,
        data,
        timeout,
        responseType,
        header: buildHeaders(header, method, withAuth),
        success: (response) => {
          const statusCode = Number(response.statusCode || 0);
          if (statusCode >= 200 && statusCode < 300) {
            resolve(response);
            return;
          }
          if (shouldClearAuthBy401(statusCode, response.data, withAuth)) {
            clearAuthSession();
          }
          reject(normalizeError({ statusCode, data: response.data }));
        },
        fail: (error) => {
          reject(
            normalizeError({
              message: error && error.errMsg ? error.errMsg : "网络请求失败"
            })
          );
        }
      });
    });
  }
  function request(options = {}) {
    return requestRaw(options).then((response) => response.data);
  }
  const http = {
    get(url, params = null, options = {}) {
      return request({ ...options, url, method: "GET", params });
    },
    post(url, data = {}, options = {}) {
      return request({ ...options, url, method: "POST", data });
    },
    put(url, data = {}, options = {}) {
      return request({ ...options, url, method: "PUT", data });
    }
  };
  function login(payload) {
    return http.post("/api/auth/login", payload, { withAuth: false });
  }
  function register(payload) {
    return http.post("/api/auth/register", payload, { withAuth: false });
  }
  function logout() {
    return http.post("/api/auth/logout", {});
  }
  function authStatus() {
    return http.get("/api/auth/status");
  }
  function relaunchTo(url) {
    uni.reLaunch({ url });
  }
  function ensureAuth() {
    if (getAuthToken()) {
      return true;
    }
    relaunchTo("/views/account/index");
    return false;
  }
  const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  const AUTH_ERROR_MAP = {
    Unauthorized: "当前登录状态已失效，请重新登录",
    "Username is required": "请输入用户名",
    "Please enter a valid username": "请输入有效的用户名",
    "Username already exists": "用户名已存在",
    "Invalid email or password": "邮箱或密码错误",
    "Email already exists": "该邮箱已注册",
    "Email is required": "请输入邮箱地址",
    "Please enter a valid email address": "请输入有效的邮箱地址",
    "Password is required": "请输入密码",
    "Password must be at least 6 characters": "密码长度不能少于 6 位",
    "Password must be 128 characters or fewer": "密码长度不能超过 128 位"
  };
  const _sfc_main$8 = {
    components: {
      "u--input": __easycom_0$1,
      UButton: __easycom_0
    },
    data() {
      return {
        mode: "login",
        email: "",
        password: "",
        confirmPassword: "",
        loading: false,
        checking: false,
        errorMessage: ""
      };
    },
    computed: {
      isRegisterMode() {
        return this.mode === "register";
      },
      buttonLoading() {
        return this.loading || this.checking;
      },
      buttonText() {
        if (this.checking) {
          return "正在检测登录状态...";
        }
        if (this.loading) {
          return this.isRegisterMode ? "正在注册..." : "正在登录...";
        }
        return this.isRegisterMode ? "创建账号" : "立即登录";
      }
    },
    onLoad() {
      this.tryRestoreSession();
    },
    methods: {
      formatAuthError(error, fallback) {
        const message = String(error && error.message || "").trim();
        return AUTH_ERROR_MAP[message] || message || fallback;
      },
      switchMode(mode) {
        if (this.buttonLoading || this.mode === mode) {
          return;
        }
        this.mode = mode;
        this.errorMessage = "";
        this.confirmPassword = "";
      },
      normalizeEmail(value) {
        return String(value || "").trim();
      },
      async tryRestoreSession() {
        const token = getAuthToken();
        if (!token) {
          return;
        }
        this.checking = true;
        try {
          const response = await authStatus();
          saveAuthSession({
            token,
            email: response.email || response.username || ""
          });
          relaunchTo("/views/projects/index");
        } catch (error) {
          const statusCode = Number(error && error.statusCode || 0);
          if (statusCode === 401) {
            clearAuthSession();
          }
        } finally {
          this.checking = false;
        }
      },
      validateForm() {
        const email = this.normalizeEmail(this.email);
        const password = String(this.password || "");
        if (!email) {
          return "请输入邮箱地址";
        }
        if (!EMAIL_RE.test(email)) {
          return "请输入有效的邮箱地址";
        }
        if (!password) {
          return "请输入密码";
        }
        if (this.isRegisterMode) {
          if (password.length < 6) {
            return "密码长度不能少于 6 位";
          }
          if (password !== String(this.confirmPassword || "")) {
            return "两次输入的密码不一致";
          }
        }
        return "";
      },
      async submitAuth() {
        const validationError = this.validateForm();
        if (validationError) {
          this.errorMessage = validationError;
          return;
        }
        this.errorMessage = "";
        this.loading = true;
        try {
          const payload = {
            email: this.normalizeEmail(this.email),
            password: String(this.password || "")
          };
          const response = this.isRegisterMode ? await register(payload) : await login(payload);
          saveAuthSession(response);
          relaunchTo("/views/projects/index");
        } catch (error) {
          this.errorMessage = this.formatAuthError(
            error,
            this.isRegisterMode ? "注册失败，请稍后重试" : "登录失败，请稍后重试"
          );
        } finally {
          this.loading = false;
        }
      }
    }
  };
  function _sfc_render$7(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_u__input = resolveEasycom(vue.resolveDynamicComponent("u--input"), __easycom_0$1);
    const _component_u_button = resolveEasycom(vue.resolveDynamicComponent("u-button"), __easycom_0);
    return vue.openBlock(), vue.createElementBlock("view", { class: "auth-page" }, [
      vue.createElementVNode("view", { class: "auth-page__bg" }),
      vue.createElementVNode("view", { class: "auth-page__glow auth-page__glow--1" }),
      vue.createElementVNode("view", { class: "auth-page__glow auth-page__glow--2" }),
      vue.createElementVNode("view", { class: "auth-shell" }, [
        vue.createElementVNode("view", { class: "auth-card" }, [
          vue.createElementVNode("view", { class: "auth-brand" }, [
            vue.createElementVNode("view", { class: "auth-brand__badge" }, "AI"),
            vue.createElementVNode("view", { class: "auth-brand__text" }, [
              vue.createElementVNode("text", { class: "auth-brand__title" }, "动漫创作平台"),
              vue.createElementVNode("text", { class: "auth-brand__desc" }, "从项目创建到视频导出的一站式工作流")
            ])
          ]),
          vue.createElementVNode("view", { class: "auth-header" }, [
            vue.createElementVNode(
              "text",
              { class: "auth-title" },
              vue.toDisplayString($options.isRegisterMode ? "创建账号" : "欢迎回来"),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "text",
              { class: "auth-subtitle" },
              vue.toDisplayString($options.isRegisterMode ? "注册后即可开始创建项目、生成剧本与管理导出任务" : "登录你的账号，继续你的动漫创作工作台"),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "mode-row" }, [
            vue.createElementVNode(
              "view",
              {
                class: vue.normalizeClass(["mode-chip", { active: !$options.isRegisterMode }]),
                onClick: _cache[0] || (_cache[0] = ($event) => $options.switchMode("login"))
              },
              [
                vue.createElementVNode("text", null, "登录")
              ],
              2
              /* CLASS */
            ),
            vue.createElementVNode(
              "view",
              {
                class: vue.normalizeClass(["mode-chip", { active: $options.isRegisterMode }]),
                onClick: _cache[1] || (_cache[1] = ($event) => $options.switchMode("register"))
              },
              [
                vue.createElementVNode("text", null, "注册")
              ],
              2
              /* CLASS */
            )
          ]),
          vue.createElementVNode("view", { class: "form-stack" }, [
            vue.createElementVNode("view", { class: "form-group" }, [
              vue.createElementVNode("text", { class: "form-label" }, "邮箱地址"),
              vue.createElementVNode("view", { class: "input-shell" }, [
                vue.createElementVNode("text", { class: "input-icon" }, "✉"),
                vue.createVNode(_component_u__input, {
                  modelValue: $data.email,
                  "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.email = $event),
                  placeholder: "请输入邮箱地址",
                  maxlength: 254,
                  "confirm-type": "next",
                  clearable: "",
                  border: "none",
                  inputAlign: "left"
                }, null, 8, ["modelValue"])
              ])
            ]),
            vue.createElementVNode("view", { class: "form-group" }, [
              vue.createElementVNode("text", { class: "form-label" }, "密码"),
              vue.createElementVNode("view", { class: "input-shell" }, [
                vue.createElementVNode("text", { class: "input-icon" }, "•"),
                vue.createVNode(_component_u__input, {
                  modelValue: $data.password,
                  "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.password = $event),
                  type: "password",
                  placeholder: "请输入密码",
                  maxlength: 128,
                  "confirm-type": "done",
                  clearable: "",
                  border: "none",
                  inputAlign: "left",
                  onConfirm: $options.submitAuth
                }, null, 8, ["modelValue", "onConfirm"])
              ])
            ]),
            $options.isRegisterMode ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "form-group"
            }, [
              vue.createElementVNode("text", { class: "form-label" }, "确认密码"),
              vue.createElementVNode("view", { class: "input-shell" }, [
                vue.createElementVNode("text", { class: "input-icon" }, "•"),
                vue.createVNode(_component_u__input, {
                  modelValue: $data.confirmPassword,
                  "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.confirmPassword = $event),
                  type: "password",
                  placeholder: "请再次输入密码",
                  maxlength: 128,
                  "confirm-type": "done",
                  clearable: "",
                  border: "none",
                  inputAlign: "left",
                  onConfirm: $options.submitAuth
                }, null, 8, ["modelValue", "onConfirm"])
              ])
            ])) : vue.createCommentVNode("v-if", true)
          ]),
          $data.errorMessage ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "notice-card notice-card--error"
          }, [
            vue.createElementVNode("text", { class: "notice-icon" }, "!"),
            vue.createElementVNode(
              "text",
              { class: "notice-text" },
              vue.toDisplayString($data.errorMessage),
              1
              /* TEXT */
            )
          ])) : vue.createCommentVNode("v-if", true),
          vue.createVNode(_component_u_button, {
            class: "auth-btn",
            type: "primary",
            loading: $options.buttonLoading,
            onClick: $options.submitAuth
          }, {
            default: vue.withCtx(() => [
              vue.createTextVNode(
                vue.toDisplayString($options.buttonText),
                1
                /* TEXT */
              )
            ]),
            _: 1
            /* STABLE */
          }, 8, ["loading", "onClick"]),
          vue.createElementVNode("view", { class: "mode-hint" }, [
            vue.createElementVNode(
              "text",
              null,
              vue.toDisplayString($options.isRegisterMode ? "已有账号？" : "还没有账号？"),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "text",
              {
                class: "mode-link",
                onClick: _cache[5] || (_cache[5] = ($event) => $options.switchMode($options.isRegisterMode ? "login" : "register"))
              },
              vue.toDisplayString($options.isRegisterMode ? "立即登录" : "立即注册"),
              1
              /* TEXT */
            )
          ])
        ])
      ])
    ]);
  }
  const ViewsAccountIndex = /* @__PURE__ */ _export_sfc(_sfc_main$8, [["render", _sfc_render$7], ["__scopeId", "data-v-626d5ac4"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/account/index.vue"]]);
  const _sfc_main$7 = {
    name: "LoadingProgress",
    props: {
      visible: {
        type: Boolean,
        default: false
      },
      label: {
        type: String,
        default: ""
      },
      value: {
        type: Number,
        default: 0
      }
    },
    computed: {
      safeValue() {
        const value = Number(this.value);
        if (!Number.isFinite(value)) {
          return 0;
        }
        if (value < 0) {
          return 0;
        }
        if (value > 100) {
          return 100;
        }
        return Math.round(value);
      }
    }
  };
  function _sfc_render$6(_ctx, _cache, $props, $setup, $data, $options) {
    return $props.visible ? (vue.openBlock(), vue.createElementBlock("view", {
      key: 0,
      class: "loading-progress"
    }, [
      vue.createElementVNode("view", { class: "loading-progress__panel" }, [
        vue.createElementVNode("view", { class: "loading-progress__header" }, [
          vue.createElementVNode(
            "text",
            { class: "loading-progress__label" },
            vue.toDisplayString($props.label || "正在处理"),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            { class: "loading-progress__value" },
            vue.toDisplayString($options.safeValue) + "%",
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "loading-progress__track" }, [
          vue.createElementVNode(
            "view",
            {
              class: "loading-progress__bar",
              style: vue.normalizeStyle({ width: `${$options.safeValue}%` })
            },
            null,
            4
            /* STYLE */
          )
        ])
      ])
    ])) : vue.createCommentVNode("v-if", true);
  }
  const LoadingProgress = /* @__PURE__ */ _export_sfc(_sfc_main$7, [["render", _sfc_render$6], ["__scopeId", "data-v-7b58255d"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/components/LoadingProgress.vue"]]);
  function listProjects() {
    return http.get("/api/projects");
  }
  function createProject(payload) {
    return http.post("/api/projects", payload);
  }
  function getProject(projectId) {
    return http.get(`/api/projects/${encodeURIComponent(projectId)}`);
  }
  function updateProject(projectId, payload) {
    return http.put(`/api/projects/${encodeURIComponent(projectId)}`, payload);
  }
  function parseScript(payload) {
    return http.post("/api/parse-script", payload, { timeout: 6e5 });
  }
  function enhancePrompt(payload) {
    return http.post("/api/enhance-prompt", payload);
  }
  function generateCharacter(payload) {
    return http.post("/api/generate-character", payload, { timeout: 6e5 });
  }
  function generateScene(payload) {
    return http.post("/api/generate-scene", payload, { timeout: 6e5 });
  }
  function generateVideo(payload) {
    return http.post("/api/generate-video", payload, { timeout: 6e5 });
  }
  function queryVideoTask(taskId, params = {}) {
    return http.get(`/api/generate-video/tasks/${encodeURIComponent(taskId)}`, params);
  }
  const EMPTY_SCRIPT = {
    input: "",
    duration: "3min",
    result: null
  };
  function deepCopy(value, fallback = null) {
    if (value === void 0) {
      return fallback;
    }
    try {
      return JSON.parse(JSON.stringify(value));
    } catch (error) {
      return fallback;
    }
  }
  function safeText$4(value) {
    return String(value || "").trim();
  }
  function normalizeEpisodeNo(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 1;
  }
  function normalizeVideoProvider(value) {
    const provider = safeText$4(value).toLowerCase();
    if (provider === "jimeng") {
      return "jimeng";
    }
    if (provider === "grsai") {
      return "grsai";
    }
    return "openai";
  }
  function hashText(text) {
    const source = String(text || "");
    let hash = 0;
    for (let index = 0; index < source.length; index += 1) {
      hash = (hash << 5) - hash + source.charCodeAt(index) | 0;
    }
    return Math.abs(hash).toString(36);
  }
  function classifyAssetKind(asset) {
    const safeAsset = asset && typeof asset === "object" ? asset : {};
    const typeText = [
      safeAsset.asset_kind,
      safeAsset.assetKind,
      safeAsset.type,
      safeAsset.asset_type,
      safeAsset.category
    ].map((item) => safeText$4(item).toLowerCase()).join(" ");
    const contentText = [safeAsset.name, safeAsset.prompt, safeAsset.source_description].map((item) => safeText$4(item).toLowerCase()).join(" ");
    if (/character|角色/.test(typeText) || /角色/.test(contentText) || safeText$4(safeAsset.wardrobe)) {
      return "character";
    }
    if (/scene|场景|环境/.test(typeText) || /场景|环境/.test(contentText)) {
      return "scene";
    }
    return "";
  }
  function normalizeAssetEntry(asset, index = 0) {
    const safeAsset = asset && typeof asset === "object" ? { ...asset } : {};
    const assetKind = classifyAssetKind(safeAsset);
    if (assetKind) {
      safeAsset.asset_kind = assetKind;
    }
    const explicitId = safeText$4(safeAsset.id || safeAsset.asset_id);
    if (explicitId) {
      safeAsset.id = explicitId;
      return safeAsset;
    }
    const seed = [
      safeText$4(safeAsset.type),
      safeText$4(safeAsset.name),
      safeText$4(safeAsset.image_url),
      safeText$4(safeAsset.prompt),
      String(index)
    ].join("|");
    safeAsset.id = `asset_${hashText(seed)}`;
    return safeAsset;
  }
  function normalizeAssetList(list) {
    if (!Array.isArray(list)) {
      return [];
    }
    return list.map((item, index) => normalizeAssetEntry(item, index));
  }
  function createEmptyShot(index = 1) {
    return {
      sceneNo: index,
      title: `场次 ${index}`,
      duration: "5s",
      sourceDescription: "",
      shotSummary: "",
      detailedShotDescription: "",
      detailedPlot: "",
      dialogueDetails: "",
      actionDetails: "",
      shotDeployment: "",
      prompt: "",
      startFrame: {
        description: "",
        enhanced_prompt: "",
        image_url: ""
      },
      endFrame: {
        description: "",
        enhanced_prompt: "",
        image_url: ""
      },
      videoUrl: "",
      videoTask: {
        taskId: "",
        status: "",
        message: "",
        progress: 0,
        provider: "",
        reqKey: "",
        queryUrl: "",
        queryMethod: ""
      },
      includeInFinal: true,
      notes: ""
    };
  }
  function ensureEpisodeState(episodeScripts, episodeShots, episodeNo) {
    const key = String(normalizeEpisodeNo(episodeNo));
    if (!episodeScripts[key] || typeof episodeScripts[key] !== "object") {
      episodeScripts[key] = {
        script: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
        history: []
      };
    }
    if (!episodeScripts[key].script || typeof episodeScripts[key].script !== "object") {
      episodeScripts[key].script = deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT });
    }
    if (!Array.isArray(episodeScripts[key].history)) {
      episodeScripts[key].history = [];
    }
    if (!Array.isArray(episodeShots[key])) {
      episodeShots[key] = [];
    }
    return key;
  }
  function formatDialogueBeatItem(item, index = 0) {
    if (!item || typeof item !== "object") {
      return safeText$4(item);
    }
    const beatId = safeText$4(item.beat_id || item.id || index + 1);
    const speaker = safeText$4(item.speaker || item.role || `角色${index + 1}`);
    const line = safeText$4(item.line || item.dialogue);
    const tone = safeText$4(item.tone);
    const reaction = safeText$4(item.reaction);
    const parts = [];
    if (speaker || line) {
      parts.push(`${speaker}${line ? `：${line}` : ""}`);
    }
    if (tone) {
      parts.push(`语气:${tone}`);
    }
    if (reaction) {
      parts.push(`反应:${reaction}`);
    }
    const content = parts.join(" | ").trim();
    return content ? `${beatId}. ${content}` : "";
  }
  function findSceneDialogueBeat(scene, beatId = "", beatIndex = 0) {
    const beats = Array.isArray(scene && scene.dialogue_beats) ? scene.dialogue_beats : [];
    if (!beats.length) {
      return null;
    }
    const normalizedBeatId = safeText$4(beatId);
    if (normalizedBeatId) {
      const matched = beats.find((item) => safeText$4(item && (item.beat_id || item.id)) === normalizedBeatId);
      if (matched) {
        return matched;
      }
    }
    return beats[beatIndex] || null;
  }
  function formatShotPlanItem(item, index = 0) {
    if (!item || typeof item !== "object") {
      return safeText$4(item);
    }
    const beatId = safeText$4(item.beat_id || item.id || index + 1);
    const shotType = safeText$4(item.shot_type || item.lens || item.framing);
    const cameraAngle = safeText$4(item.camera_angle || item.angle);
    const cameraMovement = safeText$4(item.camera_movement || item.movement);
    const blocking = safeText$4(item.blocking || item.beat || item.description || item.action || item);
    const dialogue = safeText$4(item.dialogue || item.line);
    const duration = safeText$4(item.duration);
    const lensPart = [shotType, cameraAngle, cameraMovement].filter(Boolean).join(" / ");
    let line = `${beatId}. ${lensPart ? `${lensPart}：` : ""}${blocking || "镜头推进"}`;
    if (dialogue) {
      line += ` | 台词:${dialogue}`;
    }
    if (duration) {
      line += ` | ${duration}`;
    }
    return line;
  }
  function buildSceneStagingNotes(scene) {
    const explicit = safeText$4(scene && scene.staging_notes);
    if (explicit) {
      return explicit;
    }
    const plan = Array.isArray(scene && scene.shot_plan) ? scene.shot_plan : [];
    return plan.slice(0, 6).map((item, index) => formatShotPlanItem(item, index)).filter(Boolean).join("\n");
  }
  function buildSceneActionDetails(scene) {
    const explicit = safeText$4(scene && scene.action_details);
    if (explicit) {
      return explicit;
    }
    const actions = Array.isArray(scene && scene.character_actions) ? scene.character_actions : [];
    return actions.map((item) => safeText$4(item)).filter(Boolean).join("\n");
  }
  function buildSceneDialogueBeatDetails(scene) {
    const explicit = safeText$4(scene && scene.dialogue_beat_details);
    if (explicit) {
      return explicit;
    }
    const beats = Array.isArray(scene && scene.dialogue_beats) ? scene.dialogue_beats : [];
    return beats.slice(0, 6).map((item, index) => formatDialogueBeatItem(item, index)).filter(Boolean).join("\n");
  }
  function buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex = 0) {
    const safeBeat = beat && typeof beat === "object" ? beat : {};
    const beatId = safeText$4(safeBeat.beat_id || safeBeat.id || beatIndex + 1) || String(beatIndex + 1);
    const shotType = safeText$4(safeBeat.shot_type || safeBeat.lens || safeBeat.framing);
    const cameraAngle = safeText$4(safeBeat.camera_angle || safeBeat.angle);
    const cameraMovement = safeText$4(safeBeat.camera_movement || safeBeat.movement);
    const blocking = safeText$4(safeBeat.blocking || safeBeat.beat || safeBeat.description || safeBeat.action || beat);
    const dialogue = safeText$4(safeBeat.dialogue || safeBeat.line);
    const transition = safeText$4(safeBeat.transition);
    const duration = safeText$4(safeBeat.duration);
    const sourceDescription = safeText$4(scene && scene.description);
    const sceneShotSummary = safeText$4(scene && scene.shot_description);
    const lensSummary = [shotType, cameraAngle, cameraMovement].filter(Boolean).join(" / ");
    const dialogueBeat = findSceneDialogueBeat(scene, beatId, beatIndex);
    const dialogueBeatLine = dialogueBeat ? formatDialogueBeatItem(dialogueBeat, beatIndex).replace(/^\d+\.\s*/, "").trim() : "";
    const sceneActionLine = Array.isArray(scene && scene.character_actions) ? safeText$4(scene.character_actions[beatIndex]) : "";
    const shotDeployment = formatShotPlanItem(safeBeat, beatIndex) || [lensSummary, blocking].filter(Boolean).join("：");
    const actionDetails = [blocking, sceneActionLine].filter(Boolean).join("\n");
    const dialogueDetails = [dialogue, dialogueBeatLine].filter(Boolean).join("；");
    const dialogueBeatDetails = dialogueBeat ? formatDialogueBeatItem(dialogueBeat, beatIndex) : dialogue ? `${beatId}. ${dialogue}` : "";
    const shotSummary = lensSummary || sceneShotSummary || `镜头 ${beatId}`;
    const detailedShotDescription = [
      shotSummary && `镜头设计：${shotSummary}`,
      blocking && `当前动作：${blocking}`,
      dialogue && `对白重点：${dialogue}`,
      transition && `镜头衔接：${transition}`
    ].filter(Boolean).join("，") || blocking || shotSummary || sourceDescription;
    const detailedPlot = [
      shotDeployment ? `分镜调度：
${shotDeployment}` : "",
      actionDetails ? `动作细节：
${actionDetails}` : "",
      dialogueDetails ? `对白细节：
${dialogueDetails}` : "",
      dialogueBeatDetails ? `对白节拍：
${dialogueBeatDetails}` : ""
    ].filter(Boolean).join("\n\n");
    return {
      ...createEmptyShot(sceneNo),
      sceneNo,
      title: `场次 ${sceneNo} · 镜头 ${beatId}`,
      duration: duration || safeText$4(scene && scene.duration) || "5s",
      sourceDescription,
      shotSummary,
      detailedShotDescription,
      detailedPlot,
      dialogueDetails,
      actionDetails,
      shotDeployment,
      startFrame: {
        description: [shotSummary, blocking].filter(Boolean).join("，") || detailedShotDescription,
        enhanced_prompt: "",
        image_url: ""
      },
      endFrame: {
        description: "",
        enhanced_prompt: "",
        image_url: ""
      }
    };
  }
  function buildShotFromScene(scene, fallbackIndex = 1) {
    const sceneNo = safeText$4(scene && scene.scene_id) || String(fallbackIndex);
    const sourceDescription = safeText$4(scene && scene.description);
    const shotSummary = safeText$4(scene && scene.shot_description);
    const detailedShotDescription = safeText$4(scene && (scene.detailed_shot_description || shotSummary || sourceDescription));
    const dialogueDetails = safeText$4(
      scene && (scene.dialogue_details || (Array.isArray(scene.dialogue) ? scene.dialogue.map((item) => safeText$4(item)).filter(Boolean).join("；") : "")) || ""
    );
    const shotDeployment = buildSceneStagingNotes(scene);
    const actionDetails = buildSceneActionDetails(scene);
    const dialogueBeatDetails = buildSceneDialogueBeatDetails(scene);
    const detailedPlot = [
      shotDeployment ? `分镜调度：
${shotDeployment}` : "",
      actionDetails ? `动作细节：
${actionDetails}` : "",
      dialogueDetails ? `对白细节：
${dialogueDetails}` : "",
      dialogueBeatDetails ? `对白节拍：
${dialogueBeatDetails}` : ""
    ].filter(Boolean).join("\n\n");
    return {
      ...createEmptyShot(Number(sceneNo) || fallbackIndex),
      sceneNo,
      title: `场次 ${sceneNo}`,
      duration: safeText$4(scene && scene.duration) || "5s",
      sourceDescription,
      shotSummary,
      detailedShotDescription,
      detailedPlot,
      dialogueDetails,
      actionDetails,
      shotDeployment,
      startFrame: {
        description: detailedShotDescription,
        enhanced_prompt: "",
        image_url: ""
      },
      endFrame: {
        description: "",
        enhanced_prompt: "",
        image_url: ""
      }
    };
  }
  function buildShotsFromScene(scene, fallbackIndex = 1) {
    const plan = Array.isArray(scene && scene.shot_plan) ? scene.shot_plan.filter(Boolean) : [];
    const sceneNo = safeText$4(scene && scene.scene_id) || String(fallbackIndex);
    if (plan.length) {
      return plan.map((beat, beatIndex) => buildShotFromPlanBeat(scene, sceneNo, beat, beatIndex));
    }
    return [buildShotFromScene(scene, fallbackIndex)];
  }
  function buildShotsFromScenes(scenes) {
    if (!Array.isArray(scenes)) {
      return [];
    }
    return scenes.reduce((result, scene, index) => result.concat(buildShotsFromScene(scene, index + 1)), []);
  }
  function createDefaultProjectState() {
    return {
      currentProjectId: "",
      currentProjectName: "",
      currentScriptTitle: "",
      currentEpisodeNo: 1,
      videoProvider: "openai",
      assets: [],
      shots: [],
      generatedData: [],
      lastScript: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
      scriptHistory: [],
      episodeScripts: {
        "1": {
          script: deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
          history: []
        }
      },
      episodeShots: {
        "1": []
      }
    };
  }
  function applyProject(project) {
    const state = createDefaultProjectState();
    const safeProject = project && typeof project === "object" ? project : {};
    state.currentProjectId = safeText$4(safeProject.id);
    state.currentProjectName = safeText$4(safeProject.name);
    state.currentScriptTitle = safeText$4(safeProject.script_title);
    state.currentEpisodeNo = normalizeEpisodeNo(safeProject.episode_no);
    state.videoProvider = normalizeVideoProvider(safeProject.video_provider);
    state.assets = normalizeAssetList(safeProject.assets);
    state.generatedData = Array.isArray(safeProject.generated_data) ? deepCopy(safeProject.generated_data, []) : [];
    const incomingEpisodeScripts = safeProject.episode_scripts && typeof safeProject.episode_scripts === "object" ? safeProject.episode_scripts : {};
    const incomingEpisodeShots = safeProject.episode_shots && typeof safeProject.episode_shots === "object" ? safeProject.episode_shots : {};
    state.episodeScripts = {};
    Object.keys(incomingEpisodeScripts).forEach((key2) => {
      const entry = incomingEpisodeScripts[key2] || {};
      state.episodeScripts[String(key2)] = {
        script: entry.script && typeof entry.script === "object" ? {
          input: safeText$4(entry.script.input),
          duration: safeText$4(entry.script.duration) || "3min",
          result: deepCopy(entry.script.result, null)
        } : deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
        history: Array.isArray(entry.history) ? deepCopy(entry.history, []) : []
      };
    });
    state.episodeShots = {};
    Object.keys(incomingEpisodeShots).forEach((key2) => {
      state.episodeShots[String(key2)] = Array.isArray(incomingEpisodeShots[key2]) ? deepCopy(incomingEpisodeShots[key2], []) : [];
    });
    if (!Object.keys(state.episodeScripts).length) {
      const fallbackKey = String(state.currentEpisodeNo);
      state.episodeScripts[fallbackKey] = {
        script: {
          input: safeText$4(safeProject.script && safeProject.script.input),
          duration: safeText$4(safeProject.script && safeProject.script.duration) || "3min",
          result: deepCopy(safeProject.script && safeProject.script.result, null)
        },
        history: Array.isArray(safeProject.history) ? deepCopy(safeProject.history, []) : []
      };
    }
    if (!Object.keys(state.episodeShots).length) {
      state.episodeShots[String(state.currentEpisodeNo)] = Array.isArray(safeProject.shots) ? deepCopy(safeProject.shots, []) : [];
    }
    const key = ensureEpisodeState(state.episodeScripts, state.episodeShots, state.currentEpisodeNo);
    const episodeState = state.episodeScripts[key];
    state.lastScript = {
      input: safeText$4(episodeState.script && episodeState.script.input),
      duration: safeText$4(episodeState.script && episodeState.script.duration) || "3min",
      result: deepCopy(episodeState.script && episodeState.script.result, null)
    };
    state.scriptHistory = Array.isArray(episodeState.history) ? deepCopy(episodeState.history, []) : [];
    state.shots = Array.isArray(state.episodeShots[key]) ? deepCopy(state.episodeShots[key], []) : [];
    return state;
  }
  function buildProjectPayload(state) {
    const episodeScripts = deepCopy(state.episodeScripts, {}) || {};
    const episodeShots = deepCopy(state.episodeShots, {}) || {};
    const key = ensureEpisodeState(episodeScripts, episodeShots, state.currentEpisodeNo);
    episodeScripts[key] = {
      script: {
        input: safeText$4(state.lastScript && state.lastScript.input),
        duration: safeText$4(state.lastScript && state.lastScript.duration) || "3min",
        result: deepCopy(state.lastScript && state.lastScript.result, null)
      },
      history: Array.isArray(state.scriptHistory) ? deepCopy(state.scriptHistory, []) : []
    };
    episodeShots[key] = Array.isArray(state.shots) ? deepCopy(state.shots, []) : [];
    return {
      name: safeText$4(state.currentProjectName) || "未命名项目",
      script_title: safeText$4(state.currentScriptTitle),
      episode_no: normalizeEpisodeNo(state.currentEpisodeNo),
      video_provider: normalizeVideoProvider(state.videoProvider),
      assets: normalizeAssetList(state.assets),
      shots: episodeShots[key] || [],
      history: episodeScripts[key].history || [],
      generated_data: Array.isArray(state.generatedData) ? deepCopy(state.generatedData, []) : [],
      script: episodeScripts[key].script || deepCopy(EMPTY_SCRIPT, { ...EMPTY_SCRIPT }),
      episode_scripts: episodeScripts,
      episode_shots: episodeShots
    };
  }
  function listEpisodeOptions(state) {
    const set = /* @__PURE__ */ new Set();
    Object.keys(state && state.episodeScripts || {}).forEach((key) => {
      set.add(normalizeEpisodeNo(key));
    });
    Object.keys(state && state.episodeShots || {}).forEach((key) => {
      set.add(normalizeEpisodeNo(key));
    });
    set.add(normalizeEpisodeNo(state && state.currentEpisodeNo));
    if (!set.size) {
      set.add(1);
    }
    return [...set].sort((left, right) => left - right);
  }
  async function loadCurrentProject(options = {}) {
    const projectId = options.projectId || getCurrentProjectId();
    if (!projectId) {
      return null;
    }
    if (!options.forceRemote) {
      const cache = getProjectCache();
      if (cache && cache.id === projectId) {
        return cache;
      }
    }
    const project = await getProject(projectId);
    saveProjectCache(project);
    return project;
  }
  async function saveCurrentProjectState(state) {
    const projectId = state.currentProjectId || getCurrentProjectId();
    if (!projectId) {
      throw new Error("请先选择项目");
    }
    const payload = buildProjectPayload(state);
    const updated = await updateProject(projectId, payload);
    const merged = {
      ...payload,
      ...updated,
      id: projectId
    };
    saveProjectCache(merged);
    return merged;
  }
  const CREATE_TABS = [
    { key: "project", label: "项目" },
    { key: "script", label: "剧本" },
    { key: "assets", label: "资产" },
    { key: "director", label: "导演" }
  ];
  const PROVIDER_OPTIONS = [
    { value: "openai", label: "通用接口" },
    { value: "jimeng", label: "即梦接口" },
    { value: "grsai", label: "第三方接口" }
  ];
  const DURATION_OPTIONS = [
    { value: "30s", label: "30 秒预告" },
    { value: "3min", label: "3 分钟短剧" },
    { value: "5min", label: "5 分钟短剧" },
    { value: "custom", label: "自定义" }
  ];
  const WARDROBE_OPTIONS = ["日常", "战斗", "礼服", "特写", "自定义"];
  const ASSET_FILTERS = [{ value: "all", label: "全部" }, { value: "character", label: "角色" }, { value: "scene", label: "场景" }];
  function clone$1(value, fallback) {
    try {
      return JSON.parse(JSON.stringify(value));
    } catch (error) {
      return fallback;
    }
  }
  function safeText$3(value) {
    return String(value || "").trim();
  }
  const _sfc_main$6 = {
    components: { LoadingProgress, UButton: __easycom_0 },
    data() {
      return {
        ...createDefaultProjectState(),
        initialized: false,
        createTabs: CREATE_TABS,
        providerOptions: PROVIDER_OPTIONS,
        durationOptions: DURATION_OPTIONS,
        wardrobeOptions: WARDROBE_OPTIONS,
        assetFilters: ASSET_FILTERS,
        activeCreateTab: "project",
        projects: [],
        loading: false,
        creating: false,
        projectName: "",
        scriptTitle: "",
        selectedEpisode: 1,
        episodeChoices: Array.from({ length: 24 }, (_, index) => index + 1),
        activeProjectCache: null,
        progress: { visible: false, value: 0, label: "" },
        progressTimer: null,
        progressHideTimer: null,
        saving: false,
        parsing: false,
        scriptInput: "",
        scriptResult: null,
        rawResultText: "",
        targetDuration: "3min",
        customDuration: "",
        errorMessage: "",
        assetFilter: "all",
        characterLoading: false,
        characterEnhancing: false,
        sceneLoading: false,
        sceneEnhancing: false,
        extractingCharacters: false,
        extractingScenes: false,
        recommendActionMessage: "",
        recommendMessageTimer: null,
        currentCharacter: { name: "", description: "", wardrobe: "日常", customWardrobe: "", prompt: "" },
        currentScene: { name: "", description: "", prompt: "" },
        selectedShotIndex: -1,
        shotEnhancing: false,
        frameLoadingKey: "",
        videoLoading: false,
        pollTimers: {}
      };
    },
    computed: {
      hasProject() {
        return Boolean(this.currentProjectId);
      },
      episodeChoiceIndex() {
        const choices = Array.isArray(this.episodeChoices) ? this.episodeChoices : [];
        const index = choices.findIndex((item) => item === this.selectedEpisode);
        return index >= 0 ? index : 0;
      },
      episodeOptions() {
        return listEpisodeOptions(this);
      },
      episodeIndex() {
        const index = this.episodeOptions.findIndex((item) => item === this.currentEpisodeNo);
        return index >= 0 ? index : 0;
      },
      providerLabels() {
        const options = Array.isArray(this.providerOptions) ? this.providerOptions : [];
        return options.map((item) => item.label);
      },
      providerIndex() {
        const options = Array.isArray(this.providerOptions) ? this.providerOptions : [];
        const index = options.findIndex((item) => item.value === this.videoProvider);
        return index >= 0 ? index : 0;
      },
      durationLabels() {
        const options = Array.isArray(this.durationOptions) ? this.durationOptions : [];
        return options.map((item) => item.label);
      },
      durationIndex() {
        const options = Array.isArray(this.durationOptions) ? this.durationOptions : [];
        const index = options.findIndex((item) => item.value === this.targetDuration);
        return index >= 0 ? index : 0;
      },
      sceneRows() {
        return this.scriptResult && Array.isArray(this.scriptResult.scenes) ? this.scriptResult.scenes : [];
      },
      storyPackage() {
        return this.scriptResult && this.scriptResult.story_package && typeof this.scriptResult.story_package === "object" ? this.scriptResult.story_package : {};
      },
      hasScriptInput() {
        return Boolean(safeText$3(this.scriptInput) || safeText$3(this.lastScript && this.lastScript.input));
      },
      characterAssets() {
        return (Array.isArray(this.assets) ? this.assets : []).filter((item) => safeText$3(item && item.asset_kind).toLowerCase() === "character");
      },
      sceneAssets() {
        return (Array.isArray(this.assets) ? this.assets : []).filter((item) => safeText$3(item && item.asset_kind).toLowerCase() === "scene");
      },
      characterCandidates() {
        let list = Array.isArray(this.storyPackage.character_bible) ? this.storyPackage.character_bible : [];
        if (!list.length) {
          list = this.inferCharacterBibleFromScenes(this.sceneRows);
        }
        return list.map((item, index) => {
          const safe = item && typeof item === "object" ? item : {};
          return {
            id: safeText$3(safe.name) || String(index + 1),
            name: safeText$3(safe.name) || `角色${index + 1}`,
            role: safeText$3(safe.role),
            goal: safeText$3(safe.goal),
            tension: safeText$3(safe.tension),
            voice: safeText$3(safe.voice),
            visualAnchor: safeText$3(safe.visual_anchor || safe.visualAnchor)
          };
        }).filter((item) => item.name);
      },
      recommendedSceneCandidates() {
        return this.sceneRows.map((scene, index) => {
          const sceneId = safeText$3(scene && scene.scene_id) || String(index + 1);
          const row = {
            sceneId,
            name: `场次 ${sceneId}`,
            description: safeText$3(scene && scene.description),
            shotSummary: safeText$3(scene && scene.shot_description),
            detailed: safeText$3(scene && scene.detailed_shot_description),
            duration: safeText$3(scene && scene.duration) || "5s"
          };
          const matchedAssets = this.sceneAssets.filter((asset) => this.isSceneCandidateMatched(row, asset));
          return {
            ...row,
            generated: matchedAssets.length > 0,
            matchedAssets: matchedAssets.map((asset) => safeText$3(asset && asset.name)).filter(Boolean)
          };
        }).filter((item) => item.description || item.shotSummary || item.detailed);
      },
      recommendedCharacterCandidates() {
        return this.characterCandidates.map((item) => {
          const matchedAssets = this.characterAssets.filter((asset) => this.isCharacterCandidateMatched(item, asset));
          return {
            ...item,
            generated: matchedAssets.length > 0,
            matchedAssets: matchedAssets.map((asset) => safeText$3(asset && asset.name)).filter(Boolean)
          };
        });
      },
      hasRecommendationCandidates() {
        return this.recommendedSceneCandidates.length > 0 || this.recommendedCharacterCandidates.length > 0;
      },
      wardrobeIndex() {
        const options = Array.isArray(this.wardrobeOptions) ? this.wardrobeOptions : [];
        const index = options.findIndex((item) => item === this.currentCharacter.wardrobe);
        return index >= 0 ? index : 0;
      },
      filteredAssets() {
        return this.assetFilter === "all" ? this.assets : this.assets.filter((item) => safeText$3(item && item.asset_kind).toLowerCase() === this.assetFilter);
      },
      currentShot() {
        return this.selectedShotIndex >= 0 && this.selectedShotIndex < this.shots.length ? this.shots[this.selectedShotIndex] : null;
      }
    },
    onLoad(options) {
      this.restoreStudioView();
      this.applyLaunchState(options);
    },
    onShow() {
      if (!ensureAuth()) {
        return;
      }
      this.activeProjectCache = getProjectCache();
      this.restoreStudioView();
      if (!this.initialized) {
        this.initializePage();
      }
    },
    onPullDownRefresh() {
      if (!ensureAuth()) {
        uni.stopPullDownRefresh();
        return;
      }
      this.refreshCurrentView();
    },
    onUnload() {
      this.clearProgressTimer();
      if (this.recommendMessageTimer) {
        clearTimeout(this.recommendMessageTimer);
        this.recommendMessageTimer = null;
      }
      Object.keys(this.pollTimers || {}).forEach((key) => this.clearPolling(key));
    },
    methods: {
      showToast(message) {
        uni.showToast({ title: safeText$3(message) || "操作失败", icon: "none" });
      },
      clearProgressTimer() {
        if (this.progressTimer) {
          clearInterval(this.progressTimer);
          this.progressTimer = null;
        }
        if (this.progressHideTimer) {
          clearTimeout(this.progressHideTimer);
          this.progressHideTimer = null;
        }
      },
      startProgress(label) {
        this.clearProgressTimer();
        this.progress = { visible: true, value: 14, label: safeText$3(label) || "正在处理" };
        this.progressTimer = setInterval(() => {
          const currentValue = Number(this.progress.value || 0);
          const delta = currentValue < 60 ? 9 : currentValue < 84 ? 4 : 0;
          this.progress.value = Math.min(currentValue + delta, 90);
        }, 220);
      },
      finishProgress(label) {
        this.clearProgressTimer();
        this.progress.label = safeText$3(label) || this.progress.label || "已完成";
        this.progress.value = 100;
        this.progressHideTimer = setTimeout(() => {
          this.progress.visible = false;
          this.progress.value = 0;
        }, 320);
      },
      async runTask(label, handler, options = {}) {
        this.startProgress(label);
        try {
          const result = await handler();
          this.finishProgress(options.successText || "已完成");
          return result;
        } catch (error) {
          this.finishProgress(safeText$3(error && error.message) || options.failureText || "操作失败");
          throw error;
        }
      },
      persistStudioView() {
        saveStudioView({ mainTab: "create", createTab: this.activeCreateTab });
      },
      restoreStudioView() {
        const view = getStudioView();
        if (!view || typeof view !== "object") {
          return;
        }
        const createTab = safeText$3(view.createTab).toLowerCase();
        if (["project", "script", "assets", "director"].includes(createTab)) {
          this.activeCreateTab = createTab;
        }
      },
      applyLaunchState(options = {}) {
        const panel = safeText$3(options.panel || options.tab).toLowerCase();
        if (["project", "script", "assets", "director"].includes(panel)) {
          this.activeCreateTab = panel;
          this.persistStudioView();
        }
      },
      async initializePage() {
        try {
          await this.runTask("正在同步工作台", async () => {
            await this.fetchProjects();
            if (getCurrentProjectId()) {
              await this.fetchCurrentProject();
            }
          }, { successText: "工作台已就绪" });
          this.initialized = true;
        } catch (error) {
          this.showToast(error.message || "初始化失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      async refreshCurrentView() {
        try {
          await this.runTask("正在刷新工作台", async () => {
            await this.fetchProjects();
            if (this.hasProject || getCurrentProjectId()) {
              await this.fetchCurrentProject(true);
            }
          }, { successText: "工作台已刷新" });
        } catch (error) {
          this.showToast(error.message || "刷新失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      handleCreateTabChange(key) {
        if (!key) {
          return;
        }
        this.activeCreateTab = key;
        this.persistStudioView();
      },
      providerText(value) {
        const target = this.providerOptions.find((item) => item.value === safeText$3(value).toLowerCase());
        return target ? target.label : "通用接口";
      },
      assetCount(project) {
        return Array.isArray(project && project.assets) ? project.assets.length : 0;
      },
      shotCount(project) {
        return Array.isArray(project && project.shots) ? project.shots.length : 0;
      },
      upsertProjectSummary(project) {
        if (!project || !project.id) {
          return;
        }
        const summary = clone$1(project, {});
        const list = Array.isArray(this.projects) ? [...this.projects] : [];
        const index = list.findIndex((item) => String(item && item.id) === String(summary.id));
        if (index >= 0) {
          list.splice(index, 1, { ...list[index], ...summary });
        } else {
          list.unshift(summary);
        }
        this.projects = list;
      },
      resetAssetForms() {
        this.currentCharacter = { name: "", description: "", wardrobe: "日常", customWardrobe: "", prompt: "" };
        this.currentScene = { name: "", description: "", prompt: "" };
      },
      normalizeShot(shot, index = 0) {
        const safeShot = shot && typeof shot === "object" ? clone$1(shot, {}) : {};
        const defaults = createEmptyShot(index + 1);
        return { ...defaults, ...safeShot, title: safeText$3(safeShot.title) || `镜头 ${index + 1}`, duration: safeText$3(safeShot.duration) || "5s", startFrame: { ...defaults.startFrame, ...safeShot.startFrame || {} }, endFrame: { ...defaults.endFrame, ...safeShot.endFrame || {} }, videoTask: { ...defaults.videoTask, ...safeShot.videoTask || {} } };
      },
      hydrateProject(project) {
        const next = applyProject(project);
        next.shots = (next.shots || []).map((shot, index) => this.normalizeShot(shot, index));
        Object.assign(this, next);
        this.scriptInput = safeText$3(next.lastScript && next.lastScript.input);
        this.scriptResult = next.lastScript && next.lastScript.result ? next.lastScript.result : null;
        this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : "";
        this.applyDuration(next.lastScript && next.lastScript.duration || "3min");
        this.selectedShotIndex = next.shots.length ? 0 : -1;
        this.activeProjectCache = clone$1(project, {});
        this.errorMessage = "";
        this.resetAssetForms();
      },
      async fetchProjects() {
        const response = await listProjects();
        this.projects = Array.isArray(response) ? response : [];
        this.activeProjectCache = getProjectCache();
        return this.projects;
      },
      async loadProjects(silent = false) {
        this.loading = true;
        try {
          if (silent) {
            await this.fetchProjects();
          } else {
            await this.runTask("正在同步项目列表", () => this.fetchProjects(), { successText: "项目列表已更新" });
          }
        } catch (error) {
          this.showToast(error.message || "加载项目失败");
        } finally {
          this.loading = false;
          uni.stopPullDownRefresh();
        }
      },
      async fetchCurrentProject(forceRemote = false) {
        const project = await loadCurrentProject({ forceRemote });
        if (project) {
          this.hydrateProject(project);
        }
        return project;
      },
      async loadProject(forceRemote = false, silent = false) {
        if (!this.hasProject && !getCurrentProjectId()) {
          return;
        }
        try {
          if (silent) {
            await this.fetchCurrentProject(forceRemote);
          } else {
            await this.runTask("正在同步当前项目", () => this.fetchCurrentProject(forceRemote), { successText: "项目数据已更新" });
          }
        } catch (error) {
          this.showToast(error.message || "加载项目失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      activateProject(project, panel = "project") {
        if (!project || !project.id) {
          return;
        }
        saveProjectCache(project);
        setCurrentProjectId(project.id);
        this.hydrateProject(project);
        this.upsertProjectSummary(project);
        this.activeCreateTab = panel;
        this.persistStudioView();
      },
      async createNewProject() {
        this.creating = true;
        try {
          const detail = await this.runTask("正在创建项目", async () => {
            const created = await createProject({ name: safeText$3(this.projectName) || `项目 ${this.projects.length + 1}`, script_title: safeText$3(this.scriptTitle), episode_no: this.selectedEpisode });
            return getProject(created.id);
          }, { successText: "项目已创建" });
          this.projectName = "";
          this.scriptTitle = "";
          this.selectedEpisode = 1;
          this.activateProject(detail, "script");
        } catch (error) {
          this.showToast(error.message || "创建项目失败");
        } finally {
          this.creating = false;
        }
      },
      async openProject(project, panel = "script") {
        if (!project || !project.id) {
          return;
        }
        try {
          const detail = await this.runTask("正在打开项目", () => getProject(project.id), { successText: "项目已打开" });
          this.activateProject(detail, panel);
        } catch (error) {
          this.showToast(error.message || "打开项目失败");
        }
      },
      openCurrentProject() {
        if (this.activeProjectCache && this.activeProjectCache.id) {
          this.openProject(this.activeProjectCache, "script");
          return;
        }
        this.handleCreateTabChange("project");
      },
      handleEpisodeChange(event) {
        const next = this.episodeChoices[Number(event.detail.value || 0)] || 1;
        this.selectedEpisode = Number(next) || 1;
      },
      persistCurrentEpisodeState() {
        const key = ensureEpisodeState(this.episodeScripts, this.episodeShots, this.currentEpisodeNo);
        this.lastScript = { input: safeText$3(this.scriptInput), duration: this.resolveDurationText() || "3min", result: this.scriptResult || null };
        this.episodeScripts[key] = { script: clone$1(this.lastScript, { ...this.lastScript }), history: clone$1(this.scriptHistory, []) };
        this.episodeShots[key] = clone$1(this.shots, []);
      },
      restoreCurrentEpisodeState() {
        const key = ensureEpisodeState(this.episodeScripts, this.episodeShots, this.currentEpisodeNo);
        const episodeState = this.episodeScripts[key];
        this.lastScript = { input: safeText$3(episodeState.script && episodeState.script.input), duration: safeText$3(episodeState.script && episodeState.script.duration) || "3min", result: clone$1(episodeState.script && episodeState.script.result, null) };
        this.scriptHistory = clone$1(episodeState.history, []);
        this.shots = clone$1(this.episodeShots[key], []).map((shot, index) => this.normalizeShot(shot, index));
        this.scriptInput = this.lastScript.input;
        this.scriptResult = this.lastScript.result;
        this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : "";
        this.applyDuration(this.lastScript.duration);
        this.selectedShotIndex = this.shots.length ? 0 : -1;
      },
      handleCurrentEpisodeChange(event) {
        this.persistCurrentEpisodeState();
        this.currentEpisodeNo = this.episodeOptions[Number(event.detail.value || 0)] || 1;
        this.restoreCurrentEpisodeState();
      },
      handleProviderChange(event) {
        var _a;
        this.videoProvider = ((_a = this.providerOptions[Number(event.detail.value || 0)]) == null ? void 0 : _a.value) || "openai";
      },
      handleDurationChange(event) {
        var _a;
        this.targetDuration = ((_a = this.durationOptions[Number(event.detail.value || 0)]) == null ? void 0 : _a.value) || "3min";
      },
      addEpisode() {
        this.persistCurrentEpisodeState();
        const next = (this.episodeOptions[this.episodeOptions.length - 1] || 1) + 1;
        ensureEpisodeState(this.episodeScripts, this.episodeShots, next);
        this.currentEpisodeNo = next;
        this.restoreCurrentEpisodeState();
        this.showToast(`已切换到第 ${next} 集`);
      },
      applyDuration(value) {
        if (["30s", "3min", "5min"].includes(value)) {
          this.targetDuration = value;
          this.customDuration = "";
          return;
        }
        this.targetDuration = "custom";
        this.customDuration = safeText$3(value);
      },
      resolveDurationText() {
        return this.targetDuration === "custom" ? safeText$3(this.customDuration) : this.targetDuration;
      },
      async persistProjectState(silent = false) {
        const saveAction = async () => {
          this.persistCurrentEpisodeState();
          const updated = await saveCurrentProjectState(this);
          const merged = { ...this.activeProjectCache || {}, ...updated, id: updated.id || this.currentProjectId };
          saveProjectCache(merged);
          this.activeProjectCache = merged;
          this.upsertProjectSummary(merged);
          return merged;
        };
        if (silent) {
          return saveAction();
        }
        this.saving = true;
        try {
          return await this.runTask("正在保存项目", saveAction, { successText: "项目已保存" });
        } finally {
          this.saving = false;
        }
      },
      async saveProject() {
        try {
          await this.persistProjectState(false);
        } catch (error) {
          this.showToast(error.message || "保存失败");
        }
      },
      async parseCurrentScript() {
        const script = safeText$3(this.scriptInput);
        const duration = this.resolveDurationText();
        if (!script) {
          this.errorMessage = "请先输入剧本内容";
          return;
        }
        if (!duration) {
          this.errorMessage = "请先设置目标时长";
          return;
        }
        this.parsing = true;
        this.errorMessage = "";
        try {
          const result = await this.runTask("正在生成分镜脚本", () => parseScript({ script, duration }), { successText: "分镜脚本已生成" });
          this.scriptResult = result;
          this.rawResultText = JSON.stringify(result, null, 2);
          this.lastScript = { input: script, duration, result };
          await this.persistProjectState(true);
        } catch (error) {
          this.errorMessage = error.message || "生成分镜脚本失败";
        } finally {
          this.parsing = false;
        }
      },
      applyEditedResult() {
        try {
          const parsed = JSON.parse(this.rawResultText || "{}");
          this.scriptResult = parsed;
          this.lastScript = { input: safeText$3(this.scriptInput), duration: this.resolveDurationText() || "3min", result: parsed };
          this.persistCurrentEpisodeState();
          this.errorMessage = "";
          this.showToast("结果已应用");
        } catch (error) {
          this.errorMessage = "JSON 格式有误，请检查后再试";
        }
      },
      resetEditedResult() {
        this.rawResultText = this.scriptResult ? JSON.stringify(this.scriptResult, null, 2) : "";
      },
      async syncScenesToShots() {
        if (!this.sceneRows.length) {
          return;
        }
        this.shots = buildShotsFromScenes(this.sceneRows).map((shot, index) => this.normalizeShot(shot, index));
        this.selectedShotIndex = this.shots.length ? 0 : -1;
        await this.persistProjectState(true);
        this.activeCreateTab = "director";
        this.persistStudioView();
        this.showToast("已同步到导演模块");
      },
      setRecommendActionMessage(message) {
        this.recommendActionMessage = safeText$3(message);
        if (this.recommendMessageTimer) {
          clearTimeout(this.recommendMessageTimer);
          this.recommendMessageTimer = null;
        }
        if (!this.recommendActionMessage) {
          return;
        }
        this.recommendMessageTimer = setTimeout(() => {
          this.recommendActionMessage = "";
          this.recommendMessageTimer = null;
        }, 2600);
      },
      normalizeToken(value) {
        return safeText$3(value).toLowerCase().replace(/[\s\-_.:,;'"`~!@#$%^&*(){}\[\]<>?/\\|，。！？、；：“”‘’（）【】《》]/g, "");
      },
      buildAssetSearchText(asset) {
        const safeAsset = asset && typeof asset === "object" ? asset : {};
        return [safeAsset.name, safeAsset.prompt, safeAsset.source_description, safeAsset.type, safeAsset.asset_kind, safeAsset.wardrobe].map((item) => this.normalizeToken(item)).join(" ");
      },
      isCharacterCandidateMatched(candidate, asset) {
        const text = this.buildAssetSearchText(asset);
        if (!text) {
          return false;
        }
        const safeCandidate = candidate && typeof candidate === "object" ? candidate : {};
        const tokens = [this.normalizeToken(safeCandidate.name), this.normalizeToken(safeCandidate.role), this.normalizeToken(String(safeCandidate.visualAnchor || "").slice(0, 10))].filter((token) => token && token.length >= 2);
        return tokens.some((token) => text.includes(token));
      },
      isSceneCandidateMatched(candidate, asset) {
        const text = this.buildAssetSearchText(asset);
        if (!text) {
          return false;
        }
        const safeCandidate = candidate && typeof candidate === "object" ? candidate : {};
        const sceneName = safeText$3(safeCandidate.name).replace(/^场次\s*\d+\s*/, "");
        const tokens = [this.normalizeToken(sceneName), this.normalizeToken(String(safeCandidate.description || "").slice(0, 12)), this.normalizeToken(String(safeCandidate.shotSummary || "").slice(0, 12))].filter((token) => token && token.length >= 2);
        return tokens.some((token) => text.includes(token));
      },
      inferCharacterBibleFromScenes(scenes) {
        const list = [];
        const seen = /* @__PURE__ */ new Set();
        const pushName = (rawName) => {
          const name = safeText$3(rawName);
          if (!name || name.length > 16) {
            return;
          }
          const key = name.toLowerCase();
          if (seen.has(key)) {
            return;
          }
          seen.add(key);
          list.push({ name, role: "待补充", goal: "", tension: "", voice: "", visual_anchor: "" });
        };
        (Array.isArray(scenes) ? scenes : []).forEach((scene) => {
          if (!scene || typeof scene !== "object") {
            return;
          }
          ["dialogue_details", "dialogue_beats"].forEach((key) => {
            const beats = scene[key];
            if (!Array.isArray(beats)) {
              return;
            }
            beats.forEach((beat) => {
              if (beat && typeof beat === "object") {
                pushName(beat.speaker || beat.role || beat.character);
              }
            });
          });
          const dialogueText = safeText$3(scene.dialogue);
          if (!dialogueText) {
            return;
          }
          dialogueText.split("\n").forEach((line) => {
            const match = line.match(/^\s*([^:：\s]{1,12})\s*[:：]/);
            if (match) {
              pushName(match[1]);
            }
          });
        });
        return list;
      },
      sanitizeCharacterBible(items) {
        const seen = /* @__PURE__ */ new Set();
        return (Array.isArray(items) ? items : []).map((item) => item && typeof item === "object" ? item : {}).map((item) => ({ ...item, name: safeText$3(item.name) })).filter((item) => {
          if (!item.name) {
            return false;
          }
          const key = item.name.toLowerCase();
          if (seen.has(key)) {
            return false;
          }
          seen.add(key);
          return true;
        });
      },
      buildMergedResultFromAi(aiResult) {
        const currentResult = this.scriptResult && typeof this.scriptResult === "object" ? clone$1(this.scriptResult, {}) : {};
        const incomingScenes = Array.isArray(aiResult && aiResult.scenes) ? aiResult.scenes : [];
        const incomingStoryPackage = aiResult && aiResult.story_package && typeof aiResult.story_package === "object" ? aiResult.story_package : {};
        const currentStoryPackage = currentResult.story_package && typeof currentResult.story_package === "object" ? currentResult.story_package : {};
        const incomingCharacters = this.sanitizeCharacterBible(incomingStoryPackage.character_bible);
        const currentCharacters = this.sanitizeCharacterBible(currentStoryPackage.character_bible);
        return {
          ...currentResult,
          ...clone$1(aiResult, {}),
          story_package: {
            ...currentStoryPackage,
            ...incomingStoryPackage,
            character_bible: incomingCharacters.length ? incomingCharacters : currentCharacters
          },
          scenes: incomingScenes.length ? incomingScenes : Array.isArray(currentResult.scenes) ? currentResult.scenes : []
        };
      },
      fillSceneFromCandidate(candidate) {
        const safeCandidate = candidate && typeof candidate === "object" ? candidate : {};
        const parts = [safeText$3(safeCandidate.description), safeText$3(safeCandidate.shotSummary), safeText$3(safeCandidate.detailed)].filter(Boolean);
        this.currentScene.name = safeText$3(safeCandidate.name);
        this.currentScene.description = [...new Set(parts)].join("；");
        this.currentScene.prompt = "";
        this.setRecommendActionMessage(`已导入场景：${this.currentScene.name || "未命名场景"}`);
      },
      fillCharacterFromCandidate(candidate) {
        const safeCandidate = candidate && typeof candidate === "object" ? candidate : {};
        const parts = [
          safeText$3(safeCandidate.role) ? `角色定位：${safeText$3(safeCandidate.role)}` : "",
          safeText$3(safeCandidate.goal) ? `目标：${safeText$3(safeCandidate.goal)}` : "",
          safeText$3(safeCandidate.tension) ? `张力：${safeText$3(safeCandidate.tension)}` : "",
          safeText$3(safeCandidate.voice) ? `声音气质：${safeText$3(safeCandidate.voice)}` : "",
          safeText$3(safeCandidate.visualAnchor) ? `视觉锚点：${safeText$3(safeCandidate.visualAnchor)}` : ""
        ].filter(Boolean);
        this.currentCharacter.name = safeText$3(safeCandidate.name);
        this.currentCharacter.description = parts.join("；");
        this.currentCharacter.wardrobe = "日常";
        this.currentCharacter.customWardrobe = "";
        this.currentCharacter.prompt = "";
      },
      importCharacterFromCandidate(candidate, byLongPress = false) {
        this.fillCharacterFromCandidate(candidate);
        const name = safeText$3(candidate && candidate.name) || "未命名角色";
        this.setRecommendActionMessage(byLongPress ? `已长按导入角色：${name}` : `已导入角色：${name}`);
      },
      async runAiExtraction(trigger = "all") {
        const script = safeText$3(this.scriptInput) || safeText$3(this.lastScript && this.lastScript.input);
        const duration = this.resolveDurationText() || safeText$3(this.lastScript && this.lastScript.duration) || "3min";
        if (!script) {
          this.showToast("请先在剧本模块输入并保存剧本");
          return;
        }
        if (trigger === "character") {
          this.extractingCharacters = true;
        } else {
          this.extractingScenes = true;
        }
        try {
          const aiResult = await this.runTask("正在提取角色与场景推荐", () => parseScript({ script, duration }), { successText: "提取完成" });
          const merged = this.buildMergedResultFromAi(aiResult);
          const scenes = Array.isArray(merged.scenes) ? merged.scenes : [];
          const characters = this.sanitizeCharacterBible(merged.story_package && merged.story_package.character_bible);
          if (!scenes.length && !characters.length) {
            this.showToast("未提取到场景或角色，请补充剧本后重试");
            return;
          }
          this.scriptResult = merged;
          this.rawResultText = JSON.stringify(merged, null, 2);
          this.lastScript = { input: script, duration, result: merged };
          await this.persistProjectState(true);
          this.setRecommendActionMessage(`提取完成：场景 ${scenes.length} 个，角色 ${characters.length} 个`);
        } catch (error) {
          this.showToast(error.message || "提取失败");
        } finally {
          this.extractingCharacters = false;
          this.extractingScenes = false;
        }
      },
      async extractCharactersByAi() {
        await this.runAiExtraction("character");
      },
      async extractScenesByAi() {
        await this.runAiExtraction("scene");
      },
      handleWardrobeChange(event) {
        this.currentCharacter.wardrobe = this.wardrobeOptions[Number(event.detail.value || 0)] || "日常";
      },
      assetTypeLabel(asset) {
        return safeText$3(asset && asset.asset_kind).toLowerCase() === "character" ? `角色${safeText$3(asset.wardrobe) ? ` · ${safeText$3(asset.wardrobe)}` : ""}` : "场景";
      },
      normalizedWardrobe() {
        return this.currentCharacter.wardrobe === "自定义" ? safeText$3(this.currentCharacter.customWardrobe) : safeText$3(this.currentCharacter.wardrobe);
      },
      buildCharacterBasePrompt() {
        return [safeText$3(this.currentCharacter.name) ? `角色：${safeText$3(this.currentCharacter.name)}` : "", safeText$3(this.currentCharacter.description), this.normalizedWardrobe() ? `造型：${this.normalizedWardrobe()}` : "", "中国风动画角色设定图，单幅完整构图，人物五官、发型、服装和气质保持稳定统一"].filter(Boolean).join("；");
      },
      buildSceneBasePrompt() {
        return [safeText$3(this.currentScene.name) ? `场景：${safeText$3(this.currentScene.name)}` : "", safeText$3(this.currentScene.description), "中国风动画场景母版图，单幅完整构图，空间关系清晰，禁止拼贴、分屏、文字和水印"].filter(Boolean).join("；");
      },
      async requestEnhance(rawPrompt, context) {
        const response = await enhancePrompt({ prompt: rawPrompt, context });
        return safeText$3(response && response.enhanced_prompt) || safeText$3(rawPrompt);
      },
      async enhanceCharacterPrompt() {
        if (!safeText$3(this.currentCharacter.name) || !safeText$3(this.currentCharacter.description)) {
          this.showToast("请先填写角色名称和描述");
          return;
        }
        this.characterEnhancing = true;
        try {
          const prompt = safeText$3(this.currentCharacter.prompt) || this.buildCharacterBasePrompt();
          this.currentCharacter.prompt = await this.runTask("正在增强角色提示词", () => this.requestEnhance(prompt, { prompt_type: "character_asset", asset_type: "character", name: this.currentCharacter.name, subject_name: this.currentCharacter.name, wardrobe: this.normalizedWardrobe() }), { successText: "角色提示词已准备" });
        } catch (error) {
          this.showToast(error.message || "增强提示词失败");
        } finally {
          this.characterEnhancing = false;
        }
      },
      async enhanceScenePrompt() {
        if (!safeText$3(this.currentScene.name) || !safeText$3(this.currentScene.description)) {
          this.showToast("请先填写场景名称和描述");
          return;
        }
        this.sceneEnhancing = true;
        try {
          const prompt = safeText$3(this.currentScene.prompt) || this.buildSceneBasePrompt();
          this.currentScene.prompt = await this.runTask("正在增强场景提示词", () => this.requestEnhance(prompt, { prompt_type: "scene_asset", asset_type: "scene", name: this.currentScene.name, subject_name: this.currentScene.name }), { successText: "场景提示词已准备" });
        } catch (error) {
          this.showToast(error.message || "增强提示词失败");
        } finally {
          this.sceneEnhancing = false;
        }
      },
      async generateCharacterAsset() {
        if (!safeText$3(this.currentCharacter.name) || !safeText$3(this.currentCharacter.description)) {
          this.showToast("请先填写角色名称和描述");
          return;
        }
        this.characterLoading = true;
        try {
          const wardrobe = this.normalizedWardrobe();
          const prompt = safeText$3(this.currentCharacter.prompt) || this.buildCharacterBasePrompt();
          const response = await this.runTask("正在生成角色资产", () => generateCharacter({ description: prompt }), { successText: "角色资产已生成" });
          this.assets = [normalizeAssetEntry({ ...clone$1(response, {}), name: safeText$3(this.currentCharacter.name), type: "角色", asset_kind: "character", wardrobe, prompt, source_description: safeText$3(this.currentCharacter.description) }, this.assets.length), ...this.assets];
          this.currentCharacter.prompt = safeText$3(response && response.prompt) || prompt;
          await this.persistProjectState(true);
        } catch (error) {
          this.showToast(error.message || "生成角色资产失败");
        } finally {
          this.characterLoading = false;
        }
      },
      async generateSceneAsset() {
        if (!safeText$3(this.currentScene.name) || !safeText$3(this.currentScene.description)) {
          this.showToast("请先填写场景名称和描述");
          return;
        }
        this.sceneLoading = true;
        try {
          const prompt = safeText$3(this.currentScene.prompt) || this.buildSceneBasePrompt();
          const response = await this.runTask("正在生成场景资产", () => generateScene({ description: prompt }), { successText: "场景资产已生成" });
          this.assets = [normalizeAssetEntry({ ...clone$1(response, {}), name: safeText$3(this.currentScene.name), type: "场景", asset_kind: "scene", prompt, source_description: safeText$3(this.currentScene.description) }, this.assets.length), ...this.assets];
          this.currentScene.prompt = safeText$3(response && response.prompt) || prompt;
          await this.persistProjectState(true);
        } catch (error) {
          this.showToast(error.message || "生成场景资产失败");
        } finally {
          this.sceneLoading = false;
        }
      },
      deleteAsset(index, asset) {
        uni.showModal({ title: "删除资产", content: `确认删除“${safeText$3(asset && asset.name) || "未命名资产"}”吗？`, success: async (result) => {
          if (!result.confirm) {
            return;
          }
          const realIndex = this.assets.findIndex((item) => String(item && item.id) === String(asset && asset.id));
          this.assets.splice(realIndex >= 0 ? realIndex : index, 1);
          await this.persistProjectState(true);
        } });
      },
      addShot() {
        this.shots.push(this.normalizeShot(createEmptyShot(this.shots.length + 1), this.shots.length));
        this.selectedShotIndex = this.shots.length - 1;
      },
      async loadShotsFromScript() {
        if (!this.sceneRows.length) {
          this.showToast("当前还没有可导入的分镜结果");
          return;
        }
        this.shots = buildShotsFromScenes(this.sceneRows).map((shot, index) => this.normalizeShot(shot, index));
        this.selectedShotIndex = this.shots.length ? 0 : -1;
        await this.persistProjectState(true);
        this.showToast("镜头已导入导演模块");
      },
      buildShotPrompt(shot) {
        return shot ? [safeText$3(shot.prompt), safeText$3(shot.shotSummary), safeText$3(shot.detailedShotDescription)].filter(Boolean).join("；") : "";
      },
      async enhanceCurrentShotPrompt() {
        if (!this.currentShot) {
          return;
        }
        this.shotEnhancing = true;
        try {
          const basePrompt = this.buildShotPrompt(this.currentShot);
          const response = await this.runTask("正在增强镜头提示词", () => enhancePrompt({ prompt: basePrompt, context: { prompt_type: "shot_plan", shot_summary: this.currentShot.shotSummary } }), { successText: "镜头提示词已准备" });
          this.currentShot.prompt = safeText$3(response && response.enhanced_prompt) || basePrompt;
        } catch (error) {
          this.showToast(error.message || "增强提示词失败");
        } finally {
          this.shotEnhancing = false;
        }
      },
      async generateFrame(frameKey) {
        if (!this.currentShot) {
          return;
        }
        this.frameLoadingKey = frameKey;
        try {
          const frame = this.currentShot[frameKey];
          const description = safeText$3(frame.description) || this.buildShotPrompt(this.currentShot);
          const referenceImages = [];
          let preferImg2img = false;
          if (frameKey === "endFrame" && this.currentShot.startFrame && this.currentShot.startFrame.image_url) {
            referenceImages.push(this.currentShot.startFrame.image_url);
            preferImg2img = true;
          }
          const response = await this.runTask(frameKey === "startFrame" ? "正在生成起始帧" : "正在生成结束帧", () => generateScene({ description, reference_images: referenceImages, prefer_img2img: preferImg2img, context: { prompt_type: "frame", frame_key: frameKey } }), { successText: frameKey === "startFrame" ? "起始帧已生成" : "结束帧已生成" });
          frame.description = description;
          frame.enhanced_prompt = safeText$3(response && response.prompt) || description;
          frame.image_url = safeText$3(response && response.image_url);
          await this.persistProjectState(true);
        } catch (error) {
          this.showToast(error.message || "生成关键帧失败");
        } finally {
          this.frameLoadingKey = "";
        }
      },
      taskState(shot) {
        const status = safeText$3(shot && shot.videoTask && shot.videoTask.status).toLowerCase();
        if (safeText$3(shot && shot.videoUrl) || status === "succeeded") {
          return "succeeded";
        }
        if (["submitting", "submitted", "processing", "running", "pending"].includes(status)) {
          return "processing";
        }
        if (["failed", "error"].includes(status)) {
          return "failed";
        }
        return "idle";
      },
      taskStatusText(shot) {
        const state = this.taskState(shot);
        return state === "succeeded" ? "视频已就绪" : state === "processing" ? "视频生成中" : state === "failed" ? "视频生成失败" : "待生成";
      },
      taskProgressValue(shot) {
        const rawValue = Number(shot && shot.videoTask && shot.videoTask.progress || 0);
        const state = this.taskState(shot);
        if (state === "succeeded") {
          return 100;
        }
        if (state === "processing") {
          return rawValue > 0 ? Math.min(Math.round(rawValue), 99) : 35;
        }
        return rawValue > 0 ? Math.min(Math.round(rawValue), 100) : 0;
      },
      applyTaskUpdate(index, payload = {}) {
        const shot = this.shots[index];
        if (!shot) {
          return;
        }
        shot.videoTask = { ...shot.videoTask, taskId: safeText$3(payload.task_id || payload.taskId || shot.videoTask.taskId), status: safeText$3(payload.status || shot.videoTask.status), message: safeText$3(payload.message || shot.videoTask.message), progress: Number(payload.progress || shot.videoTask.progress || 0), provider: safeText$3(payload.provider || shot.videoTask.provider || this.videoProvider), reqKey: safeText$3(payload.req_key || payload.reqKey || shot.videoTask.reqKey), queryUrl: safeText$3(payload.query_url || payload.queryUrl || shot.videoTask.queryUrl), queryMethod: safeText$3(payload.query_method || payload.queryMethod || shot.videoTask.queryMethod) };
        const nextUrl = safeText$3(payload.video_url || payload.videoUrl);
        if (nextUrl) {
          shot.videoUrl = nextUrl;
        }
      },
      clearPolling(index) {
        if (this.pollTimers[index]) {
          clearTimeout(this.pollTimers[index]);
          delete this.pollTimers[index];
        }
      },
      startPolling(index) {
        this.clearPolling(index);
        const tick = async () => {
          const shot = this.shots[index];
          if (!shot || !shot.videoTask || !shot.videoTask.taskId) {
            return;
          }
          try {
            const response = await queryVideoTask(shot.videoTask.taskId, { provider: shot.videoTask.provider || this.videoProvider, req_key: shot.videoTask.reqKey || "", query_url: shot.videoTask.queryUrl || "", query_method: shot.videoTask.queryMethod || "" });
            this.applyTaskUpdate(index, response);
            await this.persistProjectState(true);
            if (["succeeded", "failed"].includes(safeText$3(response.status).toLowerCase()) || safeText$3(response.video_url || response.videoUrl)) {
              this.clearPolling(index);
              return;
            }
            this.pollTimers[index] = setTimeout(tick, 5e3);
          } catch (error) {
            this.applyTaskUpdate(index, { status: "failed", message: error.message || "任务查询失败" });
            await this.persistProjectState(true);
            this.clearPolling(index);
          }
        };
        this.pollTimers[index] = setTimeout(tick, 5e3);
      },
      async generateCurrentVideo() {
        if (!this.currentShot || !safeText$3(this.currentShot.startFrame && this.currentShot.startFrame.image_url)) {
          this.showToast("请先生成起始帧");
          return;
        }
        this.videoLoading = true;
        try {
          const response = await this.runTask("正在提交视频任务", () => generateVideo({ start_frame: this.currentShot.startFrame, end_frame: this.currentShot.endFrame, mode: "keyframe-interpolation", context: { video_provider: this.videoProvider, shot_title: this.currentShot.title, shot_prompt: this.buildShotPrompt(this.currentShot) }, provider: this.videoProvider }), { successText: "视频任务已提交" });
          this.applyTaskUpdate(this.selectedShotIndex, response);
          await this.persistProjectState(true);
          if (safeText$3(response.task_id || response.taskId) && !safeText$3(response.video_url || response.videoUrl)) {
            this.startPolling(this.selectedShotIndex);
          }
        } catch (error) {
          this.showToast(error.message || "提交视频任务失败");
        } finally {
          this.videoLoading = false;
        }
      },
      async refreshCurrentTask() {
        if (!this.currentShot || !safeText$3(this.currentShot.videoTask && this.currentShot.videoTask.taskId)) {
          this.showToast("当前镜头还没有任务 ID");
          return;
        }
        try {
          const response = await this.runTask("正在刷新视频任务", () => queryVideoTask(this.currentShot.videoTask.taskId, { provider: this.currentShot.videoTask.provider || this.videoProvider, req_key: this.currentShot.videoTask.reqKey || "", query_url: this.currentShot.videoTask.queryUrl || "", query_method: this.currentShot.videoTask.queryMethod || "" }), { successText: "任务状态已更新" });
          this.applyTaskUpdate(this.selectedShotIndex, response);
          await this.persistProjectState(true);
        } catch (error) {
          this.showToast(error.message || "刷新任务失败");
        }
      },
      openExportSection() {
        uni.switchTab({ url: "/views/export/index" });
      }
    }
  };
  function _sfc_render$5(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_LoadingProgress = vue.resolveComponent("LoadingProgress");
    const _component_u_button = resolveEasycom(vue.resolveDynamicComponent("u-button"), __easycom_0);
    return vue.openBlock(), vue.createElementBlock("view", { class: "studio-page" }, [
      vue.createVNode(_component_LoadingProgress, {
        visible: $data.progress.visible,
        value: $data.progress.value,
        label: $data.progress.label
      }, null, 8, ["visible", "value", "label"]),
      vue.createElementVNode("view", { class: "studio-page__bg" }),
      vue.createElementVNode("view", { class: "app-page studio-shell" }, [
        vue.createElementVNode("view", { class: "section-card tab-card" }, [
          vue.createElementVNode("view", { class: "section-head" }, [
            vue.createElementVNode("view", null, [
              vue.createElementVNode("text", { class: "section-title" }, "动漫生成"),
              vue.createElementVNode("text", { class: "section-subtitle" }, "项目、剧本、资产、导演四个阶段顺序推进，切换时保留当前编辑状态。")
            ])
          ]),
          vue.createElementVNode("view", { class: "segment-row no-top-gap" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($data.createTabs, (item) => {
                return vue.openBlock(), vue.createElementBlock("text", {
                  key: item.key,
                  class: vue.normalizeClass(["segment-pill", { active: $data.activeCreateTab === item.key }]),
                  onClick: ($event) => $options.handleCreateTabChange(item.key)
                }, vue.toDisplayString(item.label), 11, ["onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ]),
        vue.withDirectives(vue.createElementVNode(
          "view",
          { class: "panel-stack" },
          [
            vue.createElementVNode("view", { class: "section-card" }, [
              vue.createElementVNode("view", { class: "section-head" }, [
                vue.createElementVNode("view", null, [
                  vue.createElementVNode("text", { class: "section-title" }, "项目工作区"),
                  vue.createElementVNode("text", { class: "section-subtitle" }, "每个账号的项目和缓存分开保存，继续创作时会自动恢复当前项目。")
                ]),
                vue.createVNode(_component_u_button, {
                  class: "secondary-btn mini-btn",
                  onClick: $options.loadProjects
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode("刷新")
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["onClick"])
              ]),
              $data.activeProjectCache ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "focus-card top-gap"
              }, [
                vue.createElementVNode(
                  "text",
                  { class: "focus-title" },
                  vue.toDisplayString($data.activeProjectCache.name || "未命名项目"),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "section-subtitle" },
                  vue.toDisplayString($data.activeProjectCache.script_title || "未填写剧本标题") + " · 第 " + vue.toDisplayString($data.activeProjectCache.episode_no || 1) + " 集",
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("view", { class: "chip-row top-gap" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "info-chip" },
                    vue.toDisplayString($options.providerText($data.activeProjectCache.video_provider)),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "info-chip" },
                    "资产 " + vue.toDisplayString($options.assetCount($data.activeProjectCache)),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "info-chip" },
                    "镜头 " + vue.toDisplayString($options.shotCount($data.activeProjectCache)),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createVNode(_component_u_button, {
                  class: "primary-btn mini-btn top-gap",
                  type: "primary",
                  onClick: $options.openCurrentProject
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode("继续创作")
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["onClick"])
              ])) : vue.createCommentVNode("v-if", true)
            ]),
            vue.createElementVNode("view", { class: "section-card" }, [
              vue.createElementVNode("text", { class: "section-title" }, "创建新项目"),
              vue.createElementVNode("view", { class: "form-grid two-col top-gap" }, [
                vue.createElementVNode("view", { class: "form-group" }, [
                  vue.createElementVNode("text", { class: "field-label" }, "项目名称"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.projectName = $event),
                      class: "field-input",
                      type: "text",
                      placeholder: "例如：仙侠短剧第一季",
                      "placeholder-class": "field-placeholder",
                      "adjust-position": false
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.projectName]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-group" }, [
                  vue.createElementVNode("text", { class: "field-label" }, "剧本标题"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.scriptTitle = $event),
                      class: "field-input",
                      type: "text",
                      placeholder: "例如：剑心追月",
                      "placeholder-class": "field-placeholder",
                      "adjust-position": false
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.scriptTitle]
                  ])
                ])
              ]),
              vue.createElementVNode("view", { class: "form-group" }, [
                vue.createElementVNode("text", { class: "field-label" }, "起始集数"),
                vue.createElementVNode("picker", {
                  range: $data.episodeChoices,
                  value: $options.episodeChoiceIndex,
                  onChange: _cache[2] || (_cache[2] = (...args) => $options.handleEpisodeChange && $options.handleEpisodeChange(...args))
                }, [
                  vue.createElementVNode(
                    "view",
                    { class: "picker-field" },
                    "第 " + vue.toDisplayString($data.selectedEpisode) + " 集",
                    1
                    /* TEXT */
                  )
                ], 40, ["range", "value"])
              ]),
              vue.createVNode(_component_u_button, {
                class: "primary-btn large-btn",
                type: "primary",
                loading: $data.creating,
                onClick: $options.createNewProject
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode(
                    vue.toDisplayString($data.creating ? "正在创建项目..." : "创建并进入剧本阶段"),
                    1
                    /* TEXT */
                  )
                ]),
                _: 1
                /* STABLE */
              }, 8, ["loading", "onClick"])
            ]),
            vue.createElementVNode("view", { class: "section-card" }, [
              vue.createElementVNode("text", { class: "section-title" }, "项目列表"),
              $data.loading ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "empty-block"
              }, [
                vue.createElementVNode("text", null, "正在同步项目列表...")
              ])) : !$data.projects.length ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 1,
                class: "empty-block"
              }, [
                vue.createElementVNode("text", null, "还没有项目，先创建一个再开始。")
              ])) : (vue.openBlock(), vue.createElementBlock("view", {
                key: 2,
                class: "list-stack top-gap"
              }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList($data.projects, (project) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      key: project.id,
                      class: "list-card",
                      onClick: ($event) => $options.openProject(project)
                    }, [
                      vue.createElementVNode("view", { class: "list-card__body" }, [
                        vue.createElementVNode(
                          "text",
                          { class: "list-card__title" },
                          vue.toDisplayString(project.name || "未命名项目"),
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode(
                          "text",
                          { class: "list-card__desc" },
                          vue.toDisplayString(project.script_title || "未填写剧本标题") + " · 第 " + vue.toDisplayString(project.episode_no || 1) + " 集",
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode("view", { class: "chip-row top-gap" }, [
                          vue.createElementVNode(
                            "text",
                            { class: "info-chip" },
                            vue.toDisplayString($options.providerText(project.video_provider)),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "text",
                            { class: "info-chip" },
                            "资产 " + vue.toDisplayString($options.assetCount(project)),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "text",
                            { class: "info-chip" },
                            "镜头 " + vue.toDisplayString($options.shotCount(project)),
                            1
                            /* TEXT */
                          )
                        ])
                      ]),
                      vue.createVNode(_component_u_button, { class: "ghost-btn mini-btn" }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode("打开")
                        ]),
                        _: 1
                        /* STABLE */
                      })
                    ], 8, ["onClick"]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ]))
            ])
          ],
          512
          /* NEED_PATCH */
        ), [
          [vue.vShow, $data.activeCreateTab === "project"]
        ]),
        vue.withDirectives(vue.createElementVNode(
          "view",
          { class: "panel-stack" },
          [
            !$options.hasProject ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "section-card empty-block"
            }, [
              vue.createElementVNode("text", null, "先在项目模块创建或打开项目，再继续写剧本。"),
              vue.createVNode(_component_u_button, {
                class: "primary-btn mini-btn top-gap",
                type: "primary",
                onClick: _cache[3] || (_cache[3] = ($event) => $options.handleCreateTabChange("project"))
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode("去项目模块")
                ]),
                _: 1
                /* STABLE */
              })
            ])) : (vue.openBlock(), vue.createElementBlock(
              vue.Fragment,
              { key: 1 },
              [
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("view", { class: "section-head" }, [
                    vue.createElementVNode("view", null, [
                      vue.createElementVNode("text", { class: "section-title" }, "剧本设定"),
                      vue.createElementVNode("text", { class: "section-subtitle" }, "先写本集故事，再生成分镜结果并同步到导演模块。")
                    ]),
                    vue.createElementVNode("text", { class: "info-chip active" }, "状态自动保留")
                  ]),
                  vue.createElementVNode("view", { class: "form-grid two-col top-gap" }, [
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "项目名称"),
                      vue.withDirectives(vue.createElementVNode(
                        "input",
                        {
                          "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => _ctx.currentProjectName = $event),
                          class: "field-input",
                          type: "text",
                          placeholder: "请输入项目名称",
                          "placeholder-class": "field-placeholder",
                          "adjust-position": false
                        },
                        null,
                        512
                        /* NEED_PATCH */
                      ), [
                        [vue.vModelText, _ctx.currentProjectName]
                      ])
                    ]),
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "剧本标题"),
                      vue.withDirectives(vue.createElementVNode(
                        "input",
                        {
                          "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => _ctx.currentScriptTitle = $event),
                          class: "field-input",
                          type: "text",
                          placeholder: "请输入剧本标题",
                          "placeholder-class": "field-placeholder",
                          "adjust-position": false
                        },
                        null,
                        512
                        /* NEED_PATCH */
                      ), [
                        [vue.vModelText, _ctx.currentScriptTitle]
                      ])
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-grid three-col" }, [
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "集数"),
                      vue.createElementVNode("picker", {
                        range: $options.episodeOptions,
                        value: $options.episodeIndex,
                        onChange: _cache[6] || (_cache[6] = (...args) => $options.handleCurrentEpisodeChange && $options.handleCurrentEpisodeChange(...args))
                      }, [
                        vue.createElementVNode(
                          "view",
                          { class: "picker-field" },
                          "第 " + vue.toDisplayString(_ctx.currentEpisodeNo) + " 集",
                          1
                          /* TEXT */
                        )
                      ], 40, ["range", "value"])
                    ]),
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "视频接口"),
                      vue.createElementVNode("picker", {
                        range: $options.providerLabels,
                        value: $options.providerIndex,
                        onChange: _cache[7] || (_cache[7] = (...args) => $options.handleProviderChange && $options.handleProviderChange(...args))
                      }, [
                        vue.createElementVNode(
                          "view",
                          { class: "picker-field" },
                          vue.toDisplayString($options.providerLabels[$options.providerIndex]),
                          1
                          /* TEXT */
                        )
                      ], 40, ["range", "value"])
                    ]),
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "目标时长"),
                      vue.createElementVNode("picker", {
                        range: $options.durationLabels,
                        value: $options.durationIndex,
                        onChange: _cache[8] || (_cache[8] = (...args) => $options.handleDurationChange && $options.handleDurationChange(...args))
                      }, [
                        vue.createElementVNode(
                          "view",
                          { class: "picker-field" },
                          vue.toDisplayString($options.durationLabels[$options.durationIndex]),
                          1
                          /* TEXT */
                        )
                      ], 40, ["range", "value"])
                    ])
                  ]),
                  $data.targetDuration === "custom" ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "form-group"
                  }, [
                    vue.createElementVNode("text", { class: "field-label" }, "自定义时长"),
                    vue.withDirectives(vue.createElementVNode(
                      "input",
                      {
                        "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $data.customDuration = $event),
                        class: "field-input",
                        type: "text",
                        placeholder: "例如：40s 或 6min",
                        "placeholder-class": "field-placeholder",
                        "adjust-position": false
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.customDuration]
                    ])
                  ])) : vue.createCommentVNode("v-if", true),
                  vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      loading: $data.saving,
                      onClick: $options.saveProject
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("保存项目")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "ghost-btn",
                      onClick: $options.addEpisode
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("新增集数")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "ghost-btn",
                      onClick: _cache[10] || (_cache[10] = ($event) => $options.loadProject(true))
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("重新加载")
                      ]),
                      _: 1
                      /* STABLE */
                    })
                  ])
                ]),
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("text", { class: "section-title" }, "本集剧本输入"),
                  vue.createElementVNode("view", { class: "form-group top-gap" }, [
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $data.scriptInput = $event),
                        class: "field-textarea large-textarea",
                        placeholder: "输入本集故事梗概、人物冲突和关键转折",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.scriptInput]
                    ])
                  ]),
                  $data.errorMessage ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "message-card message-card--error"
                  }, [
                    vue.createElementVNode(
                      "text",
                      null,
                      vue.toDisplayString($data.errorMessage),
                      1
                      /* TEXT */
                    )
                  ])) : vue.createCommentVNode("v-if", true),
                  vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                    vue.createVNode(_component_u_button, {
                      class: "primary-btn",
                      type: "primary",
                      loading: $data.parsing,
                      onClick: $options.parseCurrentScript
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.parsing ? "正在生成分镜脚本..." : "生成分镜脚本"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      onClick: $options.saveProject
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("先保存草稿")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"])
                  ])
                ]),
                $options.sceneRows.length ? (vue.openBlock(), vue.createElementBlock("view", {
                  key: 0,
                  class: "section-card"
                }, [
                  vue.createElementVNode("view", { class: "section-head" }, [
                    vue.createElementVNode("text", { class: "section-title" }, "分镜结果"),
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn mini-btn",
                      onClick: $options.syncScenesToShots
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("同步到导演模块")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"])
                  ]),
                  vue.createElementVNode("view", { class: "list-stack top-gap" }, [
                    (vue.openBlock(true), vue.createElementBlock(
                      vue.Fragment,
                      null,
                      vue.renderList($options.sceneRows.slice(0, 8), (scene, index) => {
                        return vue.openBlock(), vue.createElementBlock("view", {
                          key: `scene-${index}`,
                          class: "list-card list-card--stack"
                        }, [
                          vue.createElementVNode(
                            "text",
                            { class: "list-card__title" },
                            "场次 " + vue.toDisplayString(scene.scene_id || index + 1) + " · " + vue.toDisplayString(scene.duration || "5s"),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "text",
                            { class: "list-card__desc" },
                            vue.toDisplayString(scene.description || "暂无场景描述"),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "text",
                            { class: "meta-hint" },
                            vue.toDisplayString(scene.shot_description || "暂无镜头摘要"),
                            1
                            /* TEXT */
                          )
                        ]);
                      }),
                      128
                      /* KEYED_FRAGMENT */
                    ))
                  ])
                ])) : vue.createCommentVNode("v-if", true),
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("text", { class: "section-title" }, "结果 JSON"),
                  vue.withDirectives(vue.createElementVNode(
                    "textarea",
                    {
                      "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $data.rawResultText = $event),
                      class: "field-textarea json-textarea top-gap",
                      placeholder: "生成完成后，可直接微调 JSON",
                      "placeholder-class": "field-placeholder"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.rawResultText]
                  ]),
                  vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      onClick: $options.applyEditedResult
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("应用修改")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "ghost-btn",
                      onClick: $options.resetEditedResult
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("恢复原结果")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"])
                  ])
                ])
              ],
              64
              /* STABLE_FRAGMENT */
            ))
          ],
          512
          /* NEED_PATCH */
        ), [
          [vue.vShow, $data.activeCreateTab === "script"]
        ]),
        vue.withDirectives(vue.createElementVNode(
          "view",
          { class: "panel-stack" },
          [
            !$options.hasProject ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "section-card empty-block"
            }, [
              vue.createElementVNode("text", null, "先选中项目，再生成角色和场景资产。"),
              vue.createVNode(_component_u_button, {
                class: "primary-btn mini-btn top-gap",
                type: "primary",
                onClick: _cache[13] || (_cache[13] = ($event) => $options.handleCreateTabChange("project"))
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode("去项目模块")
                ]),
                _: 1
                /* STABLE */
              })
            ])) : (vue.openBlock(), vue.createElementBlock(
              vue.Fragment,
              { key: 1 },
              [
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("view", { class: "section-head" }, [
                    vue.createElementVNode("view", null, [
                      vue.createElementVNode("text", { class: "section-title" }, "AI 提取推荐"),
                      vue.createElementVNode("text", { class: "section-subtitle" }, "只做推荐，不会自动写入表单。角色行支持长按快速导入。")
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn mini-btn",
                      loading: $data.extractingCharacters,
                      disabled: $data.extractingScenes || !$options.hasScriptInput,
                      onClick: $options.extractCharactersByAi
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.extractingCharacters ? "正在提取角色..." : "AI 提取角色"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "disabled", "onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn mini-btn",
                      loading: $data.extractingScenes,
                      disabled: $data.extractingCharacters || !$options.hasScriptInput,
                      onClick: $options.extractScenesByAi
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.extractingScenes ? "正在提取场景..." : "AI 提取场景"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "disabled", "onClick"])
                  ]),
                  $data.recommendActionMessage ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "message-card recommend-message top-gap"
                  }, [
                    vue.createElementVNode(
                      "text",
                      null,
                      vue.toDisplayString($data.recommendActionMessage),
                      1
                      /* TEXT */
                    )
                  ])) : vue.createCommentVNode("v-if", true),
                  !$options.hasRecommendationCandidates ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 1,
                    class: "empty-block top-gap"
                  }, [
                    vue.createElementVNode("text", null, "先在剧本模块生成分镜，或点击上方按钮提取推荐。")
                  ])) : (vue.openBlock(), vue.createElementBlock(
                    vue.Fragment,
                    { key: 2 },
                    [
                      $options.recommendedSceneCandidates.length ? (vue.openBlock(), vue.createElementBlock("view", {
                        key: 0,
                        class: "top-gap"
                      }, [
                        vue.createElementVNode("text", { class: "field-label" }, "场景推荐"),
                        vue.createElementVNode("scroll-view", {
                          "scroll-x": "",
                          class: "recommend-scroll"
                        }, [
                          vue.createElementVNode("view", { class: "recommend-table" }, [
                            vue.createElementVNode("view", { class: "recommend-row recommend-head" }, [
                              vue.createElementVNode("text", { class: "recommend-col col-name" }, "场景"),
                              vue.createElementVNode("text", { class: "recommend-col col-desc" }, "描述"),
                              vue.createElementVNode("text", { class: "recommend-col col-status" }, "状态"),
                              vue.createElementVNode("text", { class: "recommend-col col-action" }, "操作")
                            ]),
                            (vue.openBlock(true), vue.createElementBlock(
                              vue.Fragment,
                              null,
                              vue.renderList($options.recommendedSceneCandidates, (item, index) => {
                                return vue.openBlock(), vue.createElementBlock("view", {
                                  key: `scene-rec-${index}`,
                                  class: "recommend-row"
                                }, [
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-name" },
                                    vue.toDisplayString(item.name),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-desc" },
                                    vue.toDisplayString(item.description || item.shotSummary || "-"),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-status" },
                                    vue.toDisplayString(item.generated ? `已生成：${item.matchedAssets.join("、")}` : "推荐生成"),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode("view", { class: "recommend-col col-action" }, [
                                    vue.createVNode(_component_u_button, {
                                      class: "ghost-btn mini-btn",
                                      onClick: ($event) => $options.fillSceneFromCandidate(item)
                                    }, {
                                      default: vue.withCtx(() => [
                                        vue.createTextVNode("导入")
                                      ]),
                                      _: 2
                                      /* DYNAMIC */
                                    }, 1032, ["onClick"])
                                  ])
                                ]);
                              }),
                              128
                              /* KEYED_FRAGMENT */
                            ))
                          ])
                        ])
                      ])) : vue.createCommentVNode("v-if", true),
                      $options.recommendedCharacterCandidates.length ? (vue.openBlock(), vue.createElementBlock("view", {
                        key: 1,
                        class: "top-gap"
                      }, [
                        vue.createElementVNode("text", { class: "field-label" }, "角色推荐（长按可导入）"),
                        vue.createElementVNode("scroll-view", {
                          "scroll-x": "",
                          class: "recommend-scroll"
                        }, [
                          vue.createElementVNode("view", { class: "recommend-table" }, [
                            vue.createElementVNode("view", { class: "recommend-row recommend-head" }, [
                              vue.createElementVNode("text", { class: "recommend-col col-name" }, "角色"),
                              vue.createElementVNode("text", { class: "recommend-col col-role" }, "定位"),
                              vue.createElementVNode("text", { class: "recommend-col col-desc" }, "目标 / 视觉锚点"),
                              vue.createElementVNode("text", { class: "recommend-col col-status" }, "状态"),
                              vue.createElementVNode("text", { class: "recommend-col col-action" }, "操作")
                            ]),
                            (vue.openBlock(true), vue.createElementBlock(
                              vue.Fragment,
                              null,
                              vue.renderList($options.recommendedCharacterCandidates, (item, index) => {
                                return vue.openBlock(), vue.createElementBlock("view", {
                                  key: `char-rec-${index}`,
                                  class: "recommend-row recommend-row--importable",
                                  onLongpress: ($event) => $options.importCharacterFromCandidate(item, true)
                                }, [
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-name" },
                                    vue.toDisplayString(item.name || "-"),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-role" },
                                    vue.toDisplayString(item.role || "-"),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-desc" },
                                    vue.toDisplayString([item.goal, item.visualAnchor].filter(Boolean).join(" | ") || "-"),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode(
                                    "text",
                                    { class: "recommend-col col-status" },
                                    vue.toDisplayString(item.generated ? `已生成：${item.matchedAssets.join("、")}` : "推荐生成"),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode("view", { class: "recommend-col col-action" }, [
                                    vue.createVNode(_component_u_button, {
                                      class: "ghost-btn mini-btn",
                                      onClick: ($event) => $options.importCharacterFromCandidate(item)
                                    }, {
                                      default: vue.withCtx(() => [
                                        vue.createTextVNode("导入")
                                      ]),
                                      _: 2
                                      /* DYNAMIC */
                                    }, 1032, ["onClick"])
                                  ])
                                ], 40, ["onLongpress"]);
                              }),
                              128
                              /* KEYED_FRAGMENT */
                            ))
                          ])
                        ])
                      ])) : vue.createCommentVNode("v-if", true)
                    ],
                    64
                    /* STABLE_FRAGMENT */
                  ))
                ]),
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("text", { class: "section-title" }, "角色资产"),
                  vue.createElementVNode("view", { class: "form-group top-gap" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "角色名称"),
                    vue.withDirectives(vue.createElementVNode(
                      "input",
                      {
                        "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $data.currentCharacter.name = $event),
                        class: "field-input",
                        type: "text",
                        placeholder: "例如：叶青霜",
                        "placeholder-class": "field-placeholder",
                        "adjust-position": false
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentCharacter.name]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "角色描述"),
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => $data.currentCharacter.description = $event),
                        class: "field-textarea",
                        placeholder: "描述外貌、年龄感、服装和角色气质",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentCharacter.description]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "造型版本"),
                    vue.createElementVNode("picker", {
                      range: $data.wardrobeOptions,
                      value: $options.wardrobeIndex,
                      onChange: _cache[16] || (_cache[16] = (...args) => $options.handleWardrobeChange && $options.handleWardrobeChange(...args))
                    }, [
                      vue.createElementVNode(
                        "view",
                        { class: "picker-field" },
                        vue.toDisplayString($data.currentCharacter.wardrobe),
                        1
                        /* TEXT */
                      )
                    ], 40, ["range", "value"])
                  ]),
                  $data.currentCharacter.wardrobe === "自定义" ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "form-group"
                  }, [
                    vue.createElementVNode("text", { class: "field-label" }, "自定义造型"),
                    vue.withDirectives(vue.createElementVNode(
                      "input",
                      {
                        "onUpdate:modelValue": _cache[17] || (_cache[17] = ($event) => $data.currentCharacter.customWardrobe = $event),
                        class: "field-input",
                        type: "text",
                        placeholder: "例如：雨夜战损版",
                        "placeholder-class": "field-placeholder",
                        "adjust-position": false
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentCharacter.customWardrobe]
                    ])
                  ])) : vue.createCommentVNode("v-if", true),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "角色提示词"),
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[18] || (_cache[18] = ($event) => $data.currentCharacter.prompt = $event),
                        class: "field-textarea",
                        placeholder: "可手动调整，也可先点增强提示词",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentCharacter.prompt]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "action-row compact-actions" }, [
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      loading: $data.characterEnhancing,
                      onClick: $options.enhanceCharacterPrompt
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.characterEnhancing ? "正在增强..." : "增强提示词"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "primary-btn",
                      type: "primary",
                      loading: $data.characterLoading,
                      onClick: $options.generateCharacterAsset
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.characterLoading ? "正在生成..." : "生成角色资产"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"])
                  ])
                ]),
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("text", { class: "section-title" }, "场景资产"),
                  vue.createElementVNode("view", { class: "form-group top-gap" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "场景名称"),
                    vue.withDirectives(vue.createElementVNode(
                      "input",
                      {
                        "onUpdate:modelValue": _cache[19] || (_cache[19] = ($event) => $data.currentScene.name = $event),
                        class: "field-input",
                        type: "text",
                        placeholder: "例如：青云山门",
                        "placeholder-class": "field-placeholder",
                        "adjust-position": false
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentScene.name]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "场景描述"),
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[20] || (_cache[20] = ($event) => $data.currentScene.description = $event),
                        class: "field-textarea",
                        placeholder: "描述空间关系、建筑、天气和氛围",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentScene.description]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "场景提示词"),
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[21] || (_cache[21] = ($event) => $data.currentScene.prompt = $event),
                        class: "field-textarea",
                        placeholder: "可手动调整，也可先点增强提示词",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $data.currentScene.prompt]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "action-row compact-actions" }, [
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      loading: $data.sceneEnhancing,
                      onClick: $options.enhanceScenePrompt
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.sceneEnhancing ? "正在增强..." : "增强提示词"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "primary-btn",
                      type: "primary",
                      loading: $data.sceneLoading,
                      onClick: $options.generateSceneAsset
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.sceneLoading ? "正在生成..." : "生成场景资产"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"])
                  ])
                ]),
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("view", { class: "section-head" }, [
                    vue.createElementVNode("text", { class: "section-title" }, "资产库"),
                    vue.createElementVNode(
                      "text",
                      { class: "info-chip" },
                      vue.toDisplayString($options.filteredAssets.length) + " 项",
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "segment-row no-top-gap" }, [
                    (vue.openBlock(true), vue.createElementBlock(
                      vue.Fragment,
                      null,
                      vue.renderList($data.assetFilters, (item) => {
                        return vue.openBlock(), vue.createElementBlock("text", {
                          key: item.value,
                          class: vue.normalizeClass(["segment-pill", { active: $data.assetFilter === item.value }]),
                          onClick: ($event) => $data.assetFilter = item.value
                        }, vue.toDisplayString(item.label), 11, ["onClick"]);
                      }),
                      128
                      /* KEYED_FRAGMENT */
                    ))
                  ]),
                  !$options.filteredAssets.length ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "empty-block"
                  }, [
                    vue.createElementVNode("text", null, "还没有资产，先生成角色图或场景图。")
                  ])) : (vue.openBlock(), vue.createElementBlock("view", {
                    key: 1,
                    class: "list-stack top-gap"
                  }, [
                    (vue.openBlock(true), vue.createElementBlock(
                      vue.Fragment,
                      null,
                      vue.renderList($options.filteredAssets, (asset, index) => {
                        return vue.openBlock(), vue.createElementBlock("view", {
                          key: asset.id || index,
                          class: "asset-card"
                        }, [
                          asset.image_url ? (vue.openBlock(), vue.createElementBlock("image", {
                            key: 0,
                            class: "asset-image",
                            src: asset.image_url,
                            mode: "aspectFill"
                          }, null, 8, ["src"])) : vue.createCommentVNode("v-if", true),
                          vue.createElementVNode("view", { class: "list-card__body" }, [
                            vue.createElementVNode(
                              "text",
                              { class: "list-card__title" },
                              vue.toDisplayString(asset.name || `资产 ${index + 1}`),
                              1
                              /* TEXT */
                            ),
                            vue.createElementVNode(
                              "text",
                              { class: "list-card__desc" },
                              vue.toDisplayString($options.assetTypeLabel(asset)),
                              1
                              /* TEXT */
                            ),
                            asset.prompt ? (vue.openBlock(), vue.createElementBlock(
                              "text",
                              {
                                key: 0,
                                class: "meta-hint"
                              },
                              vue.toDisplayString(asset.prompt),
                              1
                              /* TEXT */
                            )) : vue.createCommentVNode("v-if", true),
                            vue.createVNode(_component_u_button, {
                              class: "ghost-btn mini-btn top-gap",
                              onClick: ($event) => $options.deleteAsset(index, asset)
                            }, {
                              default: vue.withCtx(() => [
                                vue.createTextVNode("删除")
                              ]),
                              _: 2
                              /* DYNAMIC */
                            }, 1032, ["onClick"])
                          ])
                        ]);
                      }),
                      128
                      /* KEYED_FRAGMENT */
                    ))
                  ]))
                ])
              ],
              64
              /* STABLE_FRAGMENT */
            ))
          ],
          512
          /* NEED_PATCH */
        ), [
          [vue.vShow, $data.activeCreateTab === "assets"]
        ]),
        vue.withDirectives(vue.createElementVNode(
          "view",
          { class: "panel-stack" },
          [
            !$options.hasProject ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "section-card empty-block"
            }, [
              vue.createElementVNode("text", null, "先准备项目和剧本，再进入导演模块拆分镜头。"),
              vue.createVNode(_component_u_button, {
                class: "primary-btn mini-btn top-gap",
                type: "primary",
                onClick: _cache[22] || (_cache[22] = ($event) => $options.handleCreateTabChange("project"))
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode("去项目模块")
                ]),
                _: 1
                /* STABLE */
              })
            ])) : (vue.openBlock(), vue.createElementBlock(
              vue.Fragment,
              { key: 1 },
              [
                vue.createElementVNode("view", { class: "section-card" }, [
                  vue.createElementVNode("view", { class: "section-head" }, [
                    vue.createElementVNode("text", { class: "section-title" }, "镜头清单"),
                    vue.createElementVNode("view", { class: "action-row compact-actions" }, [
                      vue.createVNode(_component_u_button, {
                        class: "secondary-btn mini-btn",
                        loading: $data.saving,
                        onClick: $options.saveProject
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode("保存镜头")
                        ]),
                        _: 1
                        /* STABLE */
                      }, 8, ["loading", "onClick"]),
                      vue.createVNode(_component_u_button, {
                        class: "ghost-btn mini-btn",
                        onClick: $options.loadShotsFromScript
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode("从剧本导入")
                        ]),
                        _: 1
                        /* STABLE */
                      }, 8, ["onClick"]),
                      vue.createVNode(_component_u_button, {
                        class: "ghost-btn mini-btn",
                        onClick: $options.addShot
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode("新增镜头")
                        ]),
                        _: 1
                        /* STABLE */
                      }, 8, ["onClick"])
                    ])
                  ]),
                  !_ctx.shots.length ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "empty-block"
                  }, [
                    vue.createElementVNode("text", null, "还没有镜头，先去剧本模块生成分镜。")
                  ])) : (vue.openBlock(), vue.createElementBlock("scroll-view", {
                    key: 1,
                    "scroll-x": "",
                    class: "shot-scroll top-gap"
                  }, [
                    vue.createElementVNode("view", { class: "shot-strip" }, [
                      (vue.openBlock(true), vue.createElementBlock(
                        vue.Fragment,
                        null,
                        vue.renderList(_ctx.shots, (shot, index) => {
                          return vue.openBlock(), vue.createElementBlock("view", {
                            key: `shot-${index}`,
                            class: vue.normalizeClass(["shot-pill", { active: $data.selectedShotIndex === index }]),
                            onClick: ($event) => $data.selectedShotIndex = index
                          }, [
                            vue.createElementVNode(
                              "text",
                              { class: "list-card__title" },
                              vue.toDisplayString(shot.title || `镜头 ${index + 1}`),
                              1
                              /* TEXT */
                            ),
                            vue.createElementVNode(
                              "text",
                              { class: "meta-hint" },
                              vue.toDisplayString($options.taskStatusText(shot)),
                              1
                              /* TEXT */
                            ),
                            $options.taskState(shot) === "processing" ? (vue.openBlock(), vue.createElementBlock("view", {
                              key: 0,
                              class: "inline-progress"
                            }, [
                              vue.createElementVNode(
                                "view",
                                {
                                  class: "inline-progress__bar",
                                  style: vue.normalizeStyle({ width: `${$options.taskProgressValue(shot)}%` })
                                },
                                null,
                                4
                                /* STYLE */
                              )
                            ])) : vue.createCommentVNode("v-if", true)
                          ], 10, ["onClick"]);
                        }),
                        128
                        /* KEYED_FRAGMENT */
                      ))
                    ])
                  ]))
                ]),
                $options.currentShot ? (vue.openBlock(), vue.createElementBlock("view", {
                  key: 0,
                  class: "section-card"
                }, [
                  vue.createElementVNode("view", { class: "section-head" }, [
                    vue.createElementVNode("text", { class: "section-title" }, "镜头编辑"),
                    vue.createElementVNode(
                      "text",
                      { class: "info-chip active" },
                      vue.toDisplayString($options.taskStatusText($options.currentShot)),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "form-grid two-col top-gap" }, [
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "镜头标题"),
                      vue.withDirectives(vue.createElementVNode(
                        "input",
                        {
                          "onUpdate:modelValue": _cache[23] || (_cache[23] = ($event) => $options.currentShot.title = $event),
                          class: "field-input",
                          type: "text",
                          placeholder: "镜头标题",
                          "placeholder-class": "field-placeholder",
                          "adjust-position": false
                        },
                        null,
                        512
                        /* NEED_PATCH */
                      ), [
                        [vue.vModelText, $options.currentShot.title]
                      ])
                    ]),
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "时长"),
                      vue.withDirectives(vue.createElementVNode(
                        "input",
                        {
                          "onUpdate:modelValue": _cache[24] || (_cache[24] = ($event) => $options.currentShot.duration = $event),
                          class: "field-input",
                          type: "text",
                          placeholder: "例如：5s",
                          "placeholder-class": "field-placeholder",
                          "adjust-position": false
                        },
                        null,
                        512
                        /* NEED_PATCH */
                      ), [
                        [vue.vModelText, $options.currentShot.duration]
                      ])
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "镜头概述"),
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[25] || (_cache[25] = ($event) => $options.currentShot.shotSummary = $event),
                        class: "field-textarea",
                        placeholder: "描述景别、动作和镜头变化",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $options.currentShot.shotSummary]
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "form-group" }, [
                    vue.createElementVNode("text", { class: "field-label" }, "镜头提示词"),
                    vue.withDirectives(vue.createElementVNode(
                      "textarea",
                      {
                        "onUpdate:modelValue": _cache[26] || (_cache[26] = ($event) => $options.currentShot.prompt = $event),
                        class: "field-textarea",
                        placeholder: "后续用于关键帧和视频生成",
                        "placeholder-class": "field-placeholder"
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelText, $options.currentShot.prompt]
                    ])
                  ]),
                  vue.createVNode(_component_u_button, {
                    class: "secondary-btn",
                    loading: $data.shotEnhancing,
                    onClick: $options.enhanceCurrentShotPrompt
                  }, {
                    default: vue.withCtx(() => [
                      vue.createTextVNode(
                        vue.toDisplayString($data.shotEnhancing ? "正在增强..." : "增强镜头提示词"),
                        1
                        /* TEXT */
                      )
                    ]),
                    _: 1
                    /* STABLE */
                  }, 8, ["loading", "onClick"]),
                  vue.createElementVNode("view", { class: "form-grid two-col top-gap" }, [
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "起始帧描述"),
                      vue.withDirectives(vue.createElementVNode(
                        "textarea",
                        {
                          "onUpdate:modelValue": _cache[27] || (_cache[27] = ($event) => $options.currentShot.startFrame.description = $event),
                          class: "field-textarea",
                          placeholder: "起始帧需要呈现什么",
                          "placeholder-class": "field-placeholder"
                        },
                        null,
                        512
                        /* NEED_PATCH */
                      ), [
                        [vue.vModelText, $options.currentShot.startFrame.description]
                      ])
                    ]),
                    vue.createElementVNode("view", { class: "form-group" }, [
                      vue.createElementVNode("text", { class: "field-label" }, "结束帧描述"),
                      vue.withDirectives(vue.createElementVNode(
                        "textarea",
                        {
                          "onUpdate:modelValue": _cache[28] || (_cache[28] = ($event) => $options.currentShot.endFrame.description = $event),
                          class: "field-textarea",
                          placeholder: "结束帧需要呈现什么",
                          "placeholder-class": "field-placeholder"
                        },
                        null,
                        512
                        /* NEED_PATCH */
                      ), [
                        [vue.vModelText, $options.currentShot.endFrame.description]
                      ])
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      loading: $data.frameLoadingKey === "startFrame",
                      onClick: _cache[29] || (_cache[29] = ($event) => $options.generateFrame("startFrame"))
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.frameLoadingKey === "startFrame" ? "正在生成..." : "生成起始帧"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading"]),
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      loading: $data.frameLoadingKey === "endFrame",
                      onClick: _cache[30] || (_cache[30] = ($event) => $options.generateFrame("endFrame"))
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.frameLoadingKey === "endFrame" ? "正在生成..." : "生成结束帧"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading"])
                  ]),
                  vue.createElementVNode("view", { class: "form-grid two-col top-gap" }, [
                    $options.currentShot.startFrame.image_url ? (vue.openBlock(), vue.createElementBlock("image", {
                      key: 0,
                      class: "preview-media",
                      src: $options.currentShot.startFrame.image_url,
                      mode: "aspectFill"
                    }, null, 8, ["src"])) : (vue.openBlock(), vue.createElementBlock("view", {
                      key: 1,
                      class: "empty-block small-empty"
                    }, [
                      vue.createElementVNode("text", null, "起始帧还未生成")
                    ])),
                    $options.currentShot.endFrame.image_url ? (vue.openBlock(), vue.createElementBlock("image", {
                      key: 2,
                      class: "preview-media",
                      src: $options.currentShot.endFrame.image_url,
                      mode: "aspectFill"
                    }, null, 8, ["src"])) : (vue.openBlock(), vue.createElementBlock("view", {
                      key: 3,
                      class: "empty-block small-empty"
                    }, [
                      vue.createElementVNode("text", null, "结束帧还未生成")
                    ]))
                  ]),
                  $options.taskState($options.currentShot) === "processing" ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "progress-card top-gap"
                  }, [
                    vue.createElementVNode("view", { class: "progress-track" }, [
                      vue.createElementVNode(
                        "view",
                        {
                          class: "progress-track__bar",
                          style: vue.normalizeStyle({ width: `${$options.taskProgressValue($options.currentShot)}%` })
                        },
                        null,
                        4
                        /* STYLE */
                      )
                    ]),
                    vue.createElementVNode(
                      "text",
                      { class: "meta-hint" },
                      "当前进度 " + vue.toDisplayString($options.taskProgressValue($options.currentShot)) + "%",
                      1
                      /* TEXT */
                    )
                  ])) : vue.createCommentVNode("v-if", true),
                  $options.currentShot.videoTask.message ? (vue.openBlock(), vue.createElementBlock(
                    "text",
                    {
                      key: 1,
                      class: "meta-hint top-gap"
                    },
                    vue.toDisplayString($options.currentShot.videoTask.message),
                    1
                    /* TEXT */
                  )) : vue.createCommentVNode("v-if", true),
                  vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                    vue.createVNode(_component_u_button, {
                      class: "primary-btn",
                      type: "primary",
                      loading: $data.videoLoading,
                      onClick: $options.generateCurrentVideo
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode(
                          vue.toDisplayString($data.videoLoading ? "正在提交任务..." : "生成视频"),
                          1
                          /* TEXT */
                        )
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["loading", "onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "secondary-btn",
                      onClick: $options.refreshCurrentTask
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("刷新任务")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"]),
                    vue.createVNode(_component_u_button, {
                      class: "ghost-btn",
                      onClick: $options.openExportSection
                    }, {
                      default: vue.withCtx(() => [
                        vue.createTextVNode("去导出管理")
                      ]),
                      _: 1
                      /* STABLE */
                    }, 8, ["onClick"])
                  ]),
                  $options.currentShot.videoUrl ? (vue.openBlock(), vue.createElementBlock("video", {
                    key: 2,
                    class: "preview-video top-gap",
                    src: $options.currentShot.videoUrl,
                    controls: "",
                    playsinline: ""
                  }, null, 8, ["src"])) : vue.createCommentVNode("v-if", true)
                ])) : vue.createCommentVNode("v-if", true)
              ],
              64
              /* STABLE_FRAGMENT */
            ))
          ],
          512
          /* NEED_PATCH */
        ), [
          [vue.vShow, $data.activeCreateTab === "director"]
        ])
      ])
    ]);
  }
  const ViewsProjectsIndex = /* @__PURE__ */ _export_sfc(_sfc_main$6, [["render", _sfc_render$5], ["__scopeId", "data-v-9d4bee16"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/projects/index.vue"]]);
  function exportVideo(payload) {
    return requestRaw({
      url: "/api/export-video",
      method: "POST",
      data: payload,
      timeout: 6e5,
      responseType: "arraybuffer",
      header: {
        "Content-Type": "application/json"
      }
    });
  }
  function safeText$2(value) {
    return String(value || "").trim();
  }
  function isBrowser() {
    return typeof window !== "undefined" && typeof document !== "undefined";
  }
  function resolveFilename(disposition, fallback = "download.bin") {
    const source = safeText$2(disposition);
    if (!source) {
      return fallback;
    }
    const utf8Match = source.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match && utf8Match[1]) {
      try {
        return decodeURIComponent(utf8Match[1]);
      } catch (error) {
        return utf8Match[1];
      }
    }
    const basicMatch = source.match(/filename="?([^"]+)"?/i);
    return basicMatch && basicMatch[1] ? basicMatch[1] : fallback;
  }
  function downloadBinaryInBrowser(data, filename, mimeType = "application/octet-stream") {
    if (!isBrowser()) {
      return false;
    }
    const blob = new Blob([data], { type: mimeType });
    const link = document.createElement("a");
    const url = window.URL.createObjectURL(blob);
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => window.URL.revokeObjectURL(url), 0);
    return true;
  }
  function downloadTextInBrowser(content, filename, mimeType = "text/plain;charset=utf-8") {
    if (!isBrowser()) {
      return false;
    }
    const blob = new Blob([content], { type: mimeType });
    const link = document.createElement("a");
    const url = window.URL.createObjectURL(blob);
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => window.URL.revokeObjectURL(url), 0);
    return true;
  }
  function clone(value, fallback) {
    try {
      return JSON.parse(JSON.stringify(value));
    } catch (error) {
      return fallback;
    }
  }
  function safeText$1(value) {
    return String(value || "").trim();
  }
  const _sfc_main$5 = {
    components: { LoadingProgress, UButton: __easycom_0 },
    data() {
      return {
        ...createDefaultProjectState(),
        initialized: false,
        progress: { visible: false, value: 0, label: "" },
        progressTimer: null,
        progressHideTimer: null,
        activeProjectCache: null,
        saving: false,
        exporting: false,
        selectedShotIndex: -1,
        finalEditText: ""
      };
    },
    computed: {
      hasProject() {
        return Boolean(this.currentProjectId);
      },
      selectedShot() {
        return this.selectedShotIndex >= 0 && this.selectedShotIndex < this.shots.length ? this.shots[this.selectedShotIndex] : null;
      },
      selectedShots() {
        return this.shots.filter((shot) => shot.includeInFinal !== false);
      },
      activeShots() {
        return this.selectedShots.filter((shot) => safeText$1(shot.videoUrl));
      },
      estimatedDurationSec() {
        return this.selectedShots.reduce((total, shot) => total + this.parseDurationToSeconds(shot.duration), 0);
      }
    },
    onShow() {
      if (!ensureAuth()) {
        return;
      }
      if (!this.initialized) {
        this.initializePage();
        return;
      }
      this.activeProjectCache = getProjectCache();
      if (this.hasProject || getCurrentProjectId()) {
        this.loadProject(true, true);
      }
    },
    onPullDownRefresh() {
      if (!ensureAuth()) {
        uni.stopPullDownRefresh();
        return;
      }
      this.refreshCurrentView();
    },
    onUnload() {
      this.clearProgressTimer();
    },
    methods: {
      showToast(message) {
        uni.showToast({ title: safeText$1(message) || "操作失败", icon: "none" });
      },
      clearProgressTimer() {
        if (this.progressTimer) {
          clearInterval(this.progressTimer);
          this.progressTimer = null;
        }
        if (this.progressHideTimer) {
          clearTimeout(this.progressHideTimer);
          this.progressHideTimer = null;
        }
      },
      startProgress(label) {
        this.clearProgressTimer();
        this.progress = { visible: true, value: 16, label: safeText$1(label) || "正在处理" };
        this.progressTimer = setInterval(() => {
          const currentValue = Number(this.progress.value || 0);
          const delta = currentValue < 60 ? 9 : currentValue < 84 ? 4 : 0;
          this.progress.value = Math.min(currentValue + delta, 90);
        }, 220);
      },
      finishProgress(label) {
        this.clearProgressTimer();
        this.progress.label = safeText$1(label) || this.progress.label || "已完成";
        this.progress.value = 100;
        this.progressHideTimer = setTimeout(() => {
          this.progress.visible = false;
          this.progress.value = 0;
        }, 320);
      },
      async runTask(label, handler, options = {}) {
        this.startProgress(label);
        try {
          const result = await handler();
          this.finishProgress(options.successText || "已完成");
          return result;
        } catch (error) {
          this.finishProgress(safeText$1(error && error.message) || options.failureText || "操作失败");
          throw error;
        }
      },
      normalizeShot(shot, index = 0) {
        const safeShot = shot && typeof shot === "object" ? clone(shot, {}) : {};
        const defaults = createEmptyShot(index + 1);
        return { ...defaults, ...safeShot, title: safeText$1(safeShot.title) || `镜头 ${index + 1}`, duration: safeText$1(safeShot.duration) || "5s", startFrame: { ...defaults.startFrame, ...safeShot.startFrame || {} }, endFrame: { ...defaults.endFrame, ...safeShot.endFrame || {} }, videoTask: { ...defaults.videoTask, ...safeShot.videoTask || {} } };
      },
      hydrateProject(project) {
        const next = applyProject(project);
        next.shots = (next.shots || []).map((shot, index) => this.normalizeShot(shot, index));
        Object.assign(this, next);
        this.selectedShotIndex = next.shots.length ? 0 : -1;
        this.finalEditText = this.readStoredFinalEditText() || this.buildFinalEditText();
        this.activeProjectCache = clone(project, {});
      },
      async fetchCurrentProject(forceRemote = false) {
        const project = await loadCurrentProject({ forceRemote });
        if (project) {
          this.hydrateProject(project);
        }
        return project;
      },
      async initializePage() {
        try {
          await this.runTask("正在同步导出内容", async () => {
            this.activeProjectCache = getProjectCache();
            if (getCurrentProjectId()) {
              await this.fetchCurrentProject(true);
            }
          }, { successText: "导出页已就绪" });
          this.initialized = true;
        } catch (error) {
          this.showToast(error.message || "初始化失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      async refreshCurrentView() {
        try {
          await this.runTask("正在刷新导出页", async () => {
            if (getCurrentProjectId()) {
              await this.fetchCurrentProject(true);
            }
          }, { successText: "导出页已刷新" });
        } catch (error) {
          this.showToast(error.message || "刷新失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      async loadProject(forceRemote = false, silent = false) {
        if (!this.hasProject && !getCurrentProjectId()) {
          return;
        }
        try {
          if (silent) {
            await this.fetchCurrentProject(forceRemote);
          } else {
            await this.runTask("正在同步当前项目", () => this.fetchCurrentProject(forceRemote), { successText: "项目数据已更新" });
          }
        } catch (error) {
          this.showToast(error.message || "加载项目失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      persistCurrentEpisodeState() {
        const key = ensureEpisodeState(this.episodeScripts, this.episodeShots, this.currentEpisodeNo);
        this.episodeShots[key] = clone(this.shots, []);
      },
      persistFinalEditText() {
        const filtered = (this.generatedData || []).filter((item) => item && item.type !== "final_edit_text");
        const text = safeText$1(this.finalEditText);
        if (text) {
          filtered.unshift({ id: `g_${Date.now()}`, type: "final_edit_text", createdAt: (/* @__PURE__ */ new Date()).toISOString(), payload: { text } });
        }
        this.generatedData = filtered;
      },
      readStoredFinalEditText() {
        const target = (this.generatedData || []).find((item) => item && item.type === "final_edit_text");
        return target && target.payload ? safeText$1(target.payload.text) : "";
      },
      async persistProjectState(silent = false) {
        const saveAction = async () => {
          this.persistCurrentEpisodeState();
          this.persistFinalEditText();
          const updated = await saveCurrentProjectState(this);
          const merged = { ...this.activeProjectCache || {}, ...updated, id: updated.id || this.currentProjectId };
          saveProjectCache(merged);
          this.activeProjectCache = merged;
          return merged;
        };
        if (silent) {
          return saveAction();
        }
        this.saving = true;
        try {
          return await this.runTask("正在保存导出草稿", saveAction, { successText: "导出草稿已保存" });
        } finally {
          this.saving = false;
        }
      },
      async saveProject() {
        try {
          await this.persistProjectState(false);
        } catch (error) {
          this.showToast(error.message || "保存失败");
        }
      },
      taskState(shot) {
        const status = safeText$1(shot && shot.videoTask && shot.videoTask.status).toLowerCase();
        if (safeText$1(shot && shot.videoUrl) || status === "succeeded") {
          return "succeeded";
        }
        if (["submitting", "submitted", "processing", "running", "pending"].includes(status)) {
          return "processing";
        }
        if (["failed", "error"].includes(status)) {
          return "failed";
        }
        return "idle";
      },
      taskStatusText(shot) {
        const state = this.taskState(shot);
        return state === "succeeded" ? "视频已就绪" : state === "processing" ? "视频生成中" : state === "failed" ? "视频生成失败" : "待生成";
      },
      parseDurationToSeconds(duration) {
        const text = safeText$1(duration).toLowerCase();
        if (!text) {
          return 0;
        }
        if (/^\d+$/.test(text)) {
          return Number(text);
        }
        const minuteMatch = text.match(/(\d+(?:\.\d+)?)\s*(min|分钟|m)/);
        if (minuteMatch) {
          return Math.round(Number(minuteMatch[1]) * 60);
        }
        const secondMatch = text.match(/(\d+(?:\.\d+)?)\s*(s|sec|秒)/);
        return secondMatch ? Math.round(Number(secondMatch[1])) : 0;
      },
      handleIncludeChange(event, index) {
        this.shots[index].includeInFinal = Boolean(event.detail.value);
      },
      buildFinalEditText() {
        return this.selectedShots.map((shot, index) => [`${index + 1}. ${safeText$1(shot.title) || `镜头 ${index + 1}`}`, safeText$1(shot.duration) ? `时长：${safeText$1(shot.duration)}` : "", safeText$1(shot.notes) ? `剪辑备注：${safeText$1(shot.notes)}` : "", safeText$1(shot.videoUrl) ? `视频：${safeText$1(shot.videoUrl)}` : "视频：待补齐"].filter(Boolean).join("\n")).join("\n\n");
      },
      syncFinalEditText() {
        this.finalEditText = this.buildFinalEditText();
      },
      downloadJson() {
        const payload = JSON.stringify({ project_name: this.currentProjectName, episode_no: this.currentEpisodeNo, final_edit_text: this.finalEditText, shots: this.selectedShots }, null, 2);
        const filename = `episode-${this.currentEpisodeNo}-final.json`;
        if (downloadTextInBrowser(payload, filename, "application/json;charset=utf-8")) {
          return;
        }
        uni.setClipboardData({ data: payload });
      },
      downloadTxt() {
        const payload = safeText$1(this.finalEditText) || this.buildFinalEditText();
        const filename = `episode-${this.currentEpisodeNo}-final.txt`;
        if (downloadTextInBrowser(payload, filename, "text/plain;charset=utf-8")) {
          return;
        }
        uni.setClipboardData({ data: payload });
      },
      async exportFinalVideo() {
        if (!this.activeShots.length) {
          this.showToast("没有可导出的镜头");
          return;
        }
        this.exporting = true;
        try {
          const response = await this.runTask("正在导出成片", async () => {
            await this.persistProjectState(true);
            return exportVideo({ shots: this.activeShots, episode_no: this.currentEpisodeNo });
          }, { successText: "导出文件已准备" });
          const headers = response.header || {};
          const disposition = headers["content-disposition"] || headers["Content-Disposition"] || "";
          const contentType = headers["content-type"] || headers["Content-Type"] || "video/mp4";
          const filename = resolveFilename(disposition, `episode-${this.currentEpisodeNo}-final.mp4`);
          if (!downloadBinaryInBrowser(response.data, filename, contentType)) {
            this.showToast("当前平台请在 H5 环境下载 MP4");
          }
        } catch (error) {
          this.showToast(error.message || "导出失败");
        } finally {
          this.exporting = false;
        }
      },
      goCreatePage() {
        uni.switchTab({ url: "/views/projects/index" });
      }
    }
  };
  function _sfc_render$4(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_LoadingProgress = vue.resolveComponent("LoadingProgress");
    const _component_u_button = resolveEasycom(vue.resolveDynamicComponent("u-button"), __easycom_0);
    return vue.openBlock(), vue.createElementBlock("view", { class: "studio-page" }, [
      vue.createVNode(_component_LoadingProgress, {
        visible: $data.progress.visible,
        value: $data.progress.value,
        label: $data.progress.label
      }, null, 8, ["visible", "value", "label"]),
      vue.createElementVNode("view", { class: "studio-page__bg" }),
      vue.createElementVNode("view", { class: "app-page studio-shell" }, [
        vue.createElementVNode("view", { class: "section-card page-head" }, [
          vue.createElementVNode("text", { class: "section-title" }, "视频导出管理"),
          vue.createElementVNode("text", { class: "section-subtitle" }, "整理入片镜头、补充剪辑说明，并导出 JSON、TXT 或 MP4。")
        ]),
        !$options.hasProject ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "section-card empty-block"
        }, [
          vue.createElementVNode("text", null, "先在动漫生成里打开一个项目，再来整理导出内容。"),
          vue.createVNode(_component_u_button, {
            class: "primary-btn top-gap",
            type: "primary",
            onClick: $options.goCreatePage
          }, {
            default: vue.withCtx(() => [
              vue.createTextVNode("去动漫生成")
            ]),
            _: 1
            /* STABLE */
          }, 8, ["onClick"])
        ])) : (vue.openBlock(), vue.createElementBlock(
          vue.Fragment,
          { key: 1 },
          [
            vue.createElementVNode("view", { class: "section-card" }, [
              vue.createElementVNode("view", { class: "section-head" }, [
                vue.createElementVNode("text", { class: "section-title" }, "导出概览"),
                vue.createVNode(_component_u_button, {
                  class: "secondary-btn mini-btn",
                  loading: $data.saving,
                  onClick: $options.saveProject
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(
                      vue.toDisplayString($data.saving ? "正在保存..." : "保存草稿"),
                      1
                      /* TEXT */
                    )
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["loading", "onClick"])
              ]),
              vue.createElementVNode("view", { class: "summary-grid" }, [
                vue.createElementVNode("view", { class: "summary-card" }, [
                  vue.createElementVNode("text", { class: "meta-label" }, "当前项目"),
                  vue.createElementVNode(
                    "text",
                    { class: "meta-value" },
                    vue.toDisplayString(_ctx.currentProjectName || "未命名项目"),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "meta-hint" },
                    "第 " + vue.toDisplayString(_ctx.currentEpisodeNo) + " 集",
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "summary-card tone-soft" }, [
                  vue.createElementVNode("text", { class: "meta-label" }, "导出统计"),
                  vue.createElementVNode(
                    "text",
                    { class: "meta-value" },
                    vue.toDisplayString($options.selectedShots.length) + " 个入片镜头",
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "meta-hint" },
                    "可导出 " + vue.toDisplayString($options.activeShots.length) + " · 预计 " + vue.toDisplayString($options.estimatedDurationSec) + " 秒",
                    1
                    /* TEXT */
                  )
                ])
              ])
            ]),
            vue.createElementVNode("view", { class: "section-card" }, [
              vue.createElementVNode("view", { class: "section-head" }, [
                vue.createElementVNode("text", { class: "section-title" }, "镜头导出清单"),
                vue.createVNode(_component_u_button, {
                  class: "secondary-btn mini-btn",
                  onClick: _cache[0] || (_cache[0] = ($event) => $options.loadProject(true))
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode("重新同步")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ]),
              !_ctx.shots.length ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "empty-block"
              }, [
                vue.createElementVNode("text", null, "当前项目还没有镜头，先去导演模块生成内容。")
              ])) : (vue.openBlock(), vue.createElementBlock("view", {
                key: 1,
                class: "list-stack"
              }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList(_ctx.shots, (shot, index) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      key: `export-${index}`,
                      class: "list-card list-card--stack",
                      onClick: ($event) => $data.selectedShotIndex = index
                    }, [
                      vue.createElementVNode("view", { class: "export-head" }, [
                        vue.createElementVNode("view", null, [
                          vue.createElementVNode(
                            "text",
                            { class: "list-card__title" },
                            vue.toDisplayString(shot.title || `镜头 ${index + 1}`),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "text",
                            { class: "list-card__desc" },
                            vue.toDisplayString(shot.duration || "5s") + " · " + vue.toDisplayString($options.taskStatusText(shot)),
                            1
                            /* TEXT */
                          )
                        ]),
                        vue.createElementVNode("switch", {
                          checked: shot.includeInFinal !== false,
                          color: "#7a9677",
                          onChange: ($event) => $options.handleIncludeChange($event, index)
                        }, null, 40, ["checked", "onChange"])
                      ]),
                      vue.createElementVNode("view", { class: "form-group" }, [
                        vue.createElementVNode("text", { class: "field-label" }, "视频链接"),
                        vue.withDirectives(vue.createElementVNode("input", {
                          "onUpdate:modelValue": ($event) => shot.videoUrl = $event,
                          class: "field-input",
                          type: "text",
                          placeholder: "https://...",
                          "placeholder-class": "field-placeholder",
                          "adjust-position": false
                        }, null, 8, ["onUpdate:modelValue"]), [
                          [vue.vModelText, shot.videoUrl]
                        ])
                      ]),
                      vue.createElementVNode("view", { class: "form-group no-gap" }, [
                        vue.createElementVNode("text", { class: "field-label" }, "剪辑备注"),
                        vue.withDirectives(vue.createElementVNode("input", {
                          "onUpdate:modelValue": ($event) => shot.notes = $event,
                          class: "field-input",
                          type: "text",
                          placeholder: "例如：结尾快切、字幕加重",
                          "placeholder-class": "field-placeholder",
                          "adjust-position": false
                        }, null, 8, ["onUpdate:modelValue"]), [
                          [vue.vModelText, shot.notes]
                        ])
                      ])
                    ], 8, ["onClick"]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ]))
            ]),
            $options.selectedShot ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "section-card"
            }, [
              vue.createElementVNode("text", { class: "section-title" }, "镜头预览"),
              $options.selectedShot.videoUrl ? (vue.openBlock(), vue.createElementBlock("video", {
                key: 0,
                class: "preview-video top-gap",
                src: $options.selectedShot.videoUrl,
                controls: "",
                playsinline: ""
              }, null, 8, ["src"])) : $options.selectedShot.startFrame && $options.selectedShot.startFrame.image_url ? (vue.openBlock(), vue.createElementBlock("image", {
                key: 1,
                class: "preview-video top-gap",
                src: $options.selectedShot.startFrame.image_url,
                mode: "aspectFill"
              }, null, 8, ["src"])) : (vue.openBlock(), vue.createElementBlock("view", {
                key: 2,
                class: "empty-block small-empty"
              }, [
                vue.createElementVNode("text", null, "当前镜头还没有可预览内容。")
              ]))
            ])) : vue.createCommentVNode("v-if", true),
            vue.createElementVNode("view", { class: "section-card" }, [
              vue.createElementVNode("view", { class: "section-head" }, [
                vue.createElementVNode("text", { class: "section-title" }, "最终成片文案"),
                vue.createVNode(_component_u_button, {
                  class: "ghost-btn mini-btn",
                  onClick: $options.syncFinalEditText
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode("根据镜头自动整理")
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["onClick"])
              ]),
              vue.withDirectives(vue.createElementVNode(
                "textarea",
                {
                  "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.finalEditText = $event),
                  class: "field-textarea json-textarea top-gap",
                  placeholder: "补充字幕、配乐、节奏和串联说明",
                  "placeholder-class": "field-placeholder"
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $data.finalEditText]
              ]),
              vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
                vue.createVNode(_component_u_button, {
                  class: "secondary-btn",
                  onClick: $options.downloadJson
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode("导出 JSON")
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["onClick"]),
                vue.createVNode(_component_u_button, {
                  class: "secondary-btn",
                  onClick: $options.downloadTxt
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode("导出 TXT")
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["onClick"]),
                vue.createVNode(_component_u_button, {
                  class: "primary-btn",
                  type: "primary",
                  loading: $data.exporting,
                  onClick: $options.exportFinalVideo
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(
                      vue.toDisplayString($data.exporting ? "正在导出..." : "导出 MP4"),
                      1
                      /* TEXT */
                    )
                  ]),
                  _: 1
                  /* STABLE */
                }, 8, ["loading", "onClick"])
              ])
            ])
          ],
          64
          /* STABLE_FRAGMENT */
        ))
      ])
    ]);
  }
  const ViewsExportIndex = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["render", _sfc_render$4], ["__scopeId", "data-v-ca040c2e"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/export/index.vue"]]);
  function getLLMConfig(process = "general") {
    return http.get("/api/llm-config", { process });
  }
  function updateLLMConfig(payload) {
    return http.post("/api/llm-config", payload);
  }
  function testLLM(payload) {
    return http.post("/api/test-llm", payload, { timeout: 12e4 });
  }
  const DEFAULT_CONFIG = { model: "", api_key: "", base_url: "", temperature: 0.7, max_tokens: 1e3, sdk_type: "openai" };
  function safeText(value) {
    return String(value || "").trim();
  }
  const _sfc_main$4 = {
    components: { LoadingProgress, UButton: __easycom_0 },
    data() {
      return {
        initialized: false,
        progress: { visible: false, value: 0, label: "" },
        progressTimer: null,
        progressHideTimer: null,
        loading: false,
        currentUser: "",
        projects: [],
        selectedProcess: "general",
        processOptions: [{ value: "general", label: "通用" }, { value: "script", label: "剧本" }, { value: "character", label: "角色" }, { value: "scene", label: "场景" }, { value: "video", label: "视频" }],
        llmConfig: { ...DEFAULT_CONFIG },
        llmLoading: false,
        llmSaving: false,
        llmTesting: false,
        testResult: { status: "", message: "" }
      };
    },
    computed: {
      workspaceAssetTotal() {
        return this.projects.reduce((total, project) => total + this.assetCount(project), 0);
      },
      workspaceShotTotal() {
        return this.projects.reduce((total, project) => total + this.shotCount(project), 0);
      },
      selectedProcessLabel() {
        const options = Array.isArray(this.processOptions) ? this.processOptions : [];
        const target = options.find((item) => item.value === this.selectedProcess);
        return target ? target.label : "通用";
      }
    },
    onShow() {
      if (!ensureAuth()) {
        return;
      }
      this.currentUser = getCurrentUser();
      if (!this.initialized) {
        this.initializePage();
        return;
      }
      this.refreshProfile(true);
    },
    onPullDownRefresh() {
      if (!ensureAuth()) {
        uni.stopPullDownRefresh();
        return;
      }
      this.refreshProfile();
    },
    onUnload() {
      this.clearProgressTimer();
    },
    methods: {
      showToast(message) {
        uni.showToast({ title: safeText(message) || "操作失败", icon: "none" });
      },
      clearProgressTimer() {
        if (this.progressTimer) {
          clearInterval(this.progressTimer);
          this.progressTimer = null;
        }
        if (this.progressHideTimer) {
          clearTimeout(this.progressHideTimer);
          this.progressHideTimer = null;
        }
      },
      startProgress(label) {
        this.clearProgressTimer();
        this.progress = { visible: true, value: 16, label: safeText(label) || "正在处理" };
        this.progressTimer = setInterval(() => {
          const currentValue = Number(this.progress.value || 0);
          const delta = currentValue < 60 ? 9 : currentValue < 84 ? 4 : 0;
          this.progress.value = Math.min(currentValue + delta, 90);
        }, 220);
      },
      finishProgress(label) {
        this.clearProgressTimer();
        this.progress.label = safeText(label) || this.progress.label || "已完成";
        this.progress.value = 100;
        this.progressHideTimer = setTimeout(() => {
          this.progress.visible = false;
          this.progress.value = 0;
        }, 320);
      },
      async runTask(label, handler, options = {}) {
        this.startProgress(label);
        try {
          const result = await handler();
          this.finishProgress(options.successText || "已完成");
          return result;
        } catch (error) {
          this.finishProgress(safeText(error && error.message) || options.failureText || "操作失败");
          throw error;
        }
      },
      assetCount(project) {
        return Array.isArray(project && project.assets) ? project.assets.length : 0;
      },
      shotCount(project) {
        return Array.isArray(project && project.shots) ? project.shots.length : 0;
      },
      buildConfigPayload() {
        return { ...this.llmConfig, process: this.selectedProcess, temperature: Number(this.llmConfig.temperature || DEFAULT_CONFIG.temperature), max_tokens: Number(this.llmConfig.max_tokens || DEFAULT_CONFIG.max_tokens) };
      },
      async fetchProjects() {
        const response = await listProjects();
        this.projects = Array.isArray(response) ? response : [];
        return this.projects;
      },
      async fetchConfig() {
        const response = await getLLMConfig(this.selectedProcess);
        this.llmConfig = { ...DEFAULT_CONFIG, ...response || {} };
        this.testResult = { status: "", message: "" };
        return this.llmConfig;
      },
      async initializePage() {
        try {
          await this.runTask("正在同步个人中心", async () => {
            await this.fetchProjects();
            await this.fetchConfig();
          }, { successText: "个人中心已就绪" });
          this.initialized = true;
        } catch (error) {
          this.showToast(error.message || "初始化失败");
        } finally {
          uni.stopPullDownRefresh();
        }
      },
      async refreshProfile(silent = false) {
        this.loading = true;
        try {
          if (silent) {
            await this.fetchProjects();
            await this.fetchConfig();
          } else {
            await this.runTask("正在刷新个人中心", async () => {
              await this.fetchProjects();
              await this.fetchConfig();
            }, { successText: "个人中心已刷新" });
          }
        } catch (error) {
          this.showToast(error.message || "刷新失败");
        } finally {
          this.loading = false;
          uni.stopPullDownRefresh();
        }
      },
      changeProcess(process) {
        if (!process || this.selectedProcess === process) {
          return;
        }
        this.selectedProcess = process;
        this.loadConfig(true);
      },
      async loadConfig(silent = false) {
        this.llmLoading = true;
        try {
          if (silent) {
            await this.fetchConfig();
          } else {
            await this.runTask("正在加载模型配置", () => this.fetchConfig(), { successText: "模型配置已更新" });
          }
        } catch (error) {
          this.testResult = { status: "error", message: error.message || "加载模型配置失败" };
        } finally {
          this.llmLoading = false;
        }
      },
      async saveConfig() {
        this.llmSaving = true;
        try {
          const response = await this.runTask("正在保存模型配置", () => updateLLMConfig(this.buildConfigPayload()), { successText: "模型配置已保存" });
          this.llmConfig = { ...DEFAULT_CONFIG, ...response || {} };
          this.testResult = { status: "success", message: "模型配置已保存" };
        } catch (error) {
          this.testResult = { status: "error", message: error.message || "保存模型配置失败" };
        } finally {
          this.llmSaving = false;
        }
      },
      async testConfig() {
        this.llmTesting = true;
        try {
          const response = await this.runTask("正在测试模型连接", () => testLLM(this.buildConfigPayload()), { successText: "模型连接测试完成" });
          this.testResult = { status: response.status || "success", message: response.message || "连接测试成功" };
        } catch (error) {
          this.testResult = { status: "error", message: error.message || "测试连接失败" };
        } finally {
          this.llmTesting = false;
        }
      },
      async logoutUser() {
        try {
          await logout();
        } catch (error) {
        }
        clearAuthSession();
        relaunchTo("/views/account/index");
      }
    }
  };
  function _sfc_render$3(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_LoadingProgress = vue.resolveComponent("LoadingProgress");
    const _component_u_button = resolveEasycom(vue.resolveDynamicComponent("u-button"), __easycom_0);
    return vue.openBlock(), vue.createElementBlock("view", { class: "studio-page" }, [
      vue.createVNode(_component_LoadingProgress, {
        visible: $data.progress.visible,
        value: $data.progress.value,
        label: $data.progress.label
      }, null, 8, ["visible", "value", "label"]),
      vue.createElementVNode("view", { class: "studio-page__bg" }),
      vue.createElementVNode("view", { class: "app-page studio-shell" }, [
        vue.createElementVNode("view", { class: "section-card page-head" }, [
          vue.createElementVNode("text", { class: "section-title" }, "个人中心"),
          vue.createElementVNode("text", { class: "section-subtitle" }, "查看工作空间概况、维护模型配置，并管理当前登录账户。")
        ]),
        vue.createElementVNode("view", { class: "section-card" }, [
          vue.createElementVNode("view", { class: "section-head" }, [
            vue.createElementVNode("text", { class: "section-title" }, "账户与空间")
          ]),
          vue.createElementVNode("view", { class: "summary-grid" }, [
            vue.createElementVNode("view", { class: "summary-card tone-soft" }, [
              vue.createElementVNode("text", { class: "meta-label" }, "工作空间概况"),
              vue.createElementVNode(
                "text",
                { class: "meta-value" },
                vue.toDisplayString($data.projects.length) + " 个项目",
                1
                /* TEXT */
              ),
              vue.createElementVNode(
                "text",
                { class: "meta-hint" },
                "资产 " + vue.toDisplayString($options.workspaceAssetTotal) + " · 镜头 " + vue.toDisplayString($options.workspaceShotTotal),
                1
                /* TEXT */
              )
            ])
          ])
        ]),
        vue.createElementVNode("view", { class: "section-card" }, [
          vue.createElementVNode("view", { class: "section-head" }, [
            vue.createElementVNode("text", { class: "section-title" }, "模型配置"),
            vue.createElementVNode(
              "text",
              { class: "info-chip" },
              vue.toDisplayString($options.selectedProcessLabel),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "segment-row no-top-gap" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($data.processOptions, (item) => {
                return vue.openBlock(), vue.createElementBlock("text", {
                  key: item.value,
                  class: vue.normalizeClass(["segment-pill", { active: $data.selectedProcess === item.value }]),
                  onClick: ($event) => $options.changeProcess(item.value)
                }, vue.toDisplayString(item.label), 11, ["onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ]),
          vue.createElementVNode("view", { class: "form-grid two-col top-gap" }, [
            vue.createElementVNode("view", { class: "form-group" }, [
              vue.createElementVNode("text", { class: "field-label" }, "SDK 类型"),
              vue.withDirectives(vue.createElementVNode(
                "input",
                {
                  "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.llmConfig.sdk_type = $event),
                  class: "field-input",
                  type: "text",
                  placeholder: "openai / dashscope",
                  "placeholder-class": "field-placeholder",
                  "adjust-position": false
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $data.llmConfig.sdk_type]
              ])
            ]),
            vue.createElementVNode("view", { class: "form-group" }, [
              vue.createElementVNode("text", { class: "field-label" }, "模型名称"),
              vue.withDirectives(vue.createElementVNode(
                "input",
                {
                  "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.llmConfig.model = $event),
                  class: "field-input",
                  type: "text",
                  placeholder: "请输入模型名称",
                  "placeholder-class": "field-placeholder",
                  "adjust-position": false
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $data.llmConfig.model]
              ])
            ])
          ]),
          vue.createElementVNode("view", { class: "form-group" }, [
            vue.createElementVNode("text", { class: "field-label" }, "API Key"),
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.llmConfig.api_key = $event),
                class: "field-input",
                type: "text",
                placeholder: "请输入 API Key",
                "placeholder-class": "field-placeholder",
                "adjust-position": false
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $data.llmConfig.api_key]
            ])
          ]),
          vue.createElementVNode("view", { class: "form-group" }, [
            vue.createElementVNode("text", { class: "field-label" }, "Base URL"),
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.llmConfig.base_url = $event),
                class: "field-input",
                type: "text",
                placeholder: "可选，自定义模型网关地址",
                "placeholder-class": "field-placeholder",
                "adjust-position": false
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $data.llmConfig.base_url]
            ])
          ]),
          vue.createElementVNode("view", { class: "form-grid two-col" }, [
            vue.createElementVNode("view", { class: "form-group" }, [
              vue.createElementVNode("text", { class: "field-label" }, "Temperature"),
              vue.withDirectives(vue.createElementVNode(
                "input",
                {
                  "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.llmConfig.temperature = $event),
                  class: "field-input",
                  type: "digit",
                  placeholder: "0.7",
                  "placeholder-class": "field-placeholder",
                  "adjust-position": false
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $data.llmConfig.temperature]
              ])
            ]),
            vue.createElementVNode("view", { class: "form-group" }, [
              vue.createElementVNode("text", { class: "field-label" }, "Max Tokens"),
              vue.withDirectives(vue.createElementVNode(
                "input",
                {
                  "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.llmConfig.max_tokens = $event),
                  class: "field-input",
                  type: "number",
                  placeholder: "1000",
                  "placeholder-class": "field-placeholder",
                  "adjust-position": false
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $data.llmConfig.max_tokens]
              ])
            ])
          ]),
          vue.createElementVNode("view", { class: "action-row compact-actions top-gap" }, [
            vue.createVNode(_component_u_button, {
              class: "secondary-btn",
              loading: $data.llmLoading,
              onClick: $options.loadConfig
            }, {
              default: vue.withCtx(() => [
                vue.createTextVNode(
                  vue.toDisplayString($data.llmLoading ? "正在加载..." : "重新加载"),
                  1
                  /* TEXT */
                )
              ]),
              _: 1
              /* STABLE */
            }, 8, ["loading", "onClick"]),
            vue.createVNode(_component_u_button, {
              class: "secondary-btn",
              loading: $data.llmSaving,
              onClick: $options.saveConfig
            }, {
              default: vue.withCtx(() => [
                vue.createTextVNode(
                  vue.toDisplayString($data.llmSaving ? "正在保存..." : "保存配置"),
                  1
                  /* TEXT */
                )
              ]),
              _: 1
              /* STABLE */
            }, 8, ["loading", "onClick"]),
            vue.createVNode(_component_u_button, {
              class: "primary-btn",
              type: "primary",
              loading: $data.llmTesting,
              onClick: $options.testConfig
            }, {
              default: vue.withCtx(() => [
                vue.createTextVNode(
                  vue.toDisplayString($data.llmTesting ? "正在测试..." : "测试连接"),
                  1
                  /* TEXT */
                )
              ]),
              _: 1
              /* STABLE */
            }, 8, ["loading", "onClick"])
          ]),
          $data.testResult.message ? (vue.openBlock(), vue.createElementBlock(
            "view",
            {
              key: 0,
              class: vue.normalizeClass(["message-card top-gap", $data.testResult.status === "success" ? "message-card--success" : "message-card--error"])
            },
            [
              vue.createElementVNode(
                "text",
                null,
                vue.toDisplayString($data.testResult.message),
                1
                /* TEXT */
              )
            ],
            2
            /* CLASS */
          )) : vue.createCommentVNode("v-if", true)
        ]),
        vue.createElementVNode("view", { class: "section-card" }, [
          vue.createElementVNode("text", { class: "section-title" }, "账户操作"),
          vue.createElementVNode("text", { class: "section-subtitle" }, "退出后会返回登录页，本地当前登录态会被清空。"),
          vue.createVNode(_component_u_button, {
            class: "danger-btn top-gap",
            type: "error",
            onClick: $options.logoutUser
          }, {
            default: vue.withCtx(() => [
              vue.createTextVNode("退出登录")
            ]),
            _: 1
            /* STABLE */
          }, 8, ["onClick"])
        ])
      ])
    ]);
  }
  const ViewsSettingsIndex = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["render", _sfc_render$3], ["__scopeId", "data-v-ab24c4f0"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/settings/index.vue"]]);
  const _sfc_main$3 = {
    onLoad() {
      uni.redirectTo({ url: "/views/projects/index?tab=create&panel=script" });
    }
  };
  function _sfc_render$2(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "redirect-page" }, [
      vue.createElementVNode("text", null, "正在进入剧本模块...")
    ]);
  }
  const ViewsScriptIndex = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["render", _sfc_render$2], ["__scopeId", "data-v-52eacc7f"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/script/index.vue"]]);
  const _sfc_main$2 = {
    onLoad() {
      uni.redirectTo({ url: "/views/projects/index?tab=create&panel=assets" });
    }
  };
  function _sfc_render$1(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "redirect-page" }, [
      vue.createElementVNode("text", null, "正在进入资产模块...")
    ]);
  }
  const ViewsAssetsIndex = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["render", _sfc_render$1], ["__scopeId", "data-v-8145de38"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/assets/index.vue"]]);
  const _sfc_main$1 = {
    onLoad() {
      uni.redirectTo({ url: "/views/projects/index?tab=create&panel=director" });
    }
  };
  function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "redirect-page" }, [
      vue.createElementVNode("text", null, "正在进入导演模块...")
    ]);
  }
  const ViewsWorkbenchIndex = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["render", _sfc_render], ["__scopeId", "data-v-d34c2368"], ["__file", "Y:/project/aiGenerate/ai-app/ai-app/views/workbench/index.vue"]]);
  __definePage("views/account/index", ViewsAccountIndex);
  __definePage("views/projects/index", ViewsProjectsIndex);
  __definePage("views/export/index", ViewsExportIndex);
  __definePage("views/settings/index", ViewsSettingsIndex);
  __definePage("views/script/index", ViewsScriptIndex);
  __definePage("views/assets/index", ViewsAssetsIndex);
  __definePage("views/workbench/index", ViewsWorkbenchIndex);
  const _sfc_main = {
    onLaunch() {
    }
  };
  const App = /* @__PURE__ */ _export_sfc(_sfc_main, [["__file", "Y:/project/aiGenerate/ai-app/ai-app/App.vue"]]);
  function createApp() {
    const app = vue.createVueApp(App);
    return {
      app
    };
  }
  const { app: __app__, Vuex: __Vuex__, Pinia: __Pinia__ } = createApp();
  uni.Vuex = __Vuex__;
  uni.Pinia = __Pinia__;
  __app__.provide("__globalStyles", __uniConfig.styles);
  __app__._component.mpType = "app";
  __app__._component.render = () => {
  };
  __app__.mount("#app");
})(Vue);
