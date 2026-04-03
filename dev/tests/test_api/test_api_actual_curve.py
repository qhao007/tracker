"""
Tracker 实际曲线与快照 API 测试用例 - v0.8.2
测试实际曲线、快照采集、快照管理、导出功能
"""

import json
import pytest
import sys
import os
import time
import glob
import shutil

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'dev'))


def create_test_client():
    """创建测试客户端"""
    from app import create_app
    app = create_app(testing=True)
    app.config['TESTING'] = True
    return app.test_client()


def cleanup_all_sessions():
    """清理所有 session 文件"""
    session_dir = os.path.join(project_root, 'dev/data/sessions')
    if os.path.exists(session_dir):
        for f in glob.glob(f'{session_dir}/*'):
            try:
                os.remove(f)
            except Exception:
                pass


class TestActualCurveAPI:
    """实际曲线数据 API 测试"""

    def setup_method(self):
        """每个测试前清理并创建新 client"""
        cleanup_all_sessions()
        self.client = create_test_client()
        
        # 登录 admin
        login_resp = self.client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        assert login_resp.status_code == 200

    def _create_project_with_dates(self):
        """创建带日期的测试项目"""
        name = f"Test_Project_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        return data.get('project', {}).get('id')

    def _create_project_with_data(self):
        """创建带 TC/CP 数据的测试项目"""
        name = f"Test_Data_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        
        if not project_id:
            return None
        
        # 添加 CP
        self.client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'Feature1',
                'description': 'Test CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        
        # 添加 TC
        tc_resp = self.client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id,
                'name': 'Test TC',
                'feature': 'Feature1',
                'status': 'PASS'
            }),
            content_type='application/json')
        tc_data = json.loads(tc_resp.data)
        tc_id = tc_data.get('test_case', {}).get('id')
        
        # 获取 CP ID 并关联
        if tc_id:
            cp_resp = self.client.get(f'/api/cp?project_id={project_id}')
            cp_list = json.loads(cp_resp.data)
            if cp_list:
                cp_id = cp_list[0].get('id')
                self.client.post('/api/tc-cp',
                    data=json.dumps({'tc_id': tc_id, 'cp_id': cp_id}),
                    content_type='application/json')
        
        return project_id

    def test_get_progress_with_actual(self):
        """API-ACT-001: 获取含实际曲线数据"""
        project_id = self._create_project_with_data()
        assert project_id is not None, "无法创建测试项目"
            
        response = self.client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'actual' in data
        assert isinstance(data['actual'], list)

    def test_get_progress_actual_empty(self):
        """API-ACT-002: 无快照时返回空数组"""
        project_id = self._create_project_with_dates()
        assert project_id is not None, "无法创建测试项目"
            
        response = self.client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'actual' in data
        assert data['actual'] == []


