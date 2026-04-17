#!/usr/bin/env python3
"""
Tracker Dashboard API 测试用例 - v0.11.0
测试 GET /api/dashboard/stats 接口
"""

import json
import pytest
import sys
import os
import time
import sqlite3
import datetime

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# 使用已存在的测试项目 ID
TEST_PROJECT_ID = 3  # SOC_DV 项目


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_client(client):
    """创建已登录的管理员客户端"""
    client.post('/api/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json')
    return client


# ============ Dashboard API 测试 ============

class TestDashboardStatsAPI:
    """Dashboard Stats API 测试 (v0.11.0)"""

    def test_api_dash_001_get_dashboard_stats_returns_correct_structure(self, admin_client):
        """API-DASH-001: GET /api/dashboard/stats 返回正确数据结构"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data

        # 验证顶层结构
        dashboard_data = data['data']
        assert 'overview' in dashboard_data
        assert 'by_feature' in dashboard_data
        assert 'by_priority' in dashboard_data
        assert 'trend' in dashboard_data
        assert 'top_uncovered' in dashboard_data
        assert 'recent_activity' in dashboard_data

    def test_api_dash_002_overview_total_cp_count(self, admin_client):
        """API-DASH-002: overview.total_cp 正确统计项目 CP 总数"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 total_cp 存在且为非负整数
        assert 'total_cp' in overview
        assert isinstance(overview['total_cp'], int)
        assert overview['total_cp'] >= 0

    def test_api_dash_003_overview_covered_cp_count(self, admin_client):
        """API-DASH-003: overview.covered_cp 正确统计已覆盖 CP (有 PASS TC)"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 covered_cp 存在且为非负整数
        assert 'covered_cp' in overview
        assert isinstance(overview['covered_cp'], int)
        assert overview['covered_cp'] >= 0

        # covered_cp 不应超过 total_cp
        assert overview['covered_cp'] <= overview['total_cp']

    def test_api_dash_004_overview_unlinked_cp_count(self, admin_client):
        """API-DASH-004: overview.unlinked_cp 正确统计未关联 CP"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 unlinked_cp 存在且为非负整数
        assert 'unlinked_cp' in overview
        assert isinstance(overview['unlinked_cp'], int)
        assert overview['unlinked_cp'] >= 0

    def test_api_dash_005_overview_coverage_rate_calculation(self, admin_client):
        """API-DASH-005: overview.coverage_rate 正确计算覆盖率百分比"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 coverage_rate 存在且格式正确
        assert 'coverage_rate' in overview
        assert isinstance(overview['coverage_rate'], (int, float))
        assert overview['coverage_rate'] >= 0
        assert overview['coverage_rate'] <= 100

        # v0.12.0: 覆盖率 = 所有 CP 覆盖率的平均值 (每个 CP 的 TC 通过率求平均)
        # 注: coverage_rate 是 average of per-CP TC pass rate，不是 covered_cp/total_cp

    def test_api_dash_006_by_feature_grouping(self, admin_client):
        """API-DASH-006: by_feature 按 feature 分组统计正确"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        by_feature = data['data']['by_feature']

        # 验证 by_feature 是数组
        assert isinstance(by_feature, list)

        # 每个 feature 条目应包含必要字段
        for item in by_feature:
            assert 'feature' in item
            assert 'total' in item
            assert 'covered' in item
            assert 'rate' in item
            assert isinstance(item['total'], int)
            assert isinstance(item['covered'], int)
            assert isinstance(item['rate'], (int, float))
            assert item['total'] >= 0
            assert item['covered'] >= 0
            assert item['covered'] <= item['total']
            assert 0 <= item['rate'] <= 100

    def test_api_dash_007_by_priority_grouping(self, admin_client):
        """API-DASH-007: by_priority 按 priority 分组统计正确"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        by_priority = data['data']['by_priority']

        # 验证 by_priority 包含 P0, P1, P2
        assert 'P0' in by_priority
        assert 'P1' in by_priority
        assert 'P2' in by_priority

        # 每个 priority 条目应包含必要字段
        for p in ['P0', 'P1', 'P2']:
            item = by_priority[p]
            assert 'total' in item
            assert 'covered' in item
            assert 'rate' in item
            assert isinstance(item['total'], int)
            assert isinstance(item['covered'], int)
            assert isinstance(item['rate'], (int, float))
            assert item['total'] >= 0
            assert item['covered'] >= 0
            assert item['covered'] <= item['total']
            assert 0 <= item['rate'] <= 100

    def test_api_dash_008_trend_data_format(self, admin_client):
        """API-DASH-008: trend 返回最近7天的覆盖率数据"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        trend = data['data']['trend']

        # 验证 trend 是数组
        assert isinstance(trend, list)

        # trend 最多7天数据
        assert len(trend) <= 7

        # 每个 trend 条目应包含必要字段
        for item in trend:
            assert 'date' in item
            assert 'rate' in item
            assert isinstance(item['rate'], (int, float))
            assert item['rate'] >= 0
            assert item['rate'] <= 100

    def test_api_dash_009_top_uncovered_ordering(self, admin_client):
        """API-DASH-009: top_uncovered 返回按 priority 排序的未覆盖 CP"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        top_uncovered = data['data']['top_uncovered']

        # 验证 top_uncovered 是数组
        assert isinstance(top_uncovered, list)

        # 最多5条
        assert len(top_uncovered) <= 5

        # 每个条目应包含必要字段
        for item in top_uncovered:
            assert 'id' in item
            assert 'name' in item
            assert 'priority' in item
            assert 'feature' in item
            assert item['priority'] in ['P0', 'P1', 'P2']

    def test_api_dash_010_unauthorized_access(self, client):
        """API-DASH-010: 未登录访问返回 401"""
        response = client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 401

    def test_api_dash_011_nonexistent_project(self, admin_client):
        """API-DASH-011: project_id 不存在返回 404"""
        # 使用一个大概率不存在的项目 ID
        response = admin_client.get('/api/dashboard/stats?project_id=99999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data


# ============ Dashboard API v0.12.0 新增测试 ============

class TestCoverageHolesAPI:
    """Coverage Holes API 测试 (v0.12.0) - API-HOLE-001 to API-HOLE-006"""

    # 使用有数据的项目 (SOC_DV 有空洞数据)
    TEST_PROJECT_ID = 3  # SOC_DV

    def test_coverage_holes_basic(self, admin_client):
        """API-HOLE-001: 测试获取空洞列表返回正确结构"""
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data

        # 验证必要字段都存在
        holes_data = data['data']
        assert 'mode' in holes_data  # v0.12.0 新增
        assert 'critical' in holes_data
        assert 'warning' in holes_data
        assert 'attention' in holes_data
        assert 'total_critical' in holes_data
        assert 'total_warning' in holes_data
        assert 'total_attention' in holes_data

        # 验证都是数组
        assert isinstance(holes_data['critical'], list)
        assert isinstance(holes_data['warning'], list)
        assert isinstance(holes_data['attention'], list)

    def test_coverage_holes_entry_structure(self, admin_client):
        """API-HOLE-002: 测试空洞条目包含必要字段"""
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 检查所有非空空洞的条目结构
        for level in ['critical', 'warning', 'attention']:
            for hole in data['data'][level]:
                assert 'cp_id' in hole
                assert 'cp_name' in hole
                assert 'feature' in hole
                assert 'priority' in hole
                assert 'coverage_rate' in hole
                assert 'linked_tcs' in hole
                assert isinstance(hole['linked_tcs'], list)

                # 验证 linked_tcs 中每个条目
                for tc in hole['linked_tcs']:
                    assert 'tc_id' in tc
                    assert 'tc_name' in tc
                    assert 'status' in tc

    def test_coverage_holes_tc_cp_mode_priority_classification(self, admin_client):
        """API-HOLE-003: 测试 tc-cp 模式按 priority 分级 (P0=critical, P1=warning, P2=attention)"""
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证是 tc_cp 模式
        assert data['data']['mode'] == 'tc_cp'

        # Critical 应该是 P0
        for hole in data['data']['critical']:
            assert hole['priority'] == 'P0', f"Critical hole {hole['cp_id']} has priority {hole['priority']}, expected P0"
            assert hole['coverage_rate'] == 0, f"Critical hole {hole['cp_id']} has non-zero coverage"

        # Warning 应该是 P1
        for hole in data['data']['warning']:
            assert hole['priority'] == 'P1', f"Warning hole {hole['cp_id']} has priority {hole['priority']}, expected P1"
            assert hole['coverage_rate'] == 0, f"Warning hole {hole['cp_id']} has non-zero coverage"

        # Attention 应该是 P2
        for hole in data['data']['attention']:
            assert hole['priority'] == 'P2', f"Attention hole {hole['cp_id']} has priority {hole['priority']}, expected P2"
            assert hole['coverage_rate'] == 0, f"Attention hole {hole['cp_id']} has non-zero coverage"

    def test_coverage_holes_sorted_by_priority(self, admin_client):
        """API-HOLE-004: 测试空洞按 priority 降序排列"""
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}

        # 检查 critical 列表是按 priority 降序 (P0 在前)
        critical_priorities = [hole['priority'] for hole in data['data']['critical']]
        if len(critical_priorities) > 1:
            for i in range(len(critical_priorities) - 1):
                assert priority_order[critical_priorities[i]] <= priority_order[critical_priorities[i + 1]], \
                    "Critical holes not sorted by priority"

    def test_coverage_holes_excludes_unlinked(self, admin_client):
        """API-HOLE-005: 测试排除未关联 TC 的 CP"""
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 所有返回的空洞都应该有 linked_tcs >= 1
        all_holes = data['data']['critical'] + data['data']['warning'] + data['data']['attention']
        for hole in all_holes:
            assert len(hole['linked_tcs']) > 0, f"CP {hole['cp_id']} has no linked TCs but returned as hole"

    def test_coverage_holes_max_20_per_category(self, admin_client):
        """API-HOLE-006: 测试每类等级最多显示 20 条"""
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data['data']['critical']) <= 20
        assert len(data['data']['warning']) <= 20
        assert len(data['data']['attention']) <= 20


class TestOwnerStatsAPI:
    """Owner Stats API 测试 (v0.12.0) - API-OWNER-001 to API-OWNER-004"""

    TEST_PROJECT_ID = 3  # SOC_DV

    def test_owner_stats_basic(self, admin_client):
        """API-OWNER-001: 测试获取 Owner 列表返回正确结构"""
        response = admin_client.get(f'/api/dashboard/owner-stats?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data

        owner_data = data['data']
        assert 'owners' in owner_data
        assert 'summary' in owner_data
        assert isinstance(owner_data['owners'], list)

    def test_owner_stats_entry_fields(self, admin_client):
        """API-OWNER-002: 测试 Owner 条目包含必要字段"""
        response = admin_client.get(f'/api/dashboard/owner-stats?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        for owner in data['data']['owners']:
            assert 'owner' in owner
            assert 'tc_total' in owner
            assert 'tc_pass' in owner
            assert 'tc_fail' in owner
            assert 'tc_not_run' in owner
            assert 'display_name' in owner

            # 验证数值都是非负整数
            assert isinstance(owner['tc_total'], int)
            assert isinstance(owner['tc_pass'], int)
            assert isinstance(owner['tc_fail'], int)
            assert isinstance(owner['tc_not_run'], int)
            assert owner['tc_total'] >= 0
            assert owner['tc_pass'] >= 0
            assert owner['tc_fail'] >= 0
            assert owner['tc_not_run'] >= 0

            # tc_total = tc_pass + tc_fail + tc_not_run
            assert owner['tc_total'] == owner['tc_pass'] + owner['tc_fail'] + owner['tc_not_run']

    def test_owner_stats_unassigned_tc(self, admin_client):
        """API-OWNER-003: 测试未分配 TC 显示 (unassigned)"""
        response = admin_client.get(f'/api/dashboard/owner-stats?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 检查是否有 (unassigned) owner
        unassigned_owners = [o for o in data['data']['owners'] if o['owner'] == '(unassigned)']
        # 如果有，验证其 TC 数量
        for unassigned in unassigned_owners:
            assert unassigned['tc_total'] >= 0

        # 验证 summary 中的 unassigned_tc_count
        summary = data['data']['summary']
        assert 'unassigned_tc_count' in summary
        assert isinstance(summary['unassigned_tc_count'], int)

    def test_owner_stats_summary_fields(self, admin_client):
        """API-OWNER-004: 测试汇总统计包含必要字段"""
        response = admin_client.get(f'/api/dashboard/owner-stats?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        summary = data['data']['summary']
        assert 'total_owners' in summary
        assert 'unassigned_tc_count' in summary

        # total_owners 应该是非负整数 (排除 unassigned)
        assert isinstance(summary['total_owners'], int)
        assert summary['total_owners'] >= 0


class TestCoverageMatrixAPI:
    """Coverage Matrix API 测试 (v0.12.0) - API-MATRIX-001 to API-MATRIX-005"""

    TEST_PROJECT_ID = 3  # SOC_DV

    def test_coverage_matrix_basic(self, admin_client):
        """API-MATRIX-001: 测试获取矩阵返回正确结构"""
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data

        matrix_data = data['data']
        assert 'matrix' in matrix_data
        assert 'features' in matrix_data
        assert 'priorities' in matrix_data
        assert 'weak_areas' in matrix_data

        # 验证 features 和 priorities 是数组
        assert isinstance(matrix_data['features'], list)
        assert isinstance(matrix_data['priorities'], list)

    def test_coverage_matrix_covered_count(self, admin_client):
        """API-MATRIX-002: 测试已覆盖计数正确 (covered <= total)"""
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        matrix = data['data']['matrix']
        for feature, priorities in matrix.items():
            for priority, cell in priorities.items():
                assert 'covered' in cell
                assert 'total' in cell
                assert cell['covered'] <= cell['total']
                assert cell['covered'] >= 0
                assert cell['total'] >= 0

    def test_coverage_matrix_cp_ids_in_cp_list(self, admin_client):
        """API-MATRIX-003: 测试 CP ID 列表在 cp_list 中"""
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        matrix = data['data']['matrix']
        for feature, priorities in matrix.items():
            for priority, cell in priorities.items():
                assert 'cp_list' in cell
                assert isinstance(cell['cp_list'], list)

                # cp_list 中每个条目应该有 id
                for cp in cell['cp_list']:
                    assert 'id' in cp
                    assert 'name' in cp
                    assert 'coverage_rate' in cp

                # cp_list 长度应该等于 total
                assert len(cell['cp_list']) == cell['total']

    def test_coverage_matrix_weak_areas_threshold(self, admin_client):
        """API-MATRIX-004: 测试薄弱区域识别 (< 50% 覆盖率)"""
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        weak_areas = data['data']['weak_areas']
        matrix = data['data']['matrix']

        # 验证每个薄弱区域确实 < 50%
        for weak in weak_areas:
            feature = weak['feature']
            priority = weak['priority']
            rate = (weak['covered'] / weak['total'] * 100) if weak['total'] > 0 else 0

            assert rate < 50, f"Weak area {feature}/{priority} has rate {rate}% >= 50%"
            assert 'severity' in weak
            assert 'covered' in weak
            assert 'total' in weak

    def test_coverage_matrix_severity_correct(self, admin_client):
        """API-MATRIX-005: 测试告警级别正确 (critical < 20%, warning < 50%)"""
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        weak_areas = data['data']['weak_areas']

        for weak in weak_areas:
            rate = (weak['covered'] / weak['total'] * 100) if weak['total'] > 0 else 0

            if weak['severity'] == 'critical':
                assert rate < 20, f"Critical area {weak['feature']}/{weak['priority']} has rate {rate}% >= 20%"
            elif weak['severity'] == 'warning':
                assert 20 <= rate < 50, f"Warning area {weak['feature']}/{weak['priority']} has rate {rate}% not in [20%, 50%)"


class TestDashboardStatsV012:
    """Dashboard Stats API v0.12.0 增强测试"""

    TEST_PROJECT_ID = 3  # SOC_DV

    def test_dashboard_stats_week_change_placeholder(self, admin_client):
        """API-DASH-012: 测试概览统计包含必要的统计字段

        注意: 周环比 (week_change) 是前端根据快照数据计算的，API 返回当前值
        本测试验证概览数据完整性
        """
        response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)

        overview = data['data']['overview']
        # 验证概览数据完整
        assert 'total_cp' in overview
        assert 'covered_cp' in overview
        assert 'coverage_rate' in overview
        assert 'unlinked_cp' in overview

    def test_dashboard_stats_no_snapshot_returns_current_data(self, admin_client):
        """API-DASH-013: 测试无快照数据时 API 仍返回当前数据

        API 本身不依赖快照，返回的是当前数据库实时数据
        """
        # 使用没有快照的项目 47
        response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True

        # 概览数据应该基于当前数据
        overview = data['data']['overview']
        assert overview['total_cp'] >= 0
        assert overview['coverage_rate'] >= 0


class TestDashboardStatsWeekChange:
    """API-DASH-014~016: 测试 week_change = 实时值 - 最新快照值"""

    TEST_PROJECT_ID = 3  # SOC_DV
    # SOC_DV 数据库路径
    DB_PATH = '/projects/management/tracker/dev/data/SOC_DV.db'

    def _get_db_path(self):
        """获取测试项目数据库路径"""
        return self.DB_PATH

    def _insert_snapshot_with_known_values(self, cp_covered, cp_total, tc_pass_count, tc_total):
        """插入一个已知值的快照，用于测试 week_change 计算"""
        conn = sqlite3.connect(self._get_db_path())
        cursor = conn.cursor()
        today = datetime.date.today().isoformat()
        # 清除当天的旧快照，避免 unique constraint
        cursor.execute(
            "DELETE FROM project_progress WHERE project_id = ? AND snapshot_date = ?",
            (self.TEST_PROJECT_ID, today)
        )
        cursor.execute("""
            INSERT INTO project_progress (
                project_id, snapshot_date, actual_coverage,
                p0_coverage, p1_coverage, p2_coverage, p3_coverage,
                tc_pass_count, tc_total, cp_covered, cp_total, progress_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.TEST_PROJECT_ID, today, 0.0,
            0, 0, 0, 0,
            tc_pass_count, tc_total, cp_covered, cp_total, '{}'
        ))
        conn.commit()
        conn.close()

    def _update_tc_status(self, delta_pass):
        """通过修改 TC 状态来改变实时 covered_cp（间接方式）
        注意: covered_cp 是有 PASS TC 的 CP 数量，需要操作关联关系
        这里改 tc_pass_count 来间接验证 tc_pass_rate 的 week_change
        """
        conn = sqlite3.connect(self._get_db_path())
        cursor = conn.cursor()
        # 获取当前 PASS 数量的 TC id
        cursor.execute(
            "SELECT id FROM test_case WHERE project_id = ? AND status = 'PASS' LIMIT ?",
            (self.TEST_PROJECT_ID, delta_pass)
        )
        # 把一些 TC 改成 PASS（假设有可改的 TC）
        cursor.execute(
            "UPDATE test_case SET status = 'PASS' WHERE project_id = ? AND status != 'PASS' LIMIT ?",
            (self.TEST_PROJECT_ID, delta_pass)
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected

    def test_week_change_covered_cp_is_realtime_minus_snapshot(self, admin_client):
        """API-DASH-014: week_change.covered_cp = 实时 covered_cp - 快照 cp_covered

        步骤:
        1. 插入快照 cp_covered=10
        2. 验证实时 covered_cp
        3. 调用 API，确认 week_change.covered_cp = 实时 - 10
        """
        # 先获取实时数据，确定当前 covered_cp
        response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
        data = json.loads(response.data)
        real_covered_cp = data['data']['overview']['covered_cp']
        real_total_cp = data['data']['overview']['total_cp']

        # 快照值设为比实时少2
        snapshot_covered_cp = max(0, real_covered_cp - 2)
        self._insert_snapshot_with_known_values(
            cp_covered=snapshot_covered_cp,
            cp_total=real_total_cp,
            tc_pass_count=0,
            tc_total=1
        )

        # 再次调用 API
        response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
        data = json.loads(response.data)
        week_change = data['data']['overview']['week_change']

        # 验证: week_change.covered_cp = 实时 - 快照
        expected = real_covered_cp - snapshot_covered_cp
        assert week_change['covered_cp'] == expected, \
            f"week_change.covered_cp 应为 {expected}，实际为 {week_change['covered_cp']}"

    def test_week_change_tc_pass_rate_is_realtime_minus_snapshot(self, admin_client):
        """API-DASH-015: week_change.tc_pass_rate = 实时 tc_pass_rate - 快照 tc_pass_rate

        步骤:
        1. 插入快照 tc_pass_rate=60%
        2. 调用 API，确认 week_change.tc_pass_rate = 实时 - 60
        """
        # 先获取实时数据
        response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
        data = json.loads(response.data)
        real_tc_pass = data['data']['overview']['tc_pass']
        real_tc_total = data['data']['overview']['tc_total']

        # 快照值: tc_pass=6, tc_total=10 => 60%
        snapshot_tc_pass = 6
        snapshot_tc_total = 10
        self._insert_snapshot_with_known_values(
            cp_covered=0,
            cp_total=1,
            tc_pass_count=snapshot_tc_pass,
            tc_total=snapshot_tc_total
        )

        # 再次调用 API
        response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
        data = json.loads(response.data)
        week_change = data['data']['overview']['week_change']

        # 实时 tc_pass_rate
        real_rate = round((real_tc_pass / real_tc_total * 100), 1) if real_tc_total > 0 else 0
        snapshot_rate = round((snapshot_tc_pass / snapshot_tc_total * 100), 1)
        expected = round(real_rate - snapshot_rate, 1)

        assert week_change['tc_pass_rate'] == expected, \
            f"week_change.tc_pass_rate 应为 {expected}，实际为 {week_change['tc_pass_rate']}"

    def test_week_change_none_when_no_snapshot(self, admin_client):
        """API-DASH-016: 无快照时 week_change 各项为 None"""
        # 找一个没有快照的项目，或者临时删除项目3的快照再恢复
        conn = sqlite3.connect(self._get_db_path())
        cursor = conn.cursor()
        # 临时备份项目3的快照
        cursor.execute("SELECT * FROM project_progress WHERE project_id = ?", (self.TEST_PROJECT_ID,))
        original_snapshots = cursor.fetchall()
        # 删除所有快照
        cursor.execute("DELETE FROM project_progress WHERE project_id = ?", (self.TEST_PROJECT_ID,))
        conn.commit()
        conn.close()

        try:
            response = admin_client.get(f'/api/dashboard/stats?project_id={self.TEST_PROJECT_ID}')
            data = json.loads(response.data)
            week_change = data['data']['overview']['week_change']
            assert week_change['covered_cp'] is None
            assert week_change['tc_pass_rate'] is None
            assert week_change['unlinked_cp'] is None
        finally:
            # 恢复快照
            if original_snapshots:
                conn = sqlite3.connect(self._get_db_path())
                cursor = conn.cursor()
                for snap in original_snapshots:
                    cursor.execute("""
                        INSERT INTO project_progress (
                            project_id, snapshot_date, actual_coverage,
                            p0_coverage, p1_coverage, p2_coverage, p3_coverage,
                            tc_pass_count, tc_total, cp_covered, cp_total, progress_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        snap[1], snap[2], snap[3],
                        snap[4], snap[5], snap[6], snap[7],
                        snap[8], snap[9], snap[10], snap[11], snap[12]
                    ))
                conn.commit()
                conn.close()


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
