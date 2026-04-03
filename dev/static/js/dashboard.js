/**
 * Dashboard Module v0.11.0
 * 获取和渲染 CP Dashboard 数据
 */

const Dashboard = {
    currentProjectId: null,
    data: null,

    // 初始化
    init(projectId) {
        this.currentProjectId = projectId;
        this.loadData();
    },

    // 加载数据
    async loadData() {
        try {
            const response = await fetch(`/api/dashboard/stats?project_id=${this.currentProjectId}`);
            const result = await response.json();

            if (result.success) {
                this.data = result.data;
                this.render();
            } else {
                this.showError(result.error || 'Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.showError('Failed to load dashboard data. Please check your connection.');
        }
    },

    // 渲染页面
    render() {
        // 渲染概览卡片
        this.renderOverview();

        // 渲染 Feature 分布
        this.renderFeatureChart();

        // 渲染 Priority 分布
        this.renderPriorityCards();

        // 渲染趋势图
        this.renderTrendChart();

        // 渲染列表
        this.renderTopUncovered();
        this.renderRecentActivity();
    },

    // 渲染概览卡片
    renderOverview() {
        const { overview } = this.data;
        const cards = [
            { key: 'total_cp', label: 'Total CP', class: 'total' },
            { key: 'covered_cp', label: 'Covered', class: 'covered' },
            { key: 'coverage_rate', label: 'Coverage', suffix: '%', class: 'rate' },
            { key: 'unlinked_cp', label: 'Unlinked', class: 'unlinked' }
        ];

        const container = document.getElementById('dashboard-overview');
        if (!container) return;

        container.innerHTML = cards.map(card => `
            <div class="overview-card ${card.class}">
                <div class="overview-value" data-count="${overview[card.key] || 0}">
                    ${overview[card.key] !== undefined ? overview[card.key] : '--'}
                    ${card.suffix || ''}
                </div>
                <div class="overview-label">${card.label}</div>
            </div>
        `).join('');
    },

    // 渲染 Feature 覆盖率图
    renderFeatureChart() {
        const { by_feature } = this.data;
        const container = document.getElementById('feature-chart');
        if (!container) return;

        if (!by_feature || by_feature.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No data available</div>';
            return;
        }

        // 按覆盖率排序
        const sorted = [...by_feature].sort((a, b) => b.rate - a.rate);

        container.innerHTML = sorted.map(item => {
            const level = item.rate >= 80 ? 'high' : (item.rate >= 50 ? 'medium' : 'low');
            return `
                <div class="feature-bar-item">
                    <div class="feature-bar-header">
                        <span class="feature-name">${this.escapeHtml(item.feature)}</span>
                        <span class="feature-rate">${item.rate.toFixed(1)}%</span>
                    </div>
                    <div class="feature-bar">
                        <div class="feature-bar-fill ${level}" style="width: ${item.rate}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // 渲染 Priority 卡片
    renderPriorityCards() {
        const { by_priority } = this.data;
        const container = document.getElementById('priority-cards');
        if (!container) return;

        const priorities = [
            { key: 'P0', color: 'p0' },
            { key: 'P1', color: 'p1' },
            { key: 'P2', color: 'p2' }
        ];

        container.innerHTML = priorities.map(p => {
            const data = by_priority[p.key] || { total: 0, covered: 0, rate: 0 };
            return `
                <div class="priority-card">
                    <div class="priority-dot ${p.color}"></div>
                    <div class="priority-info">
                        <div class="priority-label">${p.key} Priority</div>
                        <div class="priority-bar">
                            <div class="priority-bar-fill ${p.color}" style="width: ${data.rate}%"></div>
                        </div>
                    </div>
                    <div class="priority-value">${data.covered} / ${data.total}</div>
                </div>
            `;
        }).join('');
    },

    // 渲染趋势图
    renderTrendChart() {
        const { trend } = this.data;
        const container = document.getElementById('trend-chart');
        if (!container) return;

        if (!trend || trend.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No trend data available</div>';
            return;
        }

        // 计算 SVG 坐标
        const width = container.offsetWidth || 600;
        const height = 200;
        const padding = { top: 20, right: 20, bottom: 40, left: 50 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        const rates = trend.map(d => d.rate);
        const minRate = Math.floor(Math.min(...rates) / 10) * 10;
        const maxRate = Math.ceil(Math.max(...rates) / 10) * 10;
        const range = maxRate - minRate || 10;

        const xStep = chartWidth / Math.max(trend.length - 1, 1);
        const yScale = (v) => padding.top + chartHeight - ((v - minRate) / range) * chartHeight;

        // 生成折线路径
        const pathD = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const y = yScale(d.rate);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(' ');

        // 生成圆点
        const dots = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const y = yScale(d.rate);
            return `<circle class="trend-dot" cx="${x}" cy="${y}" r="4" />`;
        }).join('');

        // 生成 X 轴标签
        const labels = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const date = new Date(d.date);
            const label = `${date.getMonth() + 1}/${date.getDate()}`;
            return `<text class="trend-label" x="${x}" y="${height - 10}" text-anchor="middle">${label}</text>`;
        }).join('');

        // 生成 Y 轴标签
        const yLabels = [minRate, (minRate + maxRate) / 2, maxRate].map(v => {
            const y = yScale(v);
            return `<text class="trend-label" x="${padding.left - 10}" y="${y + 4}" text-anchor="end">${Math.round(v)}%</text>`;
        }).join('');

        container.innerHTML = `
            <svg class="trend-svg" viewBox="0 0 ${width} ${height}">
                <!-- Y 轴 -->
                <line class="trend-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" />
                ${yLabels}
                <!-- X 轴 -->
                <line class="trend-axis" x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" />
                <!-- 折线 -->
                <path class="trend-line" d="${pathD}" />
                <!-- 数据点 -->
                ${dots}
                <!-- 标签 -->
                ${labels}
            </svg>
        `;
    },

    // 渲染 Top 5 未覆盖
    renderTopUncovered() {
        const { top_uncovered } = this.data;
        const container = document.getElementById('top-uncovered');
        if (!container) return;

        if (!top_uncovered || top_uncovered.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">All CPs are covered</div>';
            return;
        }

        const priorityColors = { P0: '#ef4444', P1: '#f59e0b', P2: '#22c55e' };

        container.innerHTML = top_uncovered.map(item => `
            <div class="list-item" onclick="Dashboard.jumpToCP(${item.id})">
                <div class="list-icon" style="background: ${priorityColors[item.priority] || '#a1a1aa'}"></div>
                <div class="list-content">
                    <div class="list-title">${this.escapeHtml(item.name)}</div>
                    <div class="list-meta">${this.escapeHtml(item.feature)}</div>
                </div>
                <div class="list-tags">
                    <span class="list-tag" style="background: ${priorityColors[item.priority] || '#a1a1aa'}20; color: ${priorityColors[item.priority] || '#a1a1aa'}">${item.priority}</span>
                </div>
            </div>
        `).join('');
    },

    // 渲染 Recent Activity
    renderRecentActivity() {
        const { recent_activity } = this.data;
        const container = document.getElementById('recent-activity');
        if (!container) return;

        if (!recent_activity || recent_activity.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No recent activity</div>';
            return;
        }

        const typeConfig = {
            cp_added: { icon: '+', text: (c) => `${c} new CPs added` },
            cp_linked: { icon: '\u2192', text: (c) => `${c} CPs linked to TCs` },
            cp_covered: { icon: '\u2713', text: (c) => `${c} CPs marked covered` },
            tc_pass: { icon: '\u2713', text: (c) => `${c} TCs passed` },
            milestone: { icon: '\u2605', text: (c) => `Milestone updated` }
        };

        container.innerHTML = recent_activity.map(item => {
            const config = typeConfig[item.type] || { icon: '\u2022', text: () => 'Update' };
            const time = this.formatTime(item.timestamp);

            return `
                <div class="activity-item">
                    <div class="activity-icon">${config.icon}</div>
                    <div class="activity-content">
                        <div class="activity-text">${config.text(item.count)}</div>
                        <div class="activity-time">${time}</div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // 跳转到 CP 详情
    jumpToCP(cpId) {
        // 切换到 CP Tab
        switchTab('cp', null);
        setTimeout(() => {
            const el = document.querySelector(`tr[data-cp-id="${cpId}"]`);
            if (el) {
                el.classList.add('cp-highlight');
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(() => el.classList.remove('cp-highlight'), 3000);
            }
        }, 100);
    },

    // 工具函数
    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (hours < 1) return 'Just now';
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;

        return `${date.getMonth() + 1}/${date.getDate()}`;
    },

    showError(message) {
        const container = document.getElementById('dashboard-content');
        if (!container) return;
        container.innerHTML = `
            <div class="dashboard-empty">
                <div class="dashboard-empty-icon">\u26A0\uFE0F</div>
                <div>${this.escapeHtml(message)}</div>
            </div>
        `;
    }
};

// 初始化 Dashboard (供外部调用)
window.initDashboard = function(projectId) {
    Dashboard.init(projectId);
};