class TestSnapshotCreationAPI:
    """快照采集 API 测试"""

    def setup_method(self):
        cleanup_all_sessions()
        self.client = create_test_client()
        login_resp = self.client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        assert login_resp.status_code == 200

    def _create_project_with_data(self):
        """创建带数据的项目并返回项目ID"""
        name = f"Snap_Data_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        
        if not project_id:
            return None
        
        # 添加 CP
        cp_resp = self.client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'F1', 'description': 'CP1', 'priority': 'P1'
            }),
            content_type='application/json')
        
        # 添加 TC
        tc_resp = self.client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id, 'name': 'TC1', 'feature': 'F1', 'status': 'PASS'
            }),
            content_type='application/json')
        tc_data = json.loads(tc_resp.data)
        
        # 关联 TC 和 CP
        if tc_data.get('test_case'):
            tc_id = tc_data['test_case']['id']
            cp_list_resp = self.client.get(f'/api/cp?project_id={project_id}')
            cp_list = json.loads(cp_list_resp.data)
            if cp_list:
                cp_id = cp_list[0]['id']
                self.client.post('/api/tc-cp',
                    data=json.dumps({'tc_id': tc_id, 'cp_id': cp_id}),
                    content_type='application/json')
        
        return project_id

    def test_create_snapshot(self):
        """API-ACT-010: 手动创建快照"""
        project_id = self._create_project_with_data()
        assert project_id is not None, "无法创建测试项目"
        
        response = self.client.post(f'/api/progress/{project_id}/snapshot')
        assert response.status_code == 200, f"响应: {response.status_code} - {response.data}"
        data = json.loads(response.data)
        
        assert data.get('success') is True
        assert 'snapshot' in data

    def test_create_snapshot_calculates(self):
        """API-ACT-011: 快照计算正确覆盖率"""
        project_id = self._create_project_with_data()
        assert project_id is not None, "无法创建测试项目"
        
        response = self.client.post(f'/api/progress/{project_id}/snapshot')
        assert response.status_code == 200, f"响应: {response.status_code} - {response.data}"
        data = json.loads(response.data)
        
        snapshot = data.get('snapshot', {})
        assert 'actual_coverage' in snapshot, f"快照数据: {snapshot}"
        assert 'tc_pass_count' in snapshot
        assert 'tc_total' in snapshot
        assert 'cp_covered' in snapshot
        assert 'cp_total' in snapshot
        assert snapshot['tc_pass_count'] >= 0, "TC 通过数应为非负数"

    def test_snapshot_matches_dashboard_coverage(self):
        """
        API-ACT-013: 快照 actual_coverage 应与 Dashboard 概览一致
        v0.11.0: 验证 calculate_current_coverage 与 get_dashboard_stats 使用相同的算法
        """
        # 使用 SOC_DV 项目验证
        resp = self.client.get('/api/projects')
        projects = json.loads(resp.data)
        soc_dv = next((p for p in projects if p.get('name') == 'SOC_DV'), None)
        if not soc_dv:
            pytest.skip("SOC_DV 项目不存在")
        project_id = soc_dv['id']

        # 获取 Dashboard 概览覆盖率
        dash_resp = self.client.get(f'/api/dashboard/stats?project_id={project_id}')
        dash_data = json.loads(dash_resp.data)
        dashboard_rate = dash_data['data']['overview']['coverage_rate']

        # 创建新快照
        snap_resp = self.client.post(f'/api/progress/{project_id}/snapshot')
        assert snap_resp.status_code == 200, f"创建快照失败: {snap_resp.status_code}"
        snap_data = json.loads(snap_resp.data)
        snapshot = snap_data.get('snapshot', {})

        actual_coverage = snapshot.get('actual_coverage')
        assert actual_coverage is not None, "快照应有 actual_coverage 字段"

        # 快照覆盖率应与 Dashboard 概览一致（新算法）
        assert actual_coverage == dashboard_rate, \
            f"快照覆盖率({actual_coverage}%)应与 Dashboard 概览({dashboard_rate}%)一致"

    def test_snapshot_per_cp_coverage_average(self):
        """
        API-ACT-014: 快照使用"每个 CP 覆盖率求平均"算法
        验证：CP 覆盖率 = PASS TC数 / 关联TC总数
        """
        name = f"Snap_PerCP_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        assert project_id is not None

        # 添加 2 个 CP
        cp1_resp = self.client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'F1', 'description': 'CP1', 'priority': 'P0'
            }),
            content_type='application/json')
        cp2_resp = self.client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'F2', 'description': 'CP2', 'priority': 'P0'
            }),
            content_type='application/json')

        # 获取 CP 列表以获取 ID
        cp_list_resp = self.client.get(f'/api/cp?project_id={project_id}')
        cp_list = json.loads(cp_list_resp.data)
        assert len(cp_list) >= 2, f"应该有 2 个 CP，实际: {len(cp_list)}"

        cp1_id = next(cp['id'] for cp in cp_list if cp['feature'] == 'F1')
        cp2_id = next(cp['id'] for cp in cp_list if cp['feature'] == 'F2')

        # 添加 2 个 TC，关联到不同的 CP
        # 注意：TC 创建 API 使用 test_name 而不是 name，status 总是 OPEN
        tc1_resp = self.client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id, 'testbench': 'TB1', 'test_name': 'TC1', 'feature': 'F1', 'status': 'OPEN',
                'connections': [cp1_id]  # TC1 关联 CP1
            }),
            content_type='application/json')
        tc1_data = json.loads(tc1_resp.data)
        tc1_id = tc1_data.get('item', {}).get('id')
        assert tc1_id is not None, f"TC1 创建失败: {tc1_resp.data}"

        # 更新 TC1 状态为 PASS
        self.client.post(f'/api/tc/{tc1_id}/status',
            data=json.dumps({'project_id': project_id, 'status': 'PASS'}),
            content_type='application/json')

        tc2_resp = self.client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id, 'testbench': 'TB2', 'test_name': 'TC2', 'feature': 'F2', 'status': 'OPEN',
                'connections': [cp2_id]  # TC2 关联 CP2
            }),
            content_type='application/json')
        tc2_data = json.loads(tc2_resp.data)
        tc2_id = tc2_data.get('item', {}).get('id')
        assert tc2_id is not None, f"TC2 创建失败: {tc2_resp.data}"

        # 更新 TC2 状态为 PASS
        self.client.post(f'/api/tc/{tc2_id}/status',
            data=json.dumps({'project_id': project_id, 'status': 'PASS'}),
            content_type='application/json')

        # 创建快照
        snap_resp = self.client.post(f'/api/progress/{project_id}/snapshot')
        snap_data = json.loads(snap_resp.data)
        snapshot = snap_data.get('snapshot', {})

        # CP1: 1/1 = 100%, CP2: 1/1 = 100%
        # 平均覆盖率 = (100 + 100) / 2 = 100%
        assert snapshot['actual_coverage'] == 100.0, \
            f"两个CP各100%，平均应为100%，实际为 {snapshot['actual_coverage']}%"

    def test_snapshot_partial_cp_coverage(self):
        """
        API-ACT-015: CP 部分 TC PASS 时，按比例计算覆盖率
        验证：CP 覆盖率 = PASS TC数 / 关联TC总数
        """
        name = f"Snap_Partial_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        assert project_id is not None

        # 添加 1 个 CP
        cp_resp = self.client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'F1', 'description': 'CP1', 'priority': 'P0'
            }),
            content_type='application/json')

        # 添加 2 个 TC，都关联到同一个 CP
        # 先获取 CP ID
        cp_list_resp = self.client.get(f'/api/cp?project_id={project_id}')
        cp_list = json.loads(cp_list_resp.data)
        assert len(cp_list) > 0, "应该有 CP"
        cp_id = cp_list[0]['id']

        tc1_resp = self.client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id, 'testbench': 'TB1', 'test_name': 'TC1', 'feature': 'F1', 'status': 'OPEN',
                'connections': [cp_id]  # 关联到 CP
            }),
            content_type='application/json')
        tc1_data = json.loads(tc1_resp.data)
        tc1_id = tc1_data.get('item', {}).get('id')
        assert tc1_id is not None, f"TC1 创建失败: {tc1_resp.data}"

        # 更新 TC1 状态为 PASS
        self.client.post(f'/api/tc/{tc1_id}/status',
            data=json.dumps({'project_id': project_id, 'status': 'PASS'}),
            content_type='application/json')

        tc2_resp = self.client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id, 'testbench': 'TB2', 'test_name': 'TC2', 'feature': 'F1', 'status': 'OPEN',
                'connections': [cp_id]  # 关联到同一个 CP
            }),
            content_type='application/json')
        tc2_data = json.loads(tc2_resp.data)
        tc2_id = tc2_data.get('item', {}).get('id')
        assert tc2_id is not None, f"TC2 创建失败: {tc2_resp.data}"

        # 更新 TC2 状态为 FAIL
        self.client.post(f'/api/tc/{tc2_id}/status',
            data=json.dumps({'project_id': project_id, 'status': 'FAIL'}),
            content_type='application/json')

        # 创建快照
        snap_resp = self.client.post(f'/api/progress/{project_id}/snapshot')
        snap_data = json.loads(snap_resp.data)
        snapshot = snap_data.get('snapshot', {})

        # CP: 1/2 = 50% (1个PASS，1个FAIL)
        assert snapshot['actual_coverage'] == 50.0, \
            f"CP 关联 2 个 TC（1个PASS），覆盖率应为 50%，实际为 {snapshot['actual_coverage']}%"

    def test_create_snapshot_no_auth(self):
        """测试未登录无法创建快照"""
        # 创建未登录的 client
        client = create_test_client()
        
        # 先用 admin 创建一个项目
        admin_client = create_test_client()
        admin_client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        name = f"NoAuth_Test_{int(time.time() * 1000)}"
        resp = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        
        # 未登录 client 尝试创建快照
        if project_id:
            response = client.post(f'/api/progress/{project_id}/snapshot')
            assert response.status_code in [401, 302, 403], f"未登录应该返回 401/302/403，实际: {response.status_code}"

    def test_cron_snapshot_requires_token(self):
        """API-ACT-012: 定时任务需 Token"""
        import os
        # 先设置 CRON_API_TOKEN 环境变量（否则会返回500 "Cron not configured"）
        os.environ['CRON_API_TOKEN'] = 'test-cron-token'
        client = create_test_client()
        # 不带 token 请求应返回 401
        response = client.post('/api/cron/progress-snapshot')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data


