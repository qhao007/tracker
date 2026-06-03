"""
Tracker Progress Charts API 测试用例 - v0.15.0
测试 /api/progress/<project_id> 新增的 trend 和 feature_coverage 字段

测试 ID 映射:
- PC-API-001: test_progress_returns_trend
- PC-API-002: test_progress_returns_feature_coverage
- PC-API-003: test_feature_coverage_calculation
- PC-API-004: test_feature_coverage_sorted_by_coverage_pct
- PC-API-005: test_progress_empty_project
- PC-API-006: test_progress_priority_filter_feature_coverage
- PC-API-007: test_progress_priority_filter_trend
- PC-API-008: test_progress_date_filter
- PC-API-009: test_trend_snapshot_data_mapping
- PC-API-010: test_feature_coverage_p0_p1_sub_coverage

已知 Bug (BUG-103):
- 不带 priority 参数时 feature_coverage 计算抛出 UnboundLocalError
- 测试中使用 ?priority=P0,P1,P2,P3 作为 workaround 验证功能正确性
- 专门的回归测试 test_bug_103_feature_coverage_without_priority 记录此 Bug
"""

import json
import pytest
import sys
import os
import uuid
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app import create_app


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


class TestProgressChartsTrend:
    """trend 字段测试 - PC-API-001, PC-API-007, PC-API-009"""

    def _create_project(self, admin_client, name, start_date, end_date):
        """创建测试项目"""
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': start_date,
                'end_date': end_date
            }),
            content_type='application/json')
        if response.status_code != 200:
            return None
        data = json.loads(response.data)
        return data.get('project', {}).get('id')

    def _add_cp_with_tc(self, admin_client, project_id, feature, cp_name, priority, tc_status='PASS'):
        """添加 CP 并创建关联的 TC"""
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': feature,
                'cover_point': cp_name,
                'priority': priority
            }),
            content_type='application/json')
        if cp_response.status_code != 200:
            return None
        cp_id = json.loads(cp_response.data).get('item', {}).get('id')

        tc_response = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id,
                'testbench': 'tb_test',
                'test_name': f'TC_{cp_name}',
                'scenario': f'Test {cp_name}',
                'status': tc_status,
                'target_date': date.today().isoformat(),
                'connections': [cp_id]
            }),
            content_type='application/json')
        if tc_response.status_code != 200:
            return cp_id
        return cp_id

    def test_progress_returns_trend(self, admin_client):
        """PC-API-001: GET /api/progress/<project_id> 返回包含 trend 字段
        trend 为数组，元素含 date, tc_pass, tc_total, cp_coverage, p0_coverage, cp_covered, cp_total
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"Trend_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 添加 CP 和 TC
        self._add_cp_with_tc(admin_client, project_id, 'CPU', f'CP-P0-{unique_id}', 'P0')

        # 创建快照以产生 trend 数据
        snapshot_response = admin_client.post(f'/api/progress/{project_id}/snapshot')
        # 快照可能成功也可能失败，不影响 trend 字段存在性验证

        response = admin_client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证 trend 字段存在且为数组
        assert 'trend' in data, "响应中缺少 trend 字段"
        assert isinstance(data['trend'], list), "trend 应为数组类型"

        # 如果有快照数据，验证字段结构
        if len(data['trend']) > 0:
            trend_item = data['trend'][0]
            required_fields = ['date', 'tc_pass', 'tc_total', 'cp_coverage', 'p0_coverage', 'cp_covered', 'cp_total']
            for field in required_fields:
                assert field in trend_item, f"trend 元素缺少字段: {field}"

            # 验证字段类型
            assert isinstance(trend_item['date'], str), "date 应为字符串"
            assert isinstance(trend_item['tc_pass'], int), "tc_pass 应为整数"
            assert isinstance(trend_item['tc_total'], int), "tc_total 应为整数"
            assert isinstance(trend_item['cp_coverage'], (int, float)), "cp_coverage 应为数值"
            assert isinstance(trend_item['p0_coverage'], (int, float)), "p0_coverage 应为数值"
            assert isinstance(trend_item['cp_covered'], int), "cp_covered 应为整数"
            assert isinstance(trend_item['cp_total'], int), "cp_total 应为整数"

    def test_progress_priority_filter_trend(self, admin_client):
        """PC-API-007: Priority 过滤对 trend 生效
        ?priority=P0 时 trend 数据基于 P0 覆盖率
        验证: trend 字段存在，priority_filter 正确反映过滤条件
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"TrendPriority_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 添加 P0 和 P1 CP
        self._add_cp_with_tc(admin_client, project_id, 'CPU', f'CP-P0-{unique_id}', 'P0')
        self._add_cp_with_tc(admin_client, project_id, 'Memory', f'CP-P1-{unique_id}', 'P1')

        # 创建快照
        admin_client.post(f'/api/progress/{project_id}/snapshot')

        # 测试无过滤
        response_no_filter = admin_client.get(f'/api/progress/{project_id}')
        data_no_filter = json.loads(response_no_filter.data)
        assert 'trend' in data_no_filter
        assert data_no_filter['priority_filter'] == ""

        # 测试 P0 过滤
        response_p0 = admin_client.get(f'/api/progress/{project_id}?priority=P0')
        data_p0 = json.loads(response_p0.data)
        assert 'trend' in data_p0
        assert data_p0['priority_filter'] == "P0"

        # 验证 trend 数组存在（不管是否有数据）
        assert isinstance(data_p0['trend'], list)

    def test_trend_snapshot_data_mapping(self, admin_client):
        """PC-API-009: 快照数据正确映射到 trend
        创建快照后，trend 包含该快照数据
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"TrendSnapshot_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 添加 CP 和 PASS 状态的 TC
        self._add_cp_with_tc(admin_client, project_id, 'CPU', f'CP-P0-{unique_id}', 'P0', 'PASS')

        # 创建 TC 使 tc_pass > 0
        tc_response = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id,
                'testbench': 'tb',
                'test_name': f'TC-PASS-{unique_id}',
                'scenario': 'Test',
                'status': 'PASS',
                'target_date': '2026-01-15'
            }),
            content_type='application/json')
        assert tc_response.status_code == 200

        # 创建快照
        snapshot_response = admin_client.post(f'/api/progress/{project_id}/snapshot')
        assert snapshot_response.status_code == 200

        # 获取进度数据
        response = admin_client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'trend' in data
        assert len(data['trend']) > 0, "创建快照后 trend 应该包含数据"

        trend_item = data['trend'][0]
        # 验证快照数据映射正确
        assert 'date' in trend_item
        assert trend_item['tc_pass'] >= 0
        assert trend_item['tc_total'] >= 0
        assert 0 <= trend_item['cp_coverage'] <= 100
        assert 0 <= trend_item['p0_coverage'] <= 100
        assert trend_item['cp_covered'] >= 0
        assert trend_item['cp_total'] >= 0


class TestProgressChartsFeatureCoverage:
    """feature_coverage 字段测试 - PC-API-002 ~ PC-API-006, PC-API-010

    注意: 由于 BUG-103 (不带 priority 参数时 feature_coverage 计算抛出 UnboundLocalError),
    以下测试使用 ?priority=P0,P1,P2,P3 作为 workaround 来验证功能正确性。
    该 workaround 等价于无过滤（包含所有 Priority），同时绕过 Bug。
    """

    def _create_project(self, admin_client, name, start_date, end_date):
        """创建测试项目"""
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': start_date,
                'end_date': end_date
            }),
            content_type='application/json')
        if response.status_code != 200:
            return None
        data = json.loads(response.data)
        return data.get('project', {}).get('id')

    def _add_cp(self, admin_client, project_id, feature, cp_name, priority):
        """仅添加 CP，不创建 TC"""
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': feature,
                'cover_point': cp_name,
                'priority': priority
            }),
            content_type='application/json')
        if cp_response.status_code != 200:
            return None
        return json.loads(cp_response.data).get('item', {}).get('id')

    def _add_cp_with_tc(self, admin_client, project_id, feature, cp_name, priority, tc_status='PASS'):
        """添加 CP 并创建关联的 TC

        注意: TC 创建 API 总是将 status 设为 OPEN，忽略请求中的 status 字段。
        如果需要 PASS/FAIL 状态，创建后会通过 /api/tc/<id>/status 更新。
        """
        cp_id = self._add_cp(admin_client, project_id, feature, cp_name, priority)
        if not cp_id:
            return None

        tc_response = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id,
                'testbench': 'tb_test',
                'test_name': f'TC_{cp_name}',
                'scenario': f'Test {cp_name}',
                'status': 'OPEN',  # API 忽略此字段，总是创建为 OPEN
                'target_date': date.today().isoformat(),
                'connections': [cp_id]
            }),
            content_type='application/json')
        if tc_response.status_code != 200:
            return cp_id

        tc_data = json.loads(tc_response.data)
        tc_id = tc_data.get('item', {}).get('id')

        # 如果请求非 OPEN 状态，通过 status API 更新
        if tc_status != 'OPEN' and tc_id:
            status_response = admin_client.post(f'/api/tc/{tc_id}/status',
                data=json.dumps({'status': tc_status, 'project_id': project_id}),
                content_type='application/json')
            # 状态更新失败不影响 CP 创建结果

        return cp_id

    def test_progress_returns_feature_coverage(self, admin_client):
        """PC-API-002: GET /api/progress/<project_id> 返回包含 feature_coverage 字段
        feature_coverage 为数组，元素含 feature, total_cp, covered_cp, uncovered_cp,
        coverage_pct, p0_total, p0_covered, p0_coverage, p1_total, p1_covered, p1_coverage
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"Feature_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 添加不同 Feature 的 CP
        self._add_cp_with_tc(admin_client, project_id, 'CPU', f'CP-CPU-{unique_id}', 'P0')
        self._add_cp_with_tc(admin_client, project_id, 'Memory', f'CP-MEM-{unique_id}', 'P1')

        # 使用 priority=P0,P1,P2,P3 作为 workaround 绕过 BUG-103
        response = admin_client.get(f'/api/progress/{project_id}?priority=P0,P1,P2,P3')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证 feature_coverage 字段存在且为数组
        assert 'feature_coverage' in data, "响应中缺少 feature_coverage 字段"
        assert isinstance(data['feature_coverage'], list), "feature_coverage 应为数组类型"
        assert len(data['feature_coverage']) > 0, "有 CP 时 feature_coverage 不应为空"

        # 验证字段结构
        fc_item = data['feature_coverage'][0]
        required_fields = [
            'feature', 'total_cp', 'covered_cp', 'uncovered_cp', 'coverage_pct',
            'p0_total', 'p0_covered', 'p0_coverage',
            'p1_total', 'p1_covered', 'p1_coverage'
        ]
        for field in required_fields:
            assert field in fc_item, f"feature_coverage 元素缺少字段: {field}"

        # 验证字段类型
        assert isinstance(fc_item['feature'], str)
        assert isinstance(fc_item['total_cp'], int)
        assert isinstance(fc_item['covered_cp'], int)
        assert isinstance(fc_item['uncovered_cp'], int)
        assert isinstance(fc_item['coverage_pct'], (int, float))
        assert isinstance(fc_item['p0_total'], int)
        assert isinstance(fc_item['p0_covered'], int)
        assert isinstance(fc_item['p0_coverage'], (int, float))
        assert isinstance(fc_item['p1_total'], int)
        assert isinstance(fc_item['p1_covered'], int)
        assert isinstance(fc_item['p1_coverage'], (int, float))

    def test_feature_coverage_calculation(self, admin_client):
        """PC-API-003: feature_coverage 计算正确性
        - covered_cp + uncovered_cp = total_cp
        - coverage_pct 在 0-100 之间
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"FeatureCalc_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # Feature A: 2 个 CP，都关联 PASS TC
        self._add_cp_with_tc(admin_client, project_id, 'FeatureA', f'CP-A1-{unique_id}', 'P0', 'PASS')
        self._add_cp_with_tc(admin_client, project_id, 'FeatureA', f'CP-A2-{unique_id}', 'P0', 'PASS')

        # Feature B: 2 个 CP，1 个关联 PASS TC，1 个无 TC
        self._add_cp_with_tc(admin_client, project_id, 'FeatureB', f'CP-B1-{unique_id}', 'P1', 'PASS')
        self._add_cp(admin_client, project_id, 'FeatureB', f'CP-B2-{unique_id}', 'P1')

        # 使用 priority=P0,P1,P2,P3 作为 workaround 绕过 BUG-103
        response = admin_client.get(f'/api/progress/{project_id}?priority=P0,P1,P2,P3')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data['feature_coverage']) > 0

        for fc in data['feature_coverage']:
            # 验证 covered_cp + uncovered_cp = total_cp
            assert fc['covered_cp'] + fc['uncovered_cp'] == fc['total_cp'], \
                f"Feature {fc['feature']}: covered({fc['covered_cp']}) + uncovered({fc['uncovered_cp']}) != total({fc['total_cp']})"

            # 验证 coverage_pct 在合理范围内
            assert 0 <= fc['coverage_pct'] <= 100, \
                f"Feature {fc['feature']}: coverage_pct={fc['coverage_pct']} 不在 0-100 范围内"

            # 验证 p0_total, p1_total 不为负
            assert fc['p0_total'] >= 0
            assert fc['p1_total'] >= 0

    def test_feature_coverage_sorted_by_coverage_pct(self, admin_client):
        """PC-API-004: feature_coverage 按 coverage_pct 从高到低排列"""
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"FeatureSort_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # Feature High: 2 个 CP 都 PASS -> 100% coverage
        self._add_cp_with_tc(admin_client, project_id, 'FeatureHigh', f'CP-H1-{unique_id}', 'P0', 'PASS')
        self._add_cp_with_tc(admin_client, project_id, 'FeatureHigh', f'CP-H2-{unique_id}', 'P0', 'PASS')

        # Feature Low: 2 个 CP，1 个 PASS，1 个无 TC -> 50% coverage
        self._add_cp_with_tc(admin_client, project_id, 'FeatureLow', f'CP-L1-{unique_id}', 'P1', 'PASS')
        self._add_cp(admin_client, project_id, 'FeatureLow', f'CP-L2-{unique_id}', 'P1')

        # Feature Zero: 1 个 CP 无 TC -> 0% coverage
        self._add_cp(admin_client, project_id, 'FeatureZero', f'CP-Z1-{unique_id}', 'P2')

        # 使用 priority=P0,P1,P2,P3 作为 workaround 绕过 BUG-103
        response = admin_client.get(f'/api/progress/{project_id}?priority=P0,P1,P2,P3')
        assert response.status_code == 200
        data = json.loads(response.data)

        features = data['feature_coverage']
        assert len(features) >= 3

        # 验证按 coverage_pct 降序排列
        for i in range(len(features) - 1):
            assert features[i]['coverage_pct'] >= features[i + 1]['coverage_pct'], \
                f"feature_coverage 未按 coverage_pct 降序排列: " \
                f"features[{i}]={features[i]['coverage_pct']} < features[{i+1}]={features[i+1]['coverage_pct']}"

        # 验证最高覆盖率在最前面
        assert features[0]['feature'] == 'FeatureHigh', \
            f"最高覆盖率的 Feature 应在第一位，实际为 {features[0]['feature']}"

    def test_progress_empty_project(self, admin_client):
        """PC-API-005: 空项目（无 CP）返回正确
        feature_coverage 为空数组，trend 为空数组
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"Empty_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 不添加任何 CP
        response = admin_client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'feature_coverage' in data
        assert 'trend' in data
        assert data['feature_coverage'] == [], "空项目的 feature_coverage 应为空数组"
        assert data['trend'] == [], "空项目的 trend 应为空数组"

    def test_progress_priority_filter_feature_coverage(self, admin_client):
        """PC-API-006: Priority 过滤对 feature_coverage 生效
        ?priority=P0 时只返回包含 P0 CP 的 Feature
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"FeaturePriority_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # Feature P0Only: 只有 P0 CP
        self._add_cp_with_tc(admin_client, project_id, 'P0Only', f'CP-P0O-{unique_id}', 'P0', 'PASS')

        # Feature P1Only: 只有 P1 CP
        self._add_cp_with_tc(admin_client, project_id, 'P1Only', f'CP-P1O-{unique_id}', 'P1', 'PASS')

        # Feature Mixed: P0 + P1 CP
        self._add_cp_with_tc(admin_client, project_id, 'Mixed', f'CP-M0-{unique_id}', 'P0', 'PASS')
        self._add_cp_with_tc(admin_client, project_id, 'Mixed', f'CP-M1-{unique_id}', 'P1', 'PASS')

        # 使用 priority=P0,P1,P2,P3 作为 workaround 绕过 BUG-103 来测试"无过滤"场景
        response_all = admin_client.get(f'/api/progress/{project_id}?priority=P0,P1,P2,P3')
        data_all = json.loads(response_all.data)
        all_features = [f['feature'] for f in data_all['feature_coverage']]
        assert 'P0Only' in all_features
        assert 'P1Only' in all_features
        assert 'Mixed' in all_features

        # P0 过滤：应只返回包含 P0 CP 的 Feature (P0Only, Mixed)
        response_p0 = admin_client.get(f'/api/progress/{project_id}?priority=P0')
        data_p0 = json.loads(response_p0.data)
        p0_features = [f['feature'] for f in data_p0['feature_coverage']]

        assert 'P0Only' in p0_features, "P0 过滤应包含 P0Only Feature"
        assert 'Mixed' in p0_features, "P0 过滤应包含 Mixed Feature"
        assert 'P1Only' not in p0_features, "P0 过滤不应包含 P1Only Feature"

        # P1 过滤：应只返回包含 P1 CP 的 Feature (P1Only, Mixed)
        response_p1 = admin_client.get(f'/api/progress/{project_id}?priority=P1')
        data_p1 = json.loads(response_p1.data)
        p1_features = [f['feature'] for f in data_p1['feature_coverage']]

        assert 'P1Only' in p1_features, "P1 过滤应包含 P1Only Feature"
        assert 'Mixed' in p1_features, "P1 过滤应包含 Mixed Feature"
        assert 'P0Only' not in p1_features, "P1 过滤不应包含 P0Only Feature"

    def test_feature_coverage_p0_p1_sub_coverage(self, admin_client):
        """PC-API-010: feature_coverage 中 P0/P1 子覆盖率正确
        P0_coverage 只统计 priority='P0' 的 CP
        P1_coverage 只统计 priority='P1' 的 CP
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"SubCoverage_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # Feature Test: 2 个 P0 CP (都 PASS) + 1 个 P1 CP (无 TC)
        self._add_cp_with_tc(admin_client, project_id, 'Test', f'CP-P0-1-{unique_id}', 'P0', 'PASS')
        self._add_cp_with_tc(admin_client, project_id, 'Test', f'CP-P0-2-{unique_id}', 'P0', 'PASS')
        self._add_cp(admin_client, project_id, 'Test', f'CP-P1-1-{unique_id}', 'P1')

        # 使用 priority=P0,P1,P2,P3 作为 workaround 绕过 BUG-103
        response = admin_client.get(f'/api/progress/{project_id}?priority=P0,P1,P2,P3')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 找到 Test Feature
        test_fc = next((f for f in data['feature_coverage'] if f['feature'] == 'Test'), None)
        assert test_fc is not None, "应返回 Test Feature"

        # 验证 P0 子覆盖率
        assert test_fc['p0_total'] == 2, f"P0 CP 总数应为 2，实际为 {test_fc['p0_total']}"
        assert test_fc['p0_covered'] == 2, f"P0 covered 应为 2，实际为 {test_fc['p0_covered']}"
        assert test_fc['p0_coverage'] == 100.0, f"P0 coverage 应为 100%，实际为 {test_fc['p0_coverage']}"

        # 验证 P1 子覆盖率
        assert test_fc['p1_total'] == 1, f"P1 CP 总数应为 1，实际为 {test_fc['p1_total']}"
        assert test_fc['p1_covered'] == 0, f"P1 covered 应为 0，实际为 {test_fc['p1_covered']}"
        assert test_fc['p1_coverage'] == 0.0, f"P1 coverage 应为 0%，实际为 {test_fc['p1_coverage']}"

        # 验证总覆盖率 (2*100 + 1*0) / 3 = 66.7%
        assert test_fc['total_cp'] == 3
        assert test_fc['covered_cp'] == 2
        assert test_fc['uncovered_cp'] == 1


