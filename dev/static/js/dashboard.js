/**
 * Dashboard Module v0.12.0
 * 4-Tab Structure: Overview / Coverage Holes / Owner Distribution / Coverage Matrix
 */

const Dashboard = {
    currentProjectId: null,
    currentTab: 'overview',
    currentMode: 'tc_cp',  // v0.13.0: 'tc_cp' or 'fc_cp'
    data: null,
    holesData: null,
    ownerData: null,
    matrixData: null,

    // Tab badges
    tabBadges: {
        holes: { critical: 0, warning: 0 },
        owner: { unassigned: 0 }
    },

    // Modal event handlers
    modalEventHandlers: {
        escHandler: null,
        backdropClickHandler: null
    },

    // 初始化
    init(projectId) {
        this.currentProjectId = projectId;
        this.loadAllData();
        this.setupModalListeners();
    },

    // 设置 Modal 事件监听 (ESC 和遮罩点击关闭)
    setupModalListeners() {
        const dashboardModal = document.getElementById('dashboard-modal');
        if (!dashboardModal) return;

        // ESC 键关闭
        this.modalEventHandlers.escHandler = (e) => {
            if (e.key === 'Escape' && dashboardModal.classList.contains('active')) {
                Dashboard.closeModal();
            }
        };

        // 遮罩点击关闭
        this.modalEventHandlers.backdropClickHandler = (e) => {
            if (e.target === dashboardModal) {
                Dashboard.closeModal();
            }
        };

        document.addEventListener('keydown', this.modalEventHandlers.escHandler);
        dashboardModal.addEventListener('click', this.modalEventHandlers.backdropClickHandler);
    },

    // 关闭 Modal
    closeModal() {
        const modal = document.getElementById('dashboard-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    },

    // 显示 Modal
    showModal() {
        const modal = document.getElementById('dashboard-modal');
        if (modal) {
            modal.style.display = 'flex';  // Override inline display:none
            modal.classList.add('active');
        }
    },

    // 加载所有数据
    async loadAllData() {
        try {
            // 并行加载所有数据
            const [statsRes, holesRes, ownerRes, matrixRes] = await Promise.all([
                fetch(`/api/dashboard/stats?project_id=${this.currentProjectId}`),
                fetch(`/api/dashboard/coverage-holes?project_id=${this.currentProjectId}`),
                fetch(`/api/dashboard/owner-stats?project_id=${this.currentProjectId}`),
                fetch(`/api/dashboard/coverage-matrix?project_id=${this.currentProjectId}`)
            ]);

            const [stats, holes, owner, matrix] = await Promise.all([
                statsRes.json(),
                holesRes.json(),
                ownerRes.json(),
                matrixRes.json()
            ]);

            if (stats.success) {
                this.data = stats.data;
                // v0.13.0: 设置当前模式
                this.currentMode = stats.data.mode || 'tc_cp';
            }
            if (holes.success) {
                this.holesData = holes.data;
                this.tabBadges.holes.critical = holes.data.critical?.length || 0;
                this.tabBadges.holes.warning = (holes.data.warning?.length || 0) + (holes.data.attention?.length || 0);
            }
            if (owner.success) {
                this.ownerData = owner.data;
                this.tabBadges.owner.unassigned = owner.data.summary?.unassigned_tc_count || 0;
            }
            if (matrix.success) this.matrixData = matrix.data;

            this.render();
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.showError('Failed to load dashboard data');
        }
    },

    // 切换 Tab
    switchTab(tabName) {
        this.currentTab = tabName;
        // Update tab buttons
        document.querySelectorAll('.dashboard-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        // Update tab content
        document.querySelectorAll('.dashboard-tab-content').forEach(content => {
            content.classList.toggle('active', content.dataset.tab === tabName);
        });
        // Re-render the specific tab
        this.renderTab(tabName);
    },

    // 渲染页面
    render() {
        this.updateTabBadges();
        this.renderTab('overview');
    },

    // 渲染指定 Tab
    renderTab(tabName) {
        switch (tabName) {
            case 'overview':
                this.renderOverviewTab();
                break;
            case 'holes':
                this.renderHolesTab();
                break;
            case 'owner':
                this.renderOwnerTab();
                break;
            case 'matrix':
                this.renderMatrixTab();
                break;
        }
    },

    // 更新 Tab 徽章
    updateTabBadges() {
        const criticalBadge = document.querySelector('.dashboard-tab[data-tab="holes"] .badge-critical');
        const ownerBadge = document.querySelector('.dashboard-tab[data-tab="owner"] .badge-info');

        if (criticalBadge) {
            const total = this.tabBadges.holes.critical + this.tabBadges.holes.warning;
            criticalBadge.textContent = total > 0 ? total : '';
            criticalBadge.style.display = total > 0 ? 'inline-flex' : 'none';
        }
    },

    // ===== Tab 1: 概览 =====
    renderOverviewTab() {
        if (!this.data) return;

        const { overview, trend, by_feature } = this.data;

        // 渲染概览卡片 (3 cards: Covered, Unlinked, Pass Rate)
        this.renderOverviewCards(overview);

        // 渲染趋势图
        this.renderTrendChart(trend);

        // 渲染空洞摘要
        this.renderHolesSummary();

        // 渲染 Owner 摘要
        this.renderOwnerSummary();

        // 渲染矩阵预览
        this.renderMatrixPreview();
    },

    renderOverviewCards(overview) {
        const container = document.getElementById('dashboard-overview');
        if (!container) return;

        // TC Pass Rate calculation
        const tcPassRate = overview.tc_pass_rate !== undefined
            ? overview.tc_pass_rate
            : (overview.tc_pass && overview.tc_total
                ? Math.round((overview.tc_pass / overview.tc_total) * 100) : 0);

        // v0.12.0: 周环比变化 (§6)
        // 注意: unlinked 的 week_change 语义与 covered/tc_pass_rate 相反
        // - covered_cp 增加 = 好 = 绿色, 减少 = 坏 = 红色
        // - unlinked 增加 = 坏 = 红色, 减少 = 好 = 绿色
        // - tc_pass_rate 增加 = 好 = 绿色, 减少 = 坏 = 红色
        const weekChange = overview.week_change || {};
        const getChangeDisplay = (change, suffix = '', higherIsBetter = true) => {
            if (change === null || change === undefined) return { text: '--', cls: '' };
            const sign = change > 0 ? '↑' : change < 0 ? '↓' : '';
            const value = change > 0 ? `+${change}` : change.toString();
            // higherIsBetter=true: 上升=绿, 下降=红
            // higherIsBetter=false: 上升=红, 下降=绿
            const cls = change === 0 ? '' : (change > 0 === higherIsBetter) ? 'positive' : 'negative';
            return { text: `${sign}${value}${suffix}`, cls };
        };

        const coveredChange = getChangeDisplay(weekChange.covered_cp);
        const unlinkedChange = getChangeDisplay(weekChange.unlinked_cp, '', false); // false = 上升是坏的
        const passRateChange = getChangeDisplay(weekChange.tc_pass_rate, '%');

        // v0.13.0: 根据模式设置标签
        // 规格书节 4.1: 前端展示标签保持一致（CP Covered, Unlinked, TC Pass Rate）
        // 不区分 TC-CP/FC-CP 模式
        const mode = this.currentMode;
        const isFcCpMode = mode === 'fc_cp';

        // v0.13.0: unlinked 的 week_change 不显示（语义不明确）
        // - TC-CP 模式：unlinked = 没有关联 TC 的 CP
        // - FC-CP 模式：unlinked = 没有关联 FC 的 CP
        // 两种模式下 unlinked 变化都不能准确反映系统健康状况
        const unlinkedChangeDisplay = { text: '--', cls: '' };

        // 第三个卡片：统一显示 TC Pass Rate（TC-CP 和 FC-CP 模式都显示 TC 数据）
        const thirdCardLabel = 'TC Pass Rate';
        const thirdCardChange = passRateChange;

        const cards = [
            {
                key: 'covered',
                label: 'Covered',
                value: `${overview.covered_cp || 0}/${overview.total_cp || 0}`,
                suffix: '',
                change: coveredChange,
                class: 'covered',
                icon: '✓'
            },
            {
                key: 'unlinked',
                label: 'Unlinked',
                value: overview.unlinked_cp || 0,
                suffix: '',
                change: unlinkedChangeDisplay,
                class: 'unlinked',
                icon: '○'
            },
            {
                key: 'pass_rate',
                label: thirdCardLabel,
                value: tcPassRate,
                suffix: '%',
                change: thirdCardChange,
                class: 'pass-rate',
                icon: '%'
            }
        ];

        container.innerHTML = cards.map(card => `
            <div class="overview-card ${card.class}">
                <div class="overview-value">
                    ${card.value}${card.suffix}
                    <span class="overview-change ${card.change.cls}">${card.change.text}</span>
                </div>
                <div class="overview-label">${card.label}</div>
            </div>
        `).join('');
    },

    renderTrendChart(trend) {
        const container = document.getElementById('trend-chart');
        if (!container) return;

        if (!trend || trend.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No trend data</div>';
            return;
        }

        const width = container.offsetWidth || 600;
        const height = 200;
        const padding = { top: 20, right: 20, bottom: 40, left: 50 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        const rates = trend.map(d => d.rate);
        const minRate = Math.floor(Math.min(...rates, 0) / 10) * 10;
        const maxRate = Math.ceil(Math.max(...rates, 100) / 10) * 10;
        const range = maxRate - minRate || 10;

        const xStep = chartWidth / Math.max(trend.length - 1, 1);
        const yScale = (v) => padding.top + chartHeight - ((v - minRate) / range) * chartHeight;

        const pathD = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const y = yScale(d.rate);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(' ');

        const dots = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const y = yScale(d.rate);
            return `<circle class="trend-dot" cx="${x}" cy="${y}" r="4" />`;
        }).join('');

        const labels = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const date = new Date(d.date);
            const label = `${date.getMonth() + 1}/${date.getDate()}`;
            return `<text class="trend-label" x="${x}" y="${height - 10}" text-anchor="middle">${label}</text>`;
        }).join('');

        const yLabels = [minRate, (minRate + maxRate) / 2, maxRate].map(v => {
            const y = yScale(v);
            return `<text class="trend-label" x="${padding.left - 10}" y="${y + 4}" text-anchor="end">${Math.round(v)}%</text>`;
        }).join('');

        container.innerHTML = `
            <svg class="trend-svg" viewBox="0 0 ${width} ${height}">
                <line class="trend-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" />
                ${yLabels}
                <line class="trend-axis" x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" />
                <path class="trend-line" d="${pathD}" />
                ${dots}
                ${labels}
            </svg>
        `;
    },

    renderHolesSummary() {
        const container = document.getElementById('holes-summary');
        if (!container) return;

        if (!this.holesData) {
            container.innerHTML = '<div class="dashboard-empty">Loading...</div>';
            return;
        }

        const { critical, warning, attention } = this.holesData;
        const total = (critical?.length || 0) + (warning?.length || 0) + (attention?.length || 0);

        if (total === 0) {
            container.innerHTML = '<div class="dashboard-empty">No coverage holes</div>';
            return;
        }

        // 概览页空洞摘要: 只显示 critical 等级的前 5 条 (§3.2)
        const items = (critical?.slice(0, 5) || []).map(h => ({ ...h, severity: 'critical' }));

        const priorityColors = { P0: '#ef4444', P1: '#f59e0b', P2: '#22c55e' };

        container.innerHTML = `
            <div class="summary-card-header">
                <span class="summary-card-title">Top Coverage Holes</span>
                <span class="summary-card-link" onclick="Dashboard.switchTab('holes')">View all →</span>
            </div>
            ${items.map(item => `
                <div class="hole-card ${item.severity}" onclick="Dashboard.showHoleDetail(${item.cp_id})">
                    <div class="hole-card-name">${this.escapeHtml(item.cp_name)}</div>
                    <div class="hole-card-meta">
                        <span class="hole-card-stat">${item.feature}</span>
                        <span class="hole-card-stat" style="color: ${priorityColors[item.priority] || '#a1a1aa'}">${item.priority}</span>
                        <span class="hole-card-stat">${item.linked_tcs?.length || 0} TC</span>
                    </div>
                </div>
            `).join('')}
        `;
    },

    renderOwnerSummary() {
        const container = document.getElementById('owner-summary');
        if (!container) return;

        if (!this.ownerData || !this.ownerData.owners) {
            container.innerHTML = '<div class="dashboard-empty">Loading...</div>';
            return;
        }

        const topOwners = this.ownerData.owners.slice(0, 5);

        if (topOwners.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No TC data</div>';
            return;
        }

        container.innerHTML = `
            <div class="summary-card-header">
                <span class="summary-card-title">Top Owners</span>
                <span class="summary-card-link" onclick="Dashboard.switchTab('owner')">View all →</span>
            </div>
            ${topOwners.map(owner => {
                const passRate = owner.tc_total > 0
                    ? Math.round((owner.tc_pass / owner.tc_total) * 100) : 0;
                const rateClass = passRate >= 90 ? 'excellent' : (passRate >= 70 ? 'normal' : 'warning');
                return `
                    <div class="list-item" onclick="Dashboard.showOwnerDetail('${this.escapeHtml(owner.owner)}')">
                        <div class="list-icon" style="background: var(--color-primary)"></div>
                        <div class="list-content">
                            <div class="list-title">${this.escapeHtml(owner.owner)}</div>
                            <div class="list-meta">${owner.tc_total} TC</div>
                        </div>
                        <div class="owner-pass-rate ${rateClass}">
                            ${passRate}%
                        </div>
                    </div>
                `;
            }).join('')}
        `;
    },

    renderMatrixPreview() {
        const container = document.getElementById('matrix-preview');
        if (!container) return;

        if (!this.matrixData || !this.matrixData.matrix) {
            container.innerHTML = '<div class="dashboard-empty">Loading...</div>';
            return;
        }

        const { matrix, features, priorities } = this.matrixData;

        // Show top 4 features by total CP count
        const featureStats = features.map(f => {
            let total = 0, covered = 0;
            priorities.forEach(p => {
                if (matrix[f] && matrix[f][p]) {
                    total += matrix[f][p].total || 0;
                    covered += matrix[f][p].covered || 0;
                }
            });
            return { feature: f, total, covered, rate: total > 0 ? Math.round((covered / total) * 100) : 0 };
        }).sort((a, b) => b.total - a.total).slice(0, 4);

        if (featureStats.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No matrix data</div>';
            return;
        }

        container.innerHTML = `
            <div class="summary-card-header">
                <span class="summary-card-title">Matrix Preview</span>
                <span class="summary-card-link" onclick="Dashboard.switchTab('matrix')">View full →</span>
            </div>
            ${featureStats.map(item => {
                const level = item.rate >= 80 ? 'high' : (item.rate >= 50 ? 'medium' : 'low');
                return `
                    <div class="feature-bar-item">
                        <div class="feature-bar-header">
                            <span class="feature-name">${this.escapeHtml(item.feature)}</span>
                            <span class="feature-rate">${item.rate}%</span>
                        </div>
                        <div class="feature-bar">
                            <div class="feature-bar-fill ${level}" style="width: ${item.rate}%"></div>
                        </div>
                    </div>
                `;
            }).join('')}
        `;
    },

    // ===== Tab 2: 覆盖空洞 =====
    renderHolesTab() {
        const container = document.getElementById('holes-tab-content');
        if (!container) return;

        if (!this.holesData) {
            container.innerHTML = '<div class="dashboard-empty">Loading...</div>';
            return;
        }

        const { critical, warning, attention } = this.holesData;
        const total = (critical?.length || 0) + (warning?.length || 0) + (attention?.length || 0);

        if (total === 0) {
            container.innerHTML = '<div class="dashboard-empty">No coverage holes</div>';
            return;
        }

        container.innerHTML = `
            <div class="holes-kanban">
                ${this.renderHoleColumn('critical', '🔴 Critical', critical)}
                ${this.renderHoleColumn('warning', '🟡 Warning', warning)}
                ${this.renderHoleColumn('attention', '🟡 Attention', attention)}
            </div>
        `;
    },

    renderHoleColumn(type, title, items) {
        const priorityColors = { P0: '#ef4444', P1: '#f59e0b', P2: '#22c55e' };

        return `
            <div class="hole-column">
                <div class="hole-column-header ${type}">
                    <span>${title}</span>
                    <span class="hole-count">${items?.length || 0}</span>
                </div>
                <div class="hole-list">
                    ${items?.length > 0 ? items.map(item => `
                        <div class="hole-card ${type}" onclick="Dashboard.showHoleDetail(${item.cp_id})">
                            <div class="hole-card-name">${this.escapeHtml(item.cp_name)}</div>
                            <div class="hole-card-meta">
                                <span class="hole-card-stat">${this.escapeHtml(item.feature)}</span>
                                <span class="hole-card-stat" style="color: ${priorityColors[item.priority] || '#a1a1aa'}">${item.priority}</span>
                                <span class="hole-card-stat">${item.linked_tcs?.length || 0} TC</span>
                            </div>
                        </div>
                    `).join('') : '<div class="dashboard-empty">No items</div>'}
                </div>
            </div>
        `;
    },

    showHoleDetail(cpId) {
        // Find the hole data
        let hole = null;
        const { critical, warning, attention } = this.holesData || {};
        const allHoles = [...(critical || []), ...(warning || []), ...(attention || [])];
        hole = allHoles.find(h => h.cp_id === cpId);

        if (!hole) return;

        const modal = document.getElementById('dashboard-modal');
        const modalContent = document.getElementById('dashboard-modal-content');

        if (!modal || !modalContent) return;

        const isFcCpMode = this.holesData?.mode === 'fc_cp';
        const linkedItems = isFcCpMode ? hole.linked_fcs : hole.linked_tcs;
        const itemLabel = isFcCpMode ? 'Linked FCs' : 'Linked TCs';

        modalContent.innerHTML = `
            <div class="modal-header">
                <span>Coverage Hole Detail</span>
                <button class="modal-close" onclick="closeModal('dashboard-modal')">&times;</button>
            </div>
            <div class="modal-body">
                <h3 style="margin-bottom: 16px;">${this.escapeHtml(hole.cp_name)}</h3>
                <div style="margin-bottom: 16px; display: flex; gap: 16px;">
                    <div><strong>Feature:</strong> ${this.escapeHtml(hole.feature)}</div>
                    <div><strong>Priority:</strong> ${hole.priority}</div>
                    <div><strong>Coverage:</strong> ${hole.coverage_rate}%</div>
                    <div><strong>${itemLabel}:</strong> ${linkedItems?.length || 0}</div>
                </div>
                <h4 style="margin-bottom: 8px;">${itemLabel}</h4>
                <div class="hole-detail-list">
                    ${linkedItems?.map(item => {
                        if (isFcCpMode) {
                            return `
                                <div class="hole-detail-item">
                                    <span class="hole-detail-status">${item.coverage_pct}%</span>
                                    <span class="hole-detail-name">${this.escapeHtml(item.fc_name)}</span>
                                </div>
                            `;
                        } else {
                            return `
                                <div class="hole-detail-item">
                                    <span class="hole-detail-status ${item.status === 'PASS' ? 'pass' : 'fail'}">${item.status}</span>
                                    <span class="hole-detail-name">${this.escapeHtml(item.tc_name)}</span>
                                </div>
                            `;
                        }
                    }).join('') || '<div class="dashboard-empty">No linked items</div>'}
                </div>
            </div>
        `;

        this.showModal();
    },

    // ===== Tab 3: Owner 分布 =====
    renderOwnerTab() {
        const container = document.getElementById('owner-tab-content');
        if (!container) return;

        if (!this.ownerData || !this.ownerData.owners) {
            container.innerHTML = '<div class="dashboard-empty">Loading...</div>';
            return;
        }

        const { owners, summary } = this.ownerData;

        if (owners.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">No TC data</div>';
            return;
        }

        container.innerHTML = `
            <div class="list-card" style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Total Owners:</strong> ${summary.total_owners}
                    </div>
                    <div>
                        <strong>Unassigned TCs:</strong> ${summary.unassigned_tc_count}
                    </div>
                </div>
            </div>
            <div class="list-card">
                <table class="owner-table">
                    <thead>
                        <tr>
                            <th>Owner</th>
                            <th>Total TC</th>
                            <th>Pass</th>
                            <th>Fail</th>
                            <th>Not Run</th>
                            <th>Pass Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${owners.map(owner => {
                            const passRate = owner.tc_total > 0
                                ? Math.round((owner.tc_pass / owner.tc_total) * 100) : 0;
                            const rateClass = passRate >= 90 ? 'excellent' : (passRate >= 70 ? 'normal' : 'warning');
                            return `
                                <tr onclick="Dashboard.showOwnerDetail('${this.escapeHtml(owner.owner)}')" style="cursor: pointer;">
                                    <td>
                                        <span class="owner-name">
                                            ${this.escapeHtml(owner.owner === '(unassigned)' ? '(unassigned)' : owner.owner)}
                                        </span>
                                    </td>
                                    <td class="owner-tc-count">${owner.tc_total}</td>
                                    <td style="color: #22c55e;">${owner.tc_pass}</td>
                                    <td style="color: #ef4444;">${owner.tc_fail}</td>
                                    <td style="color: #f59e0b;">${owner.tc_not_run}</td>
                                    <td>
                                        <span class="owner-pass-rate ${rateClass}">
                                            <span class="pass-rate-bar">
                                                <span class="pass-rate-bar-fill ${rateClass}" style="width: ${passRate}%"></span>
                                            </span>
                                            ${passRate}%
                                        </span>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    showOwnerDetail(ownerName) {
        if (!this.ownerData || !this.ownerData.owners) return;

        const owner = this.ownerData.owners.find(o => o.owner === ownerName);
        if (!owner) return;

        const modal = document.getElementById('dashboard-modal');
        const modalContent = document.getElementById('dashboard-modal-content');

        if (!modal || !modalContent) return;

        // Generate TC list HTML (limited to 20 items)
        const tcListHtml = (owner.tc_list || []).map(tc => `
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--color-border);">
                <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${this.escapeHtml(tc.name)}</span>
                <span class="status-${tc.status}" style="margin-left: 8px;">${tc.status}</span>
            </div>
        `).join('');

        modalContent.innerHTML = `
            <div class="modal-header">
                <span>Owner: ${this.escapeHtml(owner.owner)}</span>
                <button class="modal-close" onclick="closeModal('dashboard-modal')">&times;</button>
            </div>
            <div class="modal-body">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px;">
                    <div class="overview-card covered">
                        <div class="overview-value">${owner.tc_total}</div>
                        <div class="overview-label">Total TC</div>
                    </div>
                    <div class="overview-card covered">
                        <div class="overview-value" style="color: #22c55e;">${owner.tc_pass}</div>
                        <div class="overview-label">Pass</div>
                    </div>
                    <div class="overview-card unlinked">
                        <div class="overview-value" style="color: #ef4444;">${owner.tc_fail}</div>
                        <div class="overview-label">Fail</div>
                    </div>
                    <div class="overview-card pass-rate">
                        <div class="overview-value" style="color: #f59e0b;">${owner.tc_not_run}</div>
                        <div class="overview-label">Not Run</div>
                    </div>
                </div>
                ${owner.tc_list && owner.tc_list.length > 0 ? `
                    <h4 style="margin-bottom: 8px;">Recent TC List (${owner.tc_list.length})</h4>
                    <div style="max-height: 250px; overflow-y: auto;">
                        ${tcListHtml}
                    </div>
                ` : '<p style="color: var(--color-text-muted);">No TC assigned to this owner.</p>'}
                <p style="color: var(--color-text-muted); margin-top: 12px;">TC list limited to 20 items. Full list available in TC page.</p>
            </div>
        `;

        this.showModal();
    },

    // ===== Tab 4: 覆盖率矩阵 =====
    renderMatrixTab() {
        const container = document.getElementById('matrix-tab-content');
        if (!container) return;

        if (!this.matrixData || !this.matrixData.matrix) {
            container.innerHTML = '<div class="dashboard-empty">Loading...</div>';
            return;
        }

        const { matrix, features, priorities, weak_areas, row_totals, column_totals } = this.matrixData;

        if (features.length === 0) {
            // v0.13.0: 根据模式显示不同的空状态消息
            const emptyMsg = this.currentMode === 'fc_cp'
                ? 'No Functional Coverage data'
                : 'No Cover Point data';
            container.innerHTML = `<div class="dashboard-empty">${emptyMsg}</div>`;
            return;
        }

        // 计算总体覆盖率
        const totalCovered = Object.values(row_totals).reduce((sum, t) => sum + t.covered, 0);
        const totalCP = Object.values(row_totals).reduce((sum, t) => sum + t.total, 0);
        const overallRate = totalCP > 0 ? Math.round((totalCovered / totalCP) * 100) : 0;

        container.innerHTML = `
            <div class="list-card" style="margin-bottom: 16px;">
                <div class="summary-card-title" style="margin-bottom: 12px;">Weak Areas (Coverage &lt; 50%)</div>
                ${weak_areas?.length > 0 ? `
                    <div class="weak-areas-list">
                        ${weak_areas.map(area => `
                            <div class="weak-area-item ${area.severity}">
                                <span class="weak-area-name">${this.escapeHtml(area.feature)} - ${area.priority}</span>
                                <span class="weak-area-rate">${Math.round((area.covered / area.total) * 100)}%</span>
                                <span style="color: var(--color-text-muted); font-size: 12px;">(${area.covered}/${area.total})</span>
                            </div>
                        `).join('')}
                    </div>
                ` : '<div class="dashboard-empty">No weak areas (all ≥ 50%)</div>'}
            </div>
            <div class="list-card">
                <div class="matrix-container">
                    <table class="coverage-matrix">
                        <thead>
                            <tr>
                                <th class="feature-header">Feature</th>
                                ${priorities.map(p => `<th>${p}</th>`).join('')}
                                <th class="total-header">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${features.map(feature => {
                                const rowTotal = row_totals[feature] || { covered: 0, total: 0, rate: 0 };
                                const rowLevel = rowTotal.rate >= 80 ? 'green' : (rowTotal.rate >= 50 ? 'orange' : (rowTotal.rate >= 20 ? 'red' : 'dark-red'));

                                return `
                                <tr>
                                    <td class="feature-cell">${this.escapeHtml(feature)}</td>
                                    ${priorities.map(priority => {
                                        const cell = matrix[feature]?.[priority] || { covered: 0, total: 0, cp_list: [] };
                                        const rate = cell.total > 0 ? Math.round((cell.covered / cell.total) * 100) : 0;
                                        const level = rate >= 80 ? 'green' : (rate >= 50 ? 'orange' : (rate >= 20 ? 'red' : 'dark-red'));

                                        if (cell.total === 0) {
                                            return `<td class="matrix-cell empty">-</td>`;
                                        }

                                        return `
                                            <td class="matrix-cell ${level}" onclick="Dashboard.showMatrixCellDetail('${this.escapeHtml(feature)}', '${priority}')">
                                                <div class="matrix-cell-content">
                                                    <span class="matrix-cell-rate">${rate}%</span>
                                                    <span class="matrix-cell-count">${cell.covered}/${cell.total}</span>
                                                </div>
                                            </td>
                                        `;
                                    }).join('')}
                                    <td class="matrix-cell total-cell ${rowLevel}">
                                        <div class="matrix-cell-content">
                                            <span class="matrix-cell-rate">${rowTotal.rate}%</span>
                                            <span class="matrix-cell-count">${rowTotal.covered}/${rowTotal.total}</span>
                                        </div>
                                    </td>
                                </tr>
                            `}).join('')}
                            <tr class="total-row">
                                <td class="feature-cell total-label">Total</td>
                                ${priorities.map(priority => {
                                    const colTotal = column_totals[priority] || { covered: 0, total: 0, rate: 0 };
                                    const colLevel = colTotal.rate >= 80 ? 'green' : (colTotal.rate >= 50 ? 'orange' : (colTotal.rate >= 20 ? 'red' : 'dark-red'));

                                    if (colTotal.total === 0) {
                                        return `<td class="matrix-cell empty">-</td>`;
                                    }

                                    return `
                                        <td class="matrix-cell total-cell ${colLevel}">
                                            <div class="matrix-cell-content">
                                                <span class="matrix-cell-rate">${colTotal.rate}%</span>
                                                <span class="matrix-cell-count">${colTotal.covered}/${colTotal.total}</span>
                                            </div>
                                        </td>
                                    `;
                                }).join('')}
                                <td class="matrix-cell total-cell green">
                                    <div class="matrix-cell-content">
                                        <span class="matrix-cell-rate">${overallRate}%</span>
                                        <span class="matrix-cell-count">${totalCovered}/${totalCP}</span>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    showMatrixCellDetail(feature, priority) {
        if (!this.matrixData || !this.matrixData.matrix) return;

        const cell = this.matrixData.matrix[feature]?.[priority];
        if (!cell || !cell.cp_list || cell.cp_list.length === 0) return;

        const modal = document.getElementById('dashboard-modal');
        const modalContent = document.getElementById('dashboard-modal-content');

        if (!modal || !modalContent) return;

        const rate = cell.total > 0 ? Math.round((cell.covered / cell.total) * 100) : 0;

        // Generate CP list HTML
        const cpListHtml = cell.cp_list.map(cp => `
            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--color-border);">
                <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${this.escapeHtml(cp.name)}</span>
                <span style="width: 60px; text-align: right; color: ${cp.coverage_rate === 0 ? 'var(--color-danger)' : 'var(--color-success)'};">${cp.coverage_rate}%</span>
            </div>
        `).join('');

        modalContent.innerHTML = `
            <div class="modal-header">
                <span>${this.escapeHtml(feature)} - ${priority}</span>
                <button class="modal-close" onclick="closeModal('dashboard-modal')">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom: 16px;">
                    <strong>Coverage:</strong> ${rate}% (${cell.covered}/${cell.total})
                </div>
                <h4 style="margin-bottom: 8px;">Cover Points (${cell.cp_list.length})</h4>
                <div style="max-height: 300px; overflow-y: auto;">
                    ${cpListHtml}
                </div>
            </div>
        `;

        this.showModal();
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
                <div class="dashboard-empty-icon">⚠️</div>
                <div>${this.escapeHtml(message)}</div>
            </div>
        `;
    }
};

// 初始化 Dashboard (供外部调用)
window.initDashboard = function(projectId) {
    Dashboard.init(projectId);
};

window.switchDashboardTab = function(tabName) {
    Dashboard.switchTab(tabName);
};