class TestSnapshotManagementAPI:
    """快照管理 API 测试"""

    def setup_method(self):
        cleanup_all_sessions()
        self.client = create_test_client()
        login_resp = self.client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        assert login_resp.status_code == 200

    def _create_project_with_snapshot(self):
        """创建带快照的项目，返回 (project_id, snapshot_id)"""
        name = f"Snap_List_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        
        if not project_id:
            return None, None
        
        # 添加 CP 和 TC
        self.client.post('/api/cp',
            data=json.dumps({'project_id': project_id, 'feature': 'F1', 'description': 'C1', 'priority': 'P1'}),
            content_type='application/json')
        
        tc_resp = self.client.post('/api/tc',
            data=json.dumps({'project_id': project_id, 'name': 'TC1', 'feature': 'F1', 'status': 'PASS'}),
            content_type='application/json')
        tc_data = json.loads(tc_resp.data)
        
        # 关联
        if tc_data.get('test_case'):
            tc_id = tc_data['test_case']['id']
            cp_resp = self.client.get(f'/api/cp?project_id={project_id}')
            cp_list = json.loads(cp_resp.data)
            if cp_list:
                cp_id = cp_list[0]['id']
                self.client.post('/api/tc-cp',
                    data=json.dumps({'tc_id': tc_id, 'cp_id': cp_id}),
                    content_type='application/json')
        
        # 创建快照
        snap_resp = self.client.post(f'/api/progress/{project_id}/snapshot')
        snap_data = json.loads(snap_resp.data)
        snapshot_id = snap_data.get('snapshot', {}).get('id')
        
        return project_id, snapshot_id

    def test_get_snapshots(self):
        """API-ACT-020: 获取快照列表"""
        project_id, _ = self._create_project_with_snapshot()
        assert project_id is not None, "无法创建测试项目"
        
        response = self.client.get(f'/api/progress/{project_id}/snapshots')
        assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data}"
        data = json.loads(response.data)
        
        assert 'snapshots' in data
        assert isinstance(data['snapshots'], list)
        assert len(data['snapshots']) > 0, "应该至少有一个快照"

    def test_delete_snapshot_admin(self):
        """API-ACT-021: admin 可删除快照"""
        project_id, snapshot_id = self._create_project_with_snapshot()
        assert project_id is not None and snapshot_id is not None, "无法创建测试数据"
        
        response = self.client.delete(f'/api/progress/snapshots/{snapshot_id}')
        assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data}"
        data = json.loads(response.data)
        assert data.get('success') is True

    def test_delete_current_week_warns(self):
        """API-ACT-023: 删除当周快照有提示"""
        project_id, snapshot_id = self._create_project_with_snapshot()
        assert project_id is not None and snapshot_id is not None, "无法创建测试数据"
        
        response = self.client.delete(f'/api/progress/snapshots/{snapshot_id}')
        assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data}"
        data = json.loads(response.data)
        
        assert 'is_current_week' in data, "应该返回 is_current_week 标志"


