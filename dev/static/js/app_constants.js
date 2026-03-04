/**
 * Tracker 应用常量定义
 * v0.8.3 - 前端常量管理
 * 
 * 所有前端常量统一在此文件管理，便于维护和修改
 */

// ==================== 用户/会话常量 ====================
const SESSION_KEYS = {
    USER: 'currentUser',
    PROJECT: 'currentProject',
    PROJECT_ID: 'currentProjectId'
};

// ==================== API 端点常量 ====================
const API_ENDPOINTS = {
    // 认证
    LOGIN: '/api/login',
    LOGOUT: '/api/logout',
    LOGIN_STATUS: '/api/login-status',
    
    // 项目
    PROJECTS: '/api/projects',
    PROJECT_STATS: '/api/stats',
    
    // Cover Points
    COVER_POINTS: '/api/cover-points',
    
    // Test Cases
    TEST_CASES: '/api/tc',
    
    // 进度
    PROGRESS: '/api/progress',
    
    // 用户管理
    USERS: '/api/users',
    
    // 导入导出
    IMPORT: '/api/import',
    EXPORT: '/api/export',
    
    // 备份恢复
    BACKUP: '/api/backup'
};

// ==================== UI 常量 ====================
const UI_CONSTANTS = {
    // 分页
    DEFAULT_PAGE_SIZE: 50,
    
    // 日期格式
    DATE_FORMAT: 'YYYY-MM-DD',
    
    // 超时设置
    FETCH_TIMEOUT: 30000,
    API_TIMEOUT: 10000,
    
    // 本地存储键
    LOCAL_STORAGE: {
        LAST_PROJECT_ID: 'tracker_last_project_id'
    },
    
    // 角色
    ROLES: {
        ADMIN: 'admin',
        USER: 'user',
        GUEST: 'guest'
    },
    
    // Tab
    TABS: {
        CP: 'cp',
        TC: 'tc',
        PROGRESS: 'progress'
    },
    
    // 状态
    STATUS: {
        PASS: 'PASS',
        FAIL: 'FAIL',
        BLOCKED: 'BLOCKED',
        N/A: 'N/A',
        NOT_RUN: 'NOT_RUN'
    },
    
    // 优先级
    PRIORITY: {
        P0: 'P0',
        P1: 'P1',
        P2: 'P2',
        P3: 'P3'
    }
};

// ==================== 消息常量 ====================
const MESSAGES = {
    // 错误消息
    ERRORS: {
        PROJECT_NAME_REQUIRED: '请输入项目名称',
        DATE_REQUIRED: '请输入日期',
        PROJECT_CREATE_FAILED: '项目创建失败',
        LOGIN_FAILED: '登录失败',
        NETWORK_ERROR: '网络错误'
    },
    
    // 确认消息
    CONFIRM: {
        PROJECT_DELETE: '确定要删除项目吗？此操作不可恢复。',
        SNAPSHOT_DELETE: '确定要删除这个快照吗？'
    },
    
    // 成功消息
    SUCCESS: {
        PROJECT_CREATED: '项目创建成功',
        PROJECT_DELETED: '项目已删除',
        SAVED: '保存成功'
    }
};

// ==================== 颜色常量 ====================
const COLORS = {
    // 状态颜色
    STATUS: {
        PASS: '#4CAF50',
        FAIL: '#f44336',
        BLOCKED: '#ff9800',
        NOT_RUN: '#9e9e9e',
        N/A: '#607d8b'
    },
    
    // 优先级颜色
    PRIORITY: {
        P0: '#f44336',
        P1: '#ff9800',
        P2: '#2196F3',
        P3: '#9e9e9e'
    },
    
    // 覆盖率颜色
    COVERAGE: {
        HIGH: '#4CAF50',    // > 80%
        MEDIUM: '#ff9800',  // 50-80%
        LOW: '#f44336'      // < 50%
    }
};

// 导出供外部使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SESSION_KEYS,
        API_ENDPOINTS,
        UI_CONSTANTS,
        MESSAGES,
        COLORS
    };
}