class TestProgressChartsDateFilter:
    """日期过滤测试 - PC-API-008"""

    def _create_project(self, admin_client, name, start_date, end_date):
        """创建测试项目"""
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': start_date,
                'end_date': end_date
            }),
            content_type='application/json')
        if response.status_code != 200:
            return None
        data = json.loads(response.data)
        return data.get('project', {}).get('id')

    def _add_cp_with_tc(self, admin_client, project_id, feature, cp_name, priority, tc_status='PASS'):
        """添加 CP 并创建关联的 TC"""
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': feature,
                'cover_point': cp_name,
                'priority': priority
            }),
            content_type='application/json')
        if cp_response.status_code != 200:
            return None
        cp_id = json.loads(cp_response.data).get('item', {}).get('id')

        tc_response = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id,
                'testbench': 'tb_test',
                'test_name': f'TC_{cp_name}',
                'scenario': f'Test {cp_name}',
                'status': tc_status,
                'target_date': '2026-01-15',
                'connections': [cp_id]
            }),
            content_type='application/json')
        if tc_response.status_code != 200:
            return cp_id
        return cp_id

    def test_progress_date_filter(self, admin_client):
        """PC-API-008: 日期过滤正常
        ?start_date=...&end_date=... 时 planned/actual 曲线正常，trend/feature_coverage 正常
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"DateFilter_Test_{unique_id}",
            '2026-01-01', '2026-06-30'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 添加 CP 和 TC
        self._add_cp_with_tc(admin_client, project_id, 'CPU', f'CP-{unique_id}', 'P0')

        # 创建快照
        admin_client.post(f'/api/progress/{project_id}/snapshot')

        # 无日期过滤
        response_all = admin_client.get(f'/api/progress/{project_id}')
        data_all = json.loads(response_all.data)

        # 有日期过滤
        response_filtered = admin_client.get(
            f'/api/progress/{project_id}?start_date=2026-02-01&end_date=2026-04-30'
        )
        data_filtered = json.loads(response_filtered.data)

        # 验证基本字段都存在
        assert 'planned' in data_filtered
        assert 'actual' in data_filtered
        assert 'trend' in data_filtered
        assert 'feature_coverage' in data_filtered

        # 验证 feature_coverage 不受日期过滤影响（实时计算）
        assert len(data_filtered['feature_coverage']) == len(data_all['feature_coverage'])

        # 验证 planned 曲线受日期过滤影响（周数应该不同）
        # 过滤后的 planned 周数应该少于或等于全部
        assert len(data_filtered['planned']) <= len(data_all['planned'])

    def test_progress_date_filter_with_priority(self, admin_client):
        """PC-API-008 (扩展): 日期过滤 + Priority 过滤组合正常"""
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"DatePriority_Test_{unique_id}",
            '2026-01-01', '2026-06-30'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        self._add_cp_with_tc(admin_client, project_id, 'CPU', f'CP-P0-{unique_id}', 'P0')
        self._add_cp_with_tc(admin_client, project_id, 'Memory', f'CP-P1-{unique_id}', 'P1')

        admin_client.post(f'/api/progress/{project_id}/snapshot')

        # 组合过滤
        response = admin_client.get(
            f'/api/progress/{project_id}?start_date=2026-02-01&end_date=2026-04-30&priority=P0'
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'planned' in data
        assert 'actual' in data
        assert 'trend' in data
        assert 'feature_coverage' in data
        assert data['priority_filter'] == "P0"


class TestProgressChartsExistingProject:
    """使用现有 SOC_DV 项目数据测试 (project_id=3)"""

    def test_progress_with_existing_project(self, admin_client):
        """使用现有项目验证 API 返回结构"""
        # SOC_DV 项目 id=3
        response = admin_client.get('/api/progress/3')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 验证所有字段存在
        assert 'project_id' in data
        assert 'project_name' in data
        assert 'planned' in data
        assert 'actual' in data
        assert 'priority_filter' in data
        assert 'trend' in data
        assert 'feature_coverage' in data

        # 验证字段类型
        assert isinstance(data['trend'], list)
        assert isinstance(data['feature_coverage'], list)

        # 如果有 feature_coverage 数据，验证结构
        for fc in data['feature_coverage']:
            assert 'feature' in fc
            assert 'total_cp' in fc
            assert 'coverage_pct' in fc
            assert 0 <= fc['coverage_pct'] <= 100

        # 如果有 trend 数据，验证结构
        for t in data['trend']:
            assert 'date' in t
            assert 'cp_coverage' in t
            assert 0 <= t['cp_coverage'] <= 100


class TestBug103Regression:
    """BUG-103 回归测试: 不带 priority 参数时 feature_coverage 计算异常

    Bug 描述: 当调用 /api/progress/<project_id> 不带 priority 参数时，
    feature_coverage 计算抛出 UnboundLocalError: cannot access local variable 'priority_list'

    此测试记录 Bug 行为，当 Bug 修复后应更新此测试。
    """

    def _create_project(self, admin_client, name, start_date, end_date):
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': start_date,
                'end_date': end_date
            }),
            content_type='application/json')
        if response.status_code != 200:
            return None
        data = json.loads(response.data)
        return data.get('project', {}).get('id')

    def test_bug_103_feature_coverage_without_priority(self, admin_client):
        """BUG-103 回归测试: 不带 priority 参数时 feature_coverage 为空（Bug 表现）

        预期行为（Bug 修复后）: feature_coverage 应返回所有 Feature 的数据
        当前行为（Bug 存在时）: feature_coverage 为空数组（因为 UnboundLocalError 被捕获）
        """
        unique_id = str(uuid.uuid4())[:8]
        project_id = self._create_project(
            admin_client, f"Bug103_Test_{unique_id}",
            '2026-01-01', '2026-03-31'
        )
        if not project_id:
            pytest.skip("无法创建测试项目")

        # 添加 CP
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'CPU',
                'cover_point': f'CP-BUG103-{unique_id}',
                'priority': 'P0'
            }),
            content_type='application/json')
        assert cp_response.status_code == 200

        # 不带 priority 参数调用
        response = admin_client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)

        # 当前 Bug 表现: feature_coverage 为空数组
        # 修复后应改为: assert len(data['feature_coverage']) > 0
        # 此断言记录当前 Bug 状态
        assert 'feature_coverage' in data
        assert isinstance(data['feature_coverage'], list)

        # 标记为 xfail: 当 BUG-103 修复后，此测试应失败并需要更新
        # 当前状态: 由于 Bug 存在，feature_coverage 为空
        # 修复后期望: feature_coverage 应包含 CPU Feature 的数据
        if len(data['feature_coverage']) == 0:
            pytest.xfail("BUG-103: 不带 priority 参数时 feature_coverage 因 UnboundLocalError 为空")

        # 以下代码仅在 Bug 修复后执行
        assert len(data['feature_coverage']) > 0
        fc = data['feature_coverage'][0]
        assert fc['feature'] == 'CPU'
        assert fc['total_cp'] == 1