class TestExportAPI:
    """导出功能 API 测试"""

    def setup_method(self):
        cleanup_all_sessions()
        self.client = create_test_client()
        login_resp = self.client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        assert login_resp.status_code == 200

    def _create_project_with_snapshot(self):
        """创建带快照的项目"""
        name = f"Export_Test_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        
        if not project_id:
            return None
        
        # 添加 CP 和 TC
        self.client.post('/api/cp',
            data=json.dumps({'project_id': project_id, 'feature': 'F1', 'description': 'C1', 'priority': 'P1'}),
            content_type='application/json')
        
        tc_resp = self.client.post('/api/tc',
            data=json.dumps({'project_id': project_id, 'name': 'TC1', 'feature': 'F1', 'status': 'PASS'}),
            content_type='application/json')
        tc_data = json.loads(tc_resp.data)
        
        # 关联
        if tc_data.get('test_case'):
            tc_id = tc_data['test_case']['id']
            cp_resp = self.client.get(f'/api/cp?project_id={project_id}')
            cp_list = json.loads(cp_resp.data)
            if cp_list:
                cp_id = cp_list[0]['id']
                self.client.post('/api/tc-cp',
                    data=json.dumps({'tc_id': tc_id, 'cp_id': cp_id}),
                    content_type='application/json')
        
        # 创建快照
        self.client.post(f'/api/progress/{project_id}/snapshot')
        
        return project_id

    def test_export_progress(self):
        """API-ACT-030: 导出进度数据"""
        project_id = self._create_project_with_snapshot()
        assert project_id is not None, "无法创建测试项目"
        
        response = self.client.get(f'/api/progress/{project_id}/export')
        assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data}"
        
        data = response.data.decode('utf-8')
        assert 'snapshot_date' in data
        assert 'actual_coverage' in data

    def test_export_progress_empty(self):
        """测试无快照时导出空数据"""
        name = f"Empty_Export_{int(time.time() * 1000)}"
        resp = self.client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        data = json.loads(resp.data)
        project_id = data.get('project', {}).get('id')
        
        assert project_id is not None, "无法创建测试项目"
        
        response = self.client.get(f'/api/progress/{project_id}/export')
        assert response.status_code == 200
        
        data = response.data.decode('utf-8')
        lines = data.strip().split('\n')
        assert len(lines) == 1, "应该只有表头"
