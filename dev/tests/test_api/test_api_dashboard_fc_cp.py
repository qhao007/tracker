#!/usr/bin/env python3
"""
Tracker Dashboard API 测试用例 - FC-CP 模式支持 (v0.13.0)
测试 GET /api/dashboard/stats 和 /api/dashboard/coverage-matrix 接口的 FC-CP 模式支持
"""

import json
import pytest
import sys
import os
import time

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# 测试项目 ID
TC_CP_PROJECT_ID = 3  # SOC_DV (TC-CP 模式)


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


@pytest.fixture
def fc_cp_project(admin_client):
    """创建 FC-CP 模式的测试项目"""
    name = f"FC_CP_Dashboard_Test_{int(time.time())}"

    response = admin_client.post('/api/projects',
        data=json.dumps({
            'name': name,
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'coverage_mode': 'fc_cp'
        }),
        content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        project_id = data['project']['id']
        yield {'id': project_id, 'name': name}

        # 清理
        admin_client.delete(f"/api/projects/{project_id}")
    else:
        pytest.skip("无法创建测试项目")


@pytest.fixture
def fc_cp_test_data(admin_client, fc_cp_project):
    """创建 FC-CP 模式的测试数据:
    - 5 个 FC (Functional Coverage)
    - 8 个 CP (Cover Point)
    - 部分 FC-CP 关联
    """
    project_id = fc_cp_project['id']
    fc_ids = []
    cp_ids = []

    # 创建 5 个 FC
    csv_data = [
        ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"]
    ]
    for i in range(5):
        csv_data.append([
            f"CG_FC_{i}", f"CP_FC_{i}", "cover", f"bin_{i}", "1",
            str(50.0 + i * 10), "ready", f"Test FC {i}"
        ])

    response = admin_client.post(f'/api/fc/import?project_id={project_id}',
        data=json.dumps({'csv_data': csv_data}),
        content_type='application/json')

    if response.status_code == 200:
        # 获取导入的 FC 列表
        fc_list_response = admin_client.get(f'/api/fc?project_id={project_id}')
        fc_list = json.loads(fc_list_response.data)
        fc_ids = [fc['id'] for fc in fc_list]
    else:
        pytest.skip("无法创建测试 FC 数据")

    # 创建 8 个 CP
    for i in range(8):
        response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': f'Feature_{i // 2}',
                'sub_feature': f'SubFeature_{i}',
                'cover_point': f'CP_Test_{i}',
                'cover_point_details': f'Details {i}',
                'priority': ['P0', 'P1', 'P2'][i % 3]
            }),
            content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            cp_id = data.get('item', {}).get('id')
            if cp_id:
                cp_ids.append(cp_id)

    if len(cp_ids) < 3:
        pytest.skip("无法创建足够的测试 CP 数据")

    # 创建部分 FC-CP 关联
    # FC[0] 关联 CP[0], CP[1]
    # FC[1] 关联 CP[0]
    # FC[2] 关联 CP[2], CP[3], CP[4]
    associations = [
        (fc_ids[0], cp_ids[0]),
        (fc_ids[0], cp_ids[1]),
        (fc_ids[1], cp_ids[0]),
        (fc_ids[2], cp_ids[2]),
        (fc_ids[2], cp_ids[3]),
        (fc_ids[2], cp_ids[4]),
    ]

    for fc_id, cp_id in associations:
        admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': project_id,
                'fc_id': fc_id,
                'cp_id': cp_id
            }),
            content_type='application/json')

    yield {
        'project_id': project_id,
        'fc_ids': fc_ids,
        'cp_ids': cp_ids,
        'associations': associations
    }

    # 清理 CP
    for cp_id in cp_ids:
        try:
            admin_client.delete(f'/api/cp/{cp_id}?project_id={project_id}')
        except:
            pass


# ============ Dashboard Stats FC-CP 模式测试 ============

