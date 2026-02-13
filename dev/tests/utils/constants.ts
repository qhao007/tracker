/**
 * 常量定义
 */

// 超时配置
export const TIMEOUT = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 10000,
  EXTRA_LONG: 30000,
  NAVIGATION: 30000,
  ACTION: 5000,
};

// 重试配置
export const RETRY = {
  DEFAULT: 2,
  CI: 3,
};

// 选择器定义
export const SELECTORS = {
  // 公共选择器
  MODAL: '.modal, [class*="modal"]',
  MODAL_CLOSE: '.modal-close, [class*="close"]',
  BUTTON_PRIMARY: '.btn-primary, [class*="btn-primary"]',
  BUTTON_SECONDARY: '.btn-secondary, [class*="btn-secondary"]',

  // 项目相关
  PROJECT_SELECTOR: '#projectSelector',
  PROJECT_MODAL: '#projectModal',
  PROJECT_INPUT: '#newProjectName',

  // CP 相关
  CP_TABLE: '.cp-table',
  CP_MODAL: '#cpModal',
  CP_FEATURE: '#cpFeature',
  CP_COVER_POINT: '#cpCoverPoint',
  CP_PRIORITY: '#cpPriority',

  // TC 相关
  TC_TABLE: '.tc-table',
  TC_MODAL: '#tcModal',
  TC_TESTBENCH: '#tcTestbench',
  TC_TEST_NAME: '#tcTestName',
  TC_STATUS: '.status-select',
};

// 状态常量
export const STATUS = {
  TC: {
    PASS: 'Pass',
    FAIL: 'Fail',
    BLOCKED: 'Blocked',
    NOT_RUN: 'Not Run',
    SKIP: 'Skip',
  },
  PRIORITY: {
    P0: 'P0',
    P1: 'P1',
    P2: 'P2',
    P3: 'P3',
  },
};

// 分类常量
export const CATEGORY = {
  FUNCTIONAL: 'Functional',
  PERFORMANCE: 'Performance',
  STRESS: 'Stress',
  REGRESSION: 'Regression',
  SMOKE: 'Smoke',
};

// DV Milestone 常量
export const DV_MILESTONE = {
  RTL: 'RTL',
  GATE: 'Gate',
  SYNTHESIS: 'Synthesis',
  PT: 'PT',
  SIGN_OFF: 'Sign-off',
};

// API 端点
export const API_ENDPOINTS = {
  PROJECTS: '/api/projects',
  CP: '/api/cp',
  TC: '/api/tc',
  CONNECTIONS: '/api/connections',
  STATS: '/api/stats',
  HEALTH: '/api/health',
};

// 消息定义
export const MESSAGES = {
  SUCCESS: {
    CREATE_SUCCESS: '创建成功',
    UPDATE_SUCCESS: '更新成功',
    DELETE_SUCCESS: '删除成功',
  },
  ERROR: {
    CREATE_ERROR: '创建失败',
    UPDATE_ERROR: '更新失败',
    DELETE_ERROR: '删除失败',
    VALIDATION_ERROR: '验证失败',
    NETWORK_ERROR: '网络错误',
  },
  CONFIRM: {
    DELETE: '确定要删除吗？',
    CANCEL: '确定要取消吗？',
  },
};

// 测试数据模板
export const TEST_DATA_TEMPLATES = {
  LONG_STRING: 'A'.repeat(500),
  SPECIAL_CHARS: '!@#$%^&*()_+-=[]{}|;\':",./<>?',
  EMOJIS: '😊🔥🎉🚀✨💯',
  WHITESPACE: '   \t\n\r   ',
  UNICODE: '中文测试 🎯 عربى русский',
};

// 页面 URL
export const URLS = {
  DEV: 'http://localhost:8081',
  PROD: 'http://localhost:8080',
  TEST: 'http://localhost:8081',
};

// 浏览器配置
export const BROWSER = {
  DEFAULT_VIEWPORT: { width: 1280, height: 720 },
  HEADLESS: true,
};

// 测试标记
export const TAGS = {
  SMOKE: '@smoke',
  REGRESSION: '@regression',
  CRITICAL: '@critical',
  SLOW: '@slow',
  WIP: '@wip',
  SKIP: '@skip',
};
