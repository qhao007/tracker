#!/usr/bin/env python3
"""
Tracker Snapshot API 测试用例 - v0.12.0
测试快照保存 cp_states、tc_states 等功能

测试数据要求:
- CP 数量 >= 5 (SOC_DV: 30)
- TC 数量 >= 10 (SOC_DV: 53)
- TC-CP 连接 >= 3 (SOC_DV: 100)
"""

import json
import pytest
import sys
import os
import time

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# 使用已存在的测试项目 ID (SOC_DV)
TEST_PROJECT_ID = 3


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


# ============ Snapshot API 测试 ============

class TestSnapshotAPI:
    """Snapshot API 测试 (v0.12.0)"""

    def test_api_snap_001_snapshot_saves_cp_states(self, admin_client):
        """API-SNAP-001: 快照正确保存 cp_states (每个CP的覆盖率状态)

        验证:
        1. 创建快照后，progress_data 中包含 cp_states
        2. cp_states 的 key 是 cp_id (字符串)
        3. 每个 cp_states 条目包含: name, coverage_rate, linked_tcs
        """
        # 创建快照
        response = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 200, f"创建快照失败: {response.data}"

        data = json.loads(response.data)
        assert data['success'] == True
        assert 'snapshot' in data

        snapshot = data['snapshot']
        assert 'progress_data' in snapshot

        # 验证 cp_states 存在且不为空
        # progress_data 可能已经是 dict（API 已解析）或 JSON string
        raw_progress_data = snapshot['progress_data']
        if isinstance(raw_progress_data, str):
            progress_data = json.loads(raw_progress_data)
        else:
            progress_data = raw_progress_data
        assert 'cp_states' in progress_data
        cp_states = progress_data['cp_states']
        assert isinstance(cp_states, dict)
        assert len(cp_states) > 0, "cp_states 不应为空"

        # 验证每个 cp_states 条目结构
        for cp_id, cp_info in cp_states.items():
            assert 'name' in cp_info, f"cp_id {cp_id} 缺少 name 字段"
            assert 'coverage_rate' in cp_info, f"cp_id {cp_id} 缺少 coverage_rate 字段"
            assert 'linked_tcs' in cp_info, f"cp_id {cp_id} 缺少 linked_tcs 字段"
            assert isinstance(cp_info['coverage_rate'], (int, float)), \
                f"cp_id {cp_id} coverage_rate 应为数字"
            assert isinstance(cp_info['linked_tcs'], int), \
                f"cp_id {cp_id} linked_tcs 应为整数"

    def test_api_snap_002_snapshot_saves_tc_states(self, admin_client):
        """API-SNAP-002: 快照正确保存 tc_states (每个TC的状态)

        验证:
        1. 创建快照后，progress_data 中包含 tc_states
        2. tc_states 的 key 是 tc_id (字符串)
        3. tc_states 的 value 是 TC 状态字符串 (如 'PASS', 'FAIL', 'OPEN')
        """
        # 创建快照
        response = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 200, f"创建快照失败: {response.data}"

        data = json.loads(response.data)
        assert data['success'] == True
        assert 'snapshot' in data

        snapshot = data['snapshot']
        assert 'progress_data' in snapshot

        # 验证 tc_states 存在且不为空
        # progress_data 可能已经是 dict（API 已解析）或 JSON string
        raw_progress_data = snapshot['progress_data']
        if isinstance(raw_progress_data, str):
            progress_data = json.loads(raw_progress_data)
        else:
            progress_data = raw_progress_data
        assert 'tc_states' in progress_data
        tc_states = progress_data['tc_states']
        assert isinstance(tc_states, dict)
        assert len(tc_states) > 0, "tc_states 不应为空"

        # 验证每个 tc_states 条目结构
        valid_statuses = {'PASS', 'FAIL', 'OPEN', 'CODED', 'N/A'}
        for tc_id, status in tc_states.items():
            assert isinstance(status, str), f"tc_id {tc_id} status 应为字符串"
            assert status in valid_statuses, \
                f"tc_id {tc_id} status '{status}' 不在有效状态列表中: {valid_statuses}"

    def test_api_snap_003_old_snapshot_compatibility(self, admin_client):
        """API-SNAP-003: 旧快照兼容性 (不含 progress_data 的快照)

        验证:
        1. 获取快照列表时，即使某些快照没有 progress_data 字段也不应报错
        2. 没有 progress_data 的快照应返回空字符串或 null
        """
        # 获取所有快照
        response = admin_client.get(f'/api/progress/{TEST_PROJECT_ID}/snapshots')
        assert response.status_code == 200, f"获取快照列表失败: {response.data}"

        data = json.loads(response.data)
        assert 'snapshots' in data
        snapshots = data['snapshots']

        # 如果有快照，验证兼容性
        if len(snapshots) > 0:
            for snap in snapshots:
                # progress_data 字段可能不存在或为空
                if 'progress_data' in snap:
                    # 如果存在，应该是字符串或 null
                    assert snap['progress_data'] is None or \
                           isinstance(snap['progress_data'], str), \
                           f"快照 {snap['id']} 的 progress_data 类型错误"

    def test_api_snap_004_tc_statistics_consistency(self, admin_client):
        """API-SNAP-004: TC 统计一致性 (快照中 tc_states 数量与实际 TC 总数一致)

        验证:
        1. 快照中 tc_states 的条目数应等于项目的实际 TC 总数
        2. 快照中 tc_pass_count 应与 tc_states 中状态为 'PASS' 的数量一致
        """
        # 创建快照
        response = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 200, f"创建快照失败: {response.data}"

        data = json.loads(response.data)
        snapshot = data['snapshot']
        raw_progress_data = snapshot['progress_data']
        if isinstance(raw_progress_data, str):
            progress_data = json.loads(raw_progress_data)
        else:
            progress_data = raw_progress_data

        tc_states = progress_data['tc_states']

        # 获取实际 TC 总数
        response_tc = admin_client.get(f'/api/tc?project_id={TEST_PROJECT_ID}')
        assert response_tc.status_code == 200
        tc_data = json.loads(response_tc.data)
        actual_tc_count = len(tc_data) if isinstance(tc_data, list) else len(tc_data.get('test_cases', []))

        # 验证 tc_states 数量与实际 TC 总数一致
        assert len(tc_states) == actual_tc_count, \
            f"tc_states 数量 ({len(tc_states)}) 与实际 TC 总数 ({actual_tc_count}) 不一致"

        # 验证 tc_pass_count 与 tc_states 中 PASS 数量一致
        pass_count_in_states = sum(1 for s in tc_states.values() if s == 'PASS')
        assert snapshot['tc_pass_count'] == pass_count_in_states, \
            f"tc_pass_count ({snapshot['tc_pass_count']}) 与 tc_states 中 PASS 数量 ({pass_count_in_states}) 不一致"

    def test_api_snap_005_coverage_calculation(self, admin_client):
        """API-SNAP-005: 覆盖率计算正确性

        验证:
        1. actual_coverage 是根据各 CP 覆盖率计算的平均值
        2. cp_covered 计数是有 PASS TC 连接的 CP 数量
        3. coverage_rate 在 0-100 范围内
        """
        # 创建快照
        response = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 200, f"创建快照失败: {response.data}"

        data = json.loads(response.data)
        snapshot = data['snapshot']
        raw_progress_data = snapshot['progress_data']
        if isinstance(raw_progress_data, str):
            progress_data = json.loads(raw_progress_data)
        else:
            progress_data = raw_progress_data

        cp_states = progress_data['cp_states']

        # 验证 actual_coverage 范围
        assert 0 <= snapshot['actual_coverage'] <= 100, \
            f"actual_coverage ({snapshot['actual_coverage']}) 应在 0-100 范围内"

        # 验证 cp_covered 范围
        assert 0 <= snapshot['cp_covered'] <= snapshot['cp_total'], \
            f"cp_covered ({snapshot['cp_covered']}) 应在 0-cp_total ({snapshot['cp_total']}) 范围内"

        # 验证 cp_total 与 cp_states 数量一致
        assert snapshot['cp_total'] == len(cp_states), \
            f"cp_total ({snapshot['cp_total']}) 与 cp_states 数量 ({len(cp_states)}) 不一致"

        # 验证每个 cp 的 coverage_rate 在 0-100 范围内
        for cp_id, cp_info in cp_states.items():
            assert 0 <= cp_info['coverage_rate'] <= 100, \
                f"cp_id {cp_id} coverage_rate ({cp_info['coverage_rate']}) 应在 0-100 范围内"

    def test_api_snap_006_linked_tcs_count(self, admin_client):
        """API-SNAP-006: linked_tcs 计数正确性

        验证:
        1. cp_states 中每个 CP 的 linked_tcs 数量应为非负整数
        2. linked_tcs 计数应与 coverage_detail 中的总数一致 (如果可用)
        """
        # 创建快照
        response = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 200, f"创建快照失败: {response.data}"

        data = json.loads(response.data)
        snapshot = data['snapshot']
        raw_progress_data = snapshot['progress_data']
        if isinstance(raw_progress_data, str):
            progress_data = json.loads(raw_progress_data)
        else:
            progress_data = raw_progress_data
        cp_states = progress_data['cp_states']

        # 获取 CP 列表以验证 coverage_detail
        response_cp = admin_client.get(f'/api/cp?project_id={TEST_PROJECT_ID}')
        assert response_cp.status_code == 200
        cp_data = json.loads(response_cp.data)
        actual_cps = cp_data if isinstance(cp_data, list) else cp_data.get('cover_points', [])

        # 建立 CP ID 到 coverage_detail 的映射
        cp_coverage_map = {}
        for cp in actual_cps:
            cp_id = str(cp['id'])
            coverage_detail = cp.get('coverage_detail', '')
            # coverage_detail 格式如 "2/4" 表示 2 passed / 4 total
            if '/' in coverage_detail:
                parts = coverage_detail.split('/')
                try:
                    total = int(parts[1])
                    cp_coverage_map[cp_id] = total
                except ValueError:
                    pass

        # 验证每个 CP 的 linked_tcs 计数
        for cp_id, cp_info in cp_states.items():
            snapshot_linked_tcs = cp_info['linked_tcs']
            # linked_tcs 应该是非负整数
            assert isinstance(snapshot_linked_tcs, int), \
                f"cp_id {cp_id} linked_tcs 应为整数"
            assert snapshot_linked_tcs >= 0, \
                f"cp_id {cp_id} linked_tcs 不应为负数"

            # 如果 coverage_detail 可用，验证一致性
            if cp_id in cp_coverage_map:
                actual_total = cp_coverage_map[cp_id]
                diff = abs(snapshot_linked_tcs - actual_total)
                assert diff <= 1, \
                    f"cp_id {cp_id} linked_tcs 差异过大: 快照={snapshot_linked_tcs}, API={actual_total}"

    def test_api_snap_007_snapshot_crud_operations(self, admin_client):
        """API-SNAP-007: 快照 CRUD 操作

        验证:
        1. 可以创建新快照
        2. 可以获取快照列表
        3. 可以删除快照
        """
        # 创建快照
        response = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        snapshot_id = data['snapshot']['id']

        # 获取快照列表
        response = admin_client.get(f'/api/progress/{TEST_PROJECT_ID}/snapshots')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'snapshots' in data

        # 确认新快照在列表中
        snapshot_ids = [s['id'] for s in data['snapshots']]
        assert snapshot_id in snapshot_ids, "新创建的快照应在列表中"

        # 删除快照
        response = admin_client.delete(f'/api/progress/snapshots/{snapshot_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True

        # 确认快照已删除
        response = admin_client.get(f'/api/progress/{TEST_PROJECT_ID}/snapshots')
        data = json.loads(response.data)
        snapshot_ids = [s['id'] for s in data['snapshots']]
        assert snapshot_id not in snapshot_ids, "删除的快照不应在列表中"

    def test_api_snap_008_snapshot_requires_admin(self, client):
        """API-SNAP-008: 快照操作需要管理员权限

        验证:
        1. 未登录用户不能创建快照
        2. 返回 401 Unauthorized
        """
        response = client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response.status_code == 401, "未登录用户创建快照应返回 401"

    def test_api_snap_009_snapshot_nonexistent_project(self, admin_client):
        """API-SNAP-009: 不存在的项目返回错误

        验证:
        1. 对不存在的项目ID创建快照应返回 404
        """
        response = admin_client.post('/api/progress/99999/snapshot')
        assert response.status_code == 404, "不存在的项目应返回 404"

    def test_api_snap_010_snapshot_update_existing(self, admin_client):
        """API-SNAP-010: 更新已存在的快照

        验证:
        1. 同一天多次创建快照应更新而非创建新记录
        2. 快照ID保持不变
        """
        # 第一次创建
        response1 = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        snapshot_id1 = data1['snapshot']['id']

        # 第二次创建（同一项目）
        response2 = admin_client.post(f'/api/progress/{TEST_PROJECT_ID}/snapshot')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        snapshot_id2 = data2['snapshot']['id']

        # 同一天创建的快照ID应该相同（更新而非创建）
        assert snapshot_id1 == snapshot_id2, "同一天创建的快照应更新而非创建新记录"

        # 获取快照列表，验证只有一条记录
        response = admin_client.get(f'/api/progress/{TEST_PROJECT_ID}/snapshots')
        data = json.loads(response.data)
        today = time.strftime('%Y-%m-%d')
        today_snaps = [s for s in data['snapshots'] if s['snapshot_date'] == today]
        assert len(today_snaps) == 1, "同一天应该只有一条快照记录"