class TestDashboardStatsFCMode:
    """Dashboard Stats API FC-CP 模式测试 (API-DASH-FC-001 ~ API-DASH-FC-004)"""

    def test_dashboard_stats_fc_cp_mode(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-001: FC-CP 模式返回 FC 统计数据

        验证 FC-CP 模式下:
        - mode 字段为 'fc_cp'
        - item_type 字段为 'FC'
        - 统计数据基于 FC 而非 TC
        """
        project_id = fc_cp_test_data['project_id']
        response = admin_client.get(f'/api/dashboard/stats?project_id={project_id}')

        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        # 验证 mode 和 item_type
        assert data['data']['mode'] == 'fc_cp', "mode 应该为 'fc_cp'"
        assert data['data']['item_type'] == 'FC', "item_type 应该为 'FC'"

        overview = data['data']['overview']

        # FC-CP 模式下 TC 相关字段应为 0
        assert overview['tc_total'] == 0, "FC-CP 模式下 tc_total 应为 0"
        assert overview['tc_pass'] == 0, "FC-CP 模式下 tc_pass 应为 0"
        assert overview['tc_pass_rate'] == 0, "FC-CP 模式下 tc_pass_rate 应为 0"

    def test_dashboard_stats_tc_cp_mode(self, admin_client):
        """API-DASH-FC-002: TC-CP 模式行为保持不变

        验证 TC-CP 模式下:
        - mode 字段为 'tc_cp'
        - item_type 字段为 'TC'
        - 统计数据基于 TC 而非 FC
        """
        response = admin_client.get(f'/api/dashboard/stats?project_id={TC_CP_PROJECT_ID}')

        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        # 验证 mode 和 item_type
        assert data['data']['mode'] == 'tc_cp', "mode 应该为 'tc_cp'"
        assert data['data']['item_type'] == 'TC', "item_type 应该为 'TC'"

        overview = data['data']['overview']

        # TC-CP 模式下统计数据应该正常返回（不一定为 0）
        assert 'tc_total' in overview
        assert 'tc_pass' in overview
        assert 'tc_pass_rate' in overview

    def test_dashboard_stats_response_contains_mode(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-003: 响应包含 mode 字段

        验证 FC-CP 模式和 TC-CP 模式响应都包含 mode 字段
        """
        # FC-CP 模式
        fc_response = admin_client.get(f'/api/dashboard/stats?project_id={fc_cp_test_data["project_id"]}')
        fc_data = json.loads(fc_response.data)
        assert 'mode' in fc_data['data'], "FC-CP 模式响应应包含 mode 字段"

        # TC-CP 模式
        tc_response = admin_client.get(f'/api/dashboard/stats?project_id={TC_CP_PROJECT_ID}')
        tc_data = json.loads(tc_response.data)
        assert 'mode' in tc_data['data'], "TC-CP 模式响应应包含 mode 字段"

    def test_dashboard_stats_fc_cp_count_correct(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-004: FC 统计数量正确

        验证 FC-CP 模式下 (根据 SPEC 节 2.4 正确语义):
        - total_cp = 实际 CP 总数 (不是 FC 总数)
        - covered_cp = 有 coverage_pct > 0 的 FC 关联的 CP 数量
        - unlinked_cp = total_cp - covered_cp
        """
        project_id = fc_cp_test_data['project_id']
        cp_ids = fc_cp_test_data['cp_ids']
        associations = fc_cp_test_data['associations']

        # 计算期望值 (根据 SPEC 节 2.4 正确语义)
        # covered_cp (FC-CP) = 有 coverage_pct > 0 的 FC 关联的 CP
        # 所有测试 FC 的 coverage_pct 都 > 0 (50, 60, 70, 80, 90)
        # 所以只要有关联 FC 的 CP 就是 covered

        # 找出每个 CP 关联的 FC IDs
        cp_to_fcs = {cp_id: [] for cp_id in cp_ids}
        for fc_id, cp_id in associations:
            if cp_id in cp_to_fcs:
                cp_to_fcs[cp_id].append(fc_id)

        # 有 FC 关联且 FC coverage_pct > 0 的 CP 算 covered
        expected_covered_cp = sum(1 for fcs in cp_to_fcs.values() if len(fcs) > 0)
        expected_total_cp = len(cp_ids)
        expected_unlinked_cp = expected_total_cp - expected_covered_cp

        # 获取 API 返回值
        response = admin_client.get(f'/api/dashboard/stats?project_id={project_id}')
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 total_cp (实际 CP 总数)
        assert overview['total_cp'] == expected_total_cp, \
            f"total_cp 应为 {expected_total_cp}，实际为 {overview['total_cp']}"

        # 验证 covered_cp (有 FC 关联的 CP)
        assert overview['covered_cp'] == expected_covered_cp, \
            f"covered_cp 应为 {expected_covered_cp}，实际为 {overview['covered_cp']}"

        # 验证 unlinked_cp
        assert overview['unlinked_cp'] == expected_unlinked_cp, \
            f"unlinked_cp 应为 {expected_unlinked_cp}，实际为 {overview['unlinked_cp']}"

        # 验证覆盖率计算: covered_cp / total_cp * 100
        expected_coverage_rate = round((expected_covered_cp / expected_total_cp * 100), 1) if expected_total_cp > 0 else 0
        assert overview['coverage_rate'] == expected_coverage_rate, \
            f"coverage_rate 应为 {expected_coverage_rate}，实际为 {overview['coverage_rate']}"


# ============ Dashboard Coverage Matrix FC-CP 模式测试 ============

class TestDashboardMatrixFCMode:
    """Dashboard Coverage Matrix API FC-CP 模式测试 (API-DASH-FC-010 ~ API-DASH-FC-013)"""

    def test_dashboard_matrix_fc_cp_mode(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-010: FC-CP 模式返回 FC-CP 矩阵

        验证 FC-CP 模式下:
        - mode 字段为 'fc_cp'
        - 矩阵数据基于 FC-CP 关联计算
        """
        project_id = fc_cp_test_data['project_id']
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={project_id}')

        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        # 验证 mode
        assert data['data']['mode'] == 'fc_cp', "mode 应该为 'fc_cp'"

        # 验证矩阵结构
        matrix_data = data['data']
        assert 'matrix' in matrix_data
        assert 'features' in matrix_data
        assert 'priorities' in matrix_data

    def test_dashboard_matrix_tc_cp_mode(self, admin_client):
        """API-DASH-FC-011: TC-CP 模式行为保持不变

        验证 TC-CP 模式下:
        - mode 字段为 'tc_cp'
        - 矩阵数据基于 TC-CP 关联计算
        """
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={TC_CP_PROJECT_ID}')

        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        # 验证 mode
        assert data['data']['mode'] == 'tc_cp', "mode 应该为 'tc_cp'"

        # 验证矩阵结构
        matrix_data = data['data']
        assert 'matrix' in matrix_data
        assert 'features' in matrix_data
        assert 'priorities' in matrix_data

    def test_dashboard_matrix_response_contains_mode(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-012: 响应包含 mode 字段

        验证 FC-CP 模式和 TC-CP 模式响应都包含 mode 字段
        """
        # FC-CP 模式
        fc_response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={fc_cp_test_data["project_id"]}')
        fc_data = json.loads(fc_response.data)
        assert 'mode' in fc_data['data'], "FC-CP 模式响应应包含 mode 字段"

        # TC-CP 模式
        tc_response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={TC_CP_PROJECT_ID}')
        tc_data = json.loads(tc_response.data)
        assert 'mode' in tc_data['data'], "TC-CP 模式响应应包含 mode 字段"

    def test_dashboard_matrix_fc_cp_mapping_correct(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-013: FC-CP 关联关系正确

        验证矩阵中的覆盖率基于 FC-CP 关联计算:
        - 有 FC 关联的 CP 覆盖率 > 0
        - 无 FC 关联的 CP 覆盖率 = 0
        """
        project_id = fc_cp_test_data['project_id']
        cp_ids = fc_cp_test_data['cp_ids']
        associations = fc_cp_test_data['associations']

        # 计算每个 CP 关联的 FC IDs
        cp_to_fcs = {cp_id: [] for cp_id in cp_ids}
        for fc_id, cp_id in associations:
            if cp_id in cp_to_fcs:
                cp_to_fcs[cp_id].append(fc_id)

        # 获取 API 返回值
        response = admin_client.get(f'/api/dashboard/coverage-matrix?project_id={project_id}')
        data = json.loads(response.data)
        matrix = data['data']['matrix']

        # 遍历矩阵中的每个 CP
        for feature, priorities in matrix.items():
            for priority, cell in priorities.items():
                for cp in cell['cp_list']:
                    cp_id = cp['id']
                    if cp_id in cp_to_fcs:
                        linked_fcs = cp_to_fcs[cp_id]
                        expected_rate = 50.0 + linked_fcs[0] * 10 if linked_fcs else 0

                        # 验证: 有 FC 关联的 CP 覆盖率应该 > 0
                        if len(linked_fcs) > 0:
                            assert cp['coverage_rate'] > 0, \
                                f"CP {cp_id} 有关联 FC，覆盖率应 > 0，实际为 {cp['coverage_rate']}"
                        else:
                            assert cp['coverage_rate'] == 0, \
                                f"CP {cp_id} 无关联 FC，覆盖率应为 0，实际为 {cp['coverage_rate']}"


# ============ Dashboard week_change FC-CP 模式测试 ============

class TestDashboardWeekChangeFCMode:
    """Dashboard week_change API FC-CP 模式测试 (API-DASH-FC-015 ~ API-DASH-FC-017)"""

    def test_dashboard_week_change_fc_cp_covered_cp(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-015: FC-CP 模式 week_change.covered_cp 计算正确

        验证 FC-CP 模式下 week_change.covered_cp 正确计算（首次调用应为 None）
        """
        project_id = fc_cp_test_data['project_id']

        response = admin_client.get(f'/api/dashboard/stats?project_id={project_id}')
        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)

        overview = data['data']['overview']
        week_change = overview['week_change']

        # 首次调用 week_change 应为 None（无历史快照）
        assert week_change['covered_cp'] is None, \
            f"首次调用 week_change.covered_cp 应为 None，实际为 {week_change['covered_cp']}"

    def test_dashboard_week_change_fc_cp_unlinked_cp(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-016: FC-CP 模式 week_change.unlinked_cp 计算正确

        验证 FC-CP 模式下 week_change.unlinked_cp 正确计算（首次调用应为 None）
        """
        project_id = fc_cp_test_data['project_id']

        response = admin_client.get(f'/api/dashboard/stats?project_id={project_id}')
        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)

        overview = data['data']['overview']
        week_change = overview['week_change']

        # 首次调用 week_change 应为 None（无历史快照）
        assert week_change['unlinked_cp'] is None, \
            f"首次调用 week_change.unlinked_cp 应为 None，实际为 {week_change['unlinked_cp']}"

    def test_dashboard_week_change_fc_cp_tc_pass_rate(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-017: FC-CP 模式 week_change.tc_pass_rate 计算正确

        验证 FC-CP 模式下 week_change.tc_pass_rate 正确计算（首次调用应为 None）
        注意: FC-CP 模式下 tc_total=0, tc_pass=0, tc_pass_rate=0
        """
        project_id = fc_cp_test_data['project_id']

        response = admin_client.get(f'/api/dashboard/stats?project_id={project_id}')
        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)

        overview = data['data']['overview']
        week_change = overview['week_change']

        # 首次调用 week_change 应为 None（无历史快照）
        assert week_change['tc_pass_rate'] is None, \
            f"首次调用 week_change.tc_pass_rate 应为 None，实际为 {week_change['tc_pass_rate']}"

        # FC-CP 模式下 TC 相关字段应为 0
        assert overview['tc_total'] == 0, "FC-CP 模式下 tc_total 应为 0"
        assert overview['tc_pass'] == 0, "FC-CP 模式下 tc_pass 应为 0"
        assert overview['tc_pass_rate'] == 0, "FC-CP 模式下 tc_pass_rate 应为 0"


# ============ Dashboard 快照系统 FC-CP 模式测试 ============

class TestSnapshotFCMode:
    """Dashboard 快照系统 FC-CP 模式测试 (API-DASH-FC-025 ~ API-DASH-FC-027)"""

    def test_calculate_current_coverage_fc_cp(self, admin_client):
        """API-DASH-FC-025: FC-CP 模式 calculate_current_coverage 正确

        验证快照系统的 calculate_current_coverage 函数对 FC-CP 模式正确计算
        通过创建快照并验证 cp_covered 值
        注意: 使用独立项目避免 fixture 隔离问题
        """
        # 创建独立项目避免 fixture 状态污染
        name = f"FC_CP_Coverage_Test_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        if response.status_code != 200:
            pytest.skip("无法创建测试项目")

        project_id = json.loads(response.data)['project']['id']

        # 创建 5 个 FC
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"]
        ]
        for i in range(5):
            csv_data.append([
                f"CG_FC_{i}", f"CP_FC_{i}", "cover", f"bin_{i}", "1",
                str(50.0 + i * 10), "ready", f"Test FC {i}"
            ])

        response = admin_client.post(f'/api/fc/import?project_id={project_id}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        if response.status_code != 200:
            admin_client.delete(f'/api/projects/{project_id}')
            pytest.skip("无法创建测试 FC 数据")

        # 获取 FC 列表
        fc_list_response = admin_client.get(f'/api/fc?project_id={project_id}')
        fc_ids = [fc['id'] for fc in json.loads(fc_list_response.data)]

        # 创建 8 个 CP
        cp_ids = []
        for i in range(8):
            response = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': project_id,
                    'feature': f'Feature_{i // 2}',
                    'sub_feature': f'SubFeature_{i}',
                    'cover_point': f'CP_Test_{i}',
                    'cover_point_details': f'Details {i}',
                    'priority': ['P0', 'P1', 'P2'][i % 3]
                }),
                content_type='application/json')
            if response.status_code == 200:
                cp_ids.append(json.loads(response.data).get('item', {}).get('id'))

        if len(cp_ids) < 3:
            admin_client.delete(f'/api/projects/{project_id}')
            pytest.skip("无法创建足够的测试 CP 数据")

        # 创建部分 FC-CP 关联
        associations = [
            (fc_ids[0], cp_ids[0]),
            (fc_ids[0], cp_ids[1]),
            (fc_ids[1], cp_ids[0]),
            (fc_ids[2], cp_ids[2]),
            (fc_ids[2], cp_ids[3]),
            (fc_ids[2], cp_ids[4]),
        ]

        for fc_id, cp_id in associations:
            admin_client.post('/api/fc-cp-association',
                data=json.dumps({
                    'project_id': project_id,
                    'fc_id': fc_id,
                    'cp_id': cp_id
                }),
                content_type='application/json')

        # 计算期望的 cp_covered (有 FC 关联的 CP)
        cp_to_fcs = {cp_id: [] for cp_id in cp_ids}
        for fc_id, cp_id in associations:
            if cp_id in cp_to_fcs:
                cp_to_fcs[cp_id].append(fc_id)

        expected_cp_covered = sum(1 for fcs in cp_to_fcs.values() if len(fcs) > 0)
        expected_cp_total = len(cp_ids)

        # 创建快照
        response = admin_client.post(f'/api/progress/{project_id}/snapshot')
        assert response.status_code == 200, f"快照创建失败: {response.data}"

        # 获取项目快照历史
        response = admin_client.get(f'/api/progress/{project_id}/snapshots')
        assert response.status_code == 200, f"快照查询失败: {response.data}"
        data = json.loads(response.data)

        snapshots = data.get('snapshots', [])
        assert len(snapshots) > 0, "应至少有一个快照"

        # 验证最新快照的 cp_covered 值
        latest_snapshot = snapshots[-1]
        assert latest_snapshot['cp_covered'] == expected_cp_covered, \
            f"cp_covered 应为 {expected_cp_covered}，实际为 {latest_snapshot['cp_covered']}"
        assert latest_snapshot['cp_total'] == expected_cp_total, \
            f"cp_total 应为 {expected_cp_total}，实际为 {latest_snapshot['cp_total']}"

        # 清理
        for cp_id in cp_ids:
            try:
                admin_client.delete(f'/api/cp/{cp_id}?project_id={project_id}')
            except:
                pass
        admin_client.delete(f'/api/projects/{project_id}')

    def test_snapshot_fc_cp_cp_covered(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-026: FC-CP 快照 cp_covered 正确

        验证 FC-CP 模式下快照的 cp_covered 字段正确反映 coverage 状态
        """
        project_id = fc_cp_test_data['project_id']

        # 创建快照
        response = admin_client.post(f'/api/progress/{project_id}/snapshot')
        assert response.status_code == 200, f"快照创建失败: {response.data}"

        # 获取项目快照
        response = admin_client.get(f'/api/progress/{project_id}/snapshots')
        data = json.loads(response.data)
        snapshots = data.get('snapshots', [])
        latest = snapshots[-1]

        # 验证快照数据结构
        assert 'cp_covered' in latest, "快照应包含 cp_covered 字段"
        assert 'cp_total' in latest, "快照应包含 cp_total 字段"
        assert 'tc_pass_count' in latest, "快照应包含 tc_pass_count 字段"
        assert 'tc_total' in latest, "快照应包含 tc_total 字段"

        # FC-CP 模式下 tc 相关字段应为 0
        assert latest['tc_pass_count'] == 0, "FC-CP 模式下 tc_pass_count 应为 0"
        assert latest['tc_total'] == 0, "FC-CP 模式下 tc_total 应为 0"

    def test_snapshot_fc_cp_no_zero_coverage_fc(self, admin_client):
        """API-DASH-FC-027: FC-CP coverage_pct=0 的 FC 不算 covered

        验证只有当 FC 的 coverage_pct > 0 时，其关联的 CP 才算 covered
        注意: 使用独立项目避免 fixture 隔离问题
        """
        # 创建独立项目避免 fixture 状态污染
        name = f"FC_CP_Zero_Coverage_Test_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        if response.status_code != 200:
            pytest.skip("无法创建测试项目")

        project_id = json.loads(response.data)['project']['id']

        # 创建 2 个 FC，一个 coverage_pct=0，一个 coverage_pct=80
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG1", "CP1", "cover", "bin1", "1", "0", "ready", "Zero coverage FC"],
            ["CG2", "CP2", "cover", "bin2", "1", "80", "ready", "Non-zero coverage FC"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={project_id}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        if response.status_code != 200:
            pytest.skip("无法创建 FC 数据")

        # 获取 FC 列表
        fc_list_response = admin_client.get(f'/api/fc?project_id={project_id}')
        fc_list = json.loads(fc_list_response.data)
        fc_zero = fc_list[0]  # coverage_pct=0
        fc_nonzero = fc_list[1]  # coverage_pct=80

        # 创建 2 个 CP
        cp_ids = []
        for i in range(2):
            response = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': project_id,
                    'feature': f'Feature_{i}',
                    'sub_feature': f'SubFeature_{i}',
                    'cover_point': f'CP_Test_{i}',
                    'cover_point_details': f'Details {i}',
                    'priority': 'P0'
                }),
                content_type='application/json')
            if response.status_code == 200:
                cp_ids.append(json.loads(response.data).get('item', {}).get('id'))

        if len(cp_ids) < 2:
            pytest.skip("无法创建足够的 CP 数据")

        # FC_zero 关联 CP[0] (但 coverage_pct=0)
        # FC_nonzero 关联 CP[1] (coverage_pct=80)
        admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': project_id,
                'fc_id': fc_zero['id'],
                'cp_id': cp_ids[0]
            }),
            content_type='application/json')

        admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': project_id,
                'fc_id': fc_nonzero['id'],
                'cp_id': cp_ids[1]
            }),
            content_type='application/json')

        # 创建快照
        response = admin_client.post(f'/api/progress/{project_id}/snapshot')
        assert response.status_code == 200, f"快照创建失败: {response.data}"

        # 获取快照验证
        response = admin_client.get(f'/api/progress/{project_id}/snapshots')
        data = json.loads(response.data)
        snapshots = data.get('snapshots', [])
        latest = snapshots[-1]

        # CP[0] 有关联但 FC coverage_pct=0，不应算 covered
        # CP[1] 有关联且 FC coverage_pct=80，应算 covered
        # 因此 cp_covered 应该为 1（只有 CP[1]）
        assert latest['cp_covered'] == 1, \
            f"cp_covered 应为 1（只有 coverage_pct>0 的 FC 关联的 CP），实际为 {latest['cp_covered']}"

        # 清理
        for cp_id in cp_ids:
            try:
                admin_client.delete(f'/api/cp/{cp_id}?project_id={project_id}')
            except:
                pass

        # 删除测试项目
        try:
            admin_client.delete(f'/api/projects/{project_id}')
        except:
            pass


# ============ Dashboard 回归测试 ============

class TestDashboardRegression:
    """Dashboard API 回归测试 (API-DASH-FC-020 ~ API-DASH-FC-022)"""

    def test_dashboard_coverage_holes_fc_cp_unchanged(self, admin_client, fc_cp_test_data):
        """API-DASH-FC-020: Coverage Holes 在 FC-CP 模式下正常工作

        验证 FC-CP 模式下 coverage-holes API 仍然返回正确数据
        """
        project_id = fc_cp_test_data['project_id']
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={project_id}')

        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        holes_data = data['data']
        assert 'mode' in holes_data
        assert 'critical' in holes_data
        assert 'warning' in holes_data
        assert 'attention' in holes_data

    def test_dashboard_coverage_holes_tc_cp_unchanged(self, admin_client):
        """API-DASH-FC-020b: Coverage Holes 在 TC-CP 模式下正常工作

        验证 TC-CP 模式下 coverage-holes API 行为不变
        """
        response = admin_client.get(f'/api/dashboard/coverage-holes?project_id={TC_CP_PROJECT_ID}')

        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        holes_data = data['data']
        assert 'mode' in holes_data
        assert holes_data['mode'] == 'tc_cp'
        assert 'critical' in holes_data
        assert 'warning' in holes_data
        assert 'attention' in holes_data

    def test_dashboard_owner_stats_unchanged(self, admin_client, fc_cp_project):
        """API-DASH-FC-021: Owner Stats 在 FC-CP 模式下行为不变

        验证 Owner Stats API 不受 FC-CP 模式影响
        注意: Owner Stats 始终从 test_case 表获取数据，与 coverage_mode 无关
        """
        # TC-CP 模式
        response = admin_client.get(f'/api/dashboard/owner-stats?project_id={TC_CP_PROJECT_ID}')
        assert response.status_code == 200, f"TC-CP 模式 API 请求失败: {response.data}"

        # FC-CP 模式 (Owner Stats 应该仍然返回，只是没有 TC 数据)
        response = admin_client.get(f'/api/dashboard/owner-stats?project_id={fc_cp_project["id"]}')
        assert response.status_code == 200, f"FC-CP 模式 API 请求失败: {response.data}"
        data = json.loads(response.data)
        assert data['success'] == True

        # FC-CP 模式下应该没有 owners（因为没有 TC）
        owner_data = data['data']
        assert 'owners' in owner_data
        assert 'summary' in owner_data

    def test_dashboard_stats_tc_cp_backward_compat(self, admin_client):
        """API-DASH-FC-022: TC-CP 模式响应格式兼容

        验证 TC-CP 模式响应格式与之前版本兼容
        """
        response = admin_client.get(f'/api/dashboard/stats?project_id={TC_CP_PROJECT_ID}')
        assert response.status_code == 200, f"API 请求失败: {response.data}"
        data = json.loads(response.data)

        dashboard_data = data['data']
        # 验证原有结构
        assert 'overview' in dashboard_data
        assert 'by_feature' in dashboard_data
        assert 'by_priority' in dashboard_data
        assert 'trend' in dashboard_data
        assert 'top_uncovered' in dashboard_data
        assert 'recent_activity' in dashboard_data

        # 验证概览字段
        overview = dashboard_data['overview']
        assert 'total_cp' in overview
        assert 'covered_cp' in overview
        assert 'coverage_rate' in overview
        assert 'unlinked_cp' in overview
        assert 'tc_total' in overview
        assert 'tc_pass' in overview
        assert 'tc_pass_rate' in overview

        # 验证新增字段
        assert 'mode' in dashboard_data
        assert 'item_type' in dashboard_data
        assert dashboard_data['mode'] == 'tc_cp'
        assert dashboard_data['item_type'] == 'TC'


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])