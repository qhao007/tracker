#!/usr/bin/env python3
"""
Tracker API 测试用例 - FC 基础 CRUD + 导入导出
v0.11.0 版本新增功能测试
"""

import json
import pytest
import sys
import os
import time

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


@pytest.fixture(scope='module')
def test_project():
    """创建测试项目用于测试"""
    app = create_app(testing=True)
    with app.test_client() as client:
        # 先登录
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"FC_Test_{int(time.time())}"

        # 创建项目
        response = client.post('/api/projects',
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

            # 清理：删除测试项目
            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建测试项目")


@pytest.fixture
def test_cp(admin_client, test_project):
    """创建测试 CP 用于关联测试"""
    # 创建测试 CP
    response = admin_client.post(f'/api/cp?project_id={test_project["id"]}',
        data=json.dumps({
            'feature': 'TestFeature',
            'sub_feature': 'TestSubFeature',
            'cover_point': 'TestCP',
            'cover_point_details': 'Test CP Details',
            'priority': 'P1'
        }),
        content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        cp_id = data.get('id') or data.get('cover_point', {}).get('id')
        yield {'id': cp_id, 'project_id': test_project["id"]}

        # 清理
        try:
            admin_client.delete(f'/api/cp/{cp_id}?project_id={test_project["id"]}')
        except:
            pass
    else:
        pytest.skip("无法创建测试 CP")


@pytest.fixture
def test_fc(admin_client, test_project):
    """创建测试 FC 数据"""
    # 使用导入 API 创建 FC
    csv_data = [
        ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
        ["CG_Test", "CP_Test", "cover", "bin_1", "1", "50.0", "ready", "Test FC"]
    ]

    response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
        data=json.dumps({'csv_data': csv_data}),
        content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        # 获取导入的 FC 列表
        fc_list_response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_response.data)

        if fc_list:
            fc = fc_list[0]
            yield {'id': fc['id'], 'project_id': test_project["id"], 'data': fc}

            # 清理
            try:
                # FC 需要通过删除项目来清理，或者直接删除
                pass
            except:
                pass
        else:
            pytest.skip("无法创建测试 FC")
    else:
        pytest.skip("无法创建测试 FC")


# ============ FC 基础 CRUD 测试 ============

class TestFCListAPI:
    """FC 列表 API 测试"""

    def test_get_fc_list(self, admin_client, test_project):
        """API-FC-001: 获取 FC 列表"""
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')

        assert response.status_code == 200, f"获取 FC 列表失败: {response.data}"

        # 先导入一些 FC 数据
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG1", "CP1", "cover", "bin_1", "1", "50.0", "ready", "Test 1"],
            ["CG1", "CP1", "cover", "bin_2", "2", "60.0", "missing", "Test 2"],
            ["CG2", "CP2", "cover", "bin_3", "3", "70.0", "ready", "Test 3"]
        ]

        import_response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert import_response.status_code == 200, f"导入 FC 失败: {import_response.data}"

        # 再次获取 FC 列表
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) >= 3, f"期望至少 3 条 FC，实际 {len(data)} 条"

        # 验证 FC 数据结构
        if len(data) > 0:
            fc = data[0]
            assert 'covergroup' in fc
            assert 'coverpoint' in fc
            assert 'coverage_type' in fc
            assert 'bin_name' in fc

    def test_get_fc_list_with_filter(self, admin_client, test_project):
        """API-FC-002: 筛选 FC 列表"""
        # 先导入测试数据
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Filter_1", "CP_A", "cover", "bin_1", "1", "50.0", "ready", "Test 1"],
            ["CG_Filter_1", "CP_B", "cover", "bin_2", "2", "60.0", "missing", "Test 2"],
            ["CG_Filter_2", "CP_A", "cover", "bin_3", "3", "70.0", "ready", "Test 3"]
        ]

        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        # 按 covergroup 筛选
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}&covergroup=CG_Filter_1')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert isinstance(data, list)
        for fc in data:
            assert fc['covergroup'] == 'CG_Filter_1'

        # 按 coverpoint 筛选
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}&coverpoint=CP_A')
        data = json.loads(response.data)

        assert response.status_code == 200
        for fc in data:
            assert fc['coverpoint'] == 'CP_A'

        # 按 coverage_type 筛选
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}&coverage_type=cover')
        data = json.loads(response.data)

        assert response.status_code == 200
        for fc in data:
            assert fc['coverage_type'] == 'cover'

        # 按 bin_name 模糊搜索
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}&bin_name=bin_1')
        data = json.loads(response.data)

        assert response.status_code == 200
        for fc in data:
            assert 'bin_1' in fc['bin_name']

    def test_get_fc_list_without_project(self, admin_client):
        """获取 FC 列表 - 无 project_id"""
        response = admin_client.get('/api/fc')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data == []


class TestFCImportAPI:
    """FC 导入 API 测试"""

    def test_fc_import_success(self, admin_client, test_project):
        """API-FC-003: 成功导入 FC"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Import", "CP_Import", "cover", "bin_import_1", "1", "50.0", "ready", "Import Test 1"],
            ["CG_Import", "CP_Import", "cover", "bin_import_2", "2", "60.0", "missing", "Import Test 2"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 200, f"导入 FC 失败: {response.data}"
        result = json.loads(response.data)

        # 验证导入结果
        assert result.get('success') == True or 'imported' in result or 'errors' in result

        # 验证数据确实被导入
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        imported_cg = [fc for fc in data if fc['covergroup'] == 'CG_Import']
        assert len(imported_cg) >= 2, f"期望至少 2 条 CG_Import FC，实际 {len(imported_cg)} 条"

    def test_fc_import_conflict(self, admin_client, test_project):
        """API-FC-004: 导入重复 FC (冲突检测)"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Conflict", "CP_Conflict", "cover", "bin_conflict", "1", "50.0", "ready", "Conflict Test"]
        ]

        # 第一次导入
        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 第二次导入相同数据 - 应该报错或跳过
        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 200, f"重复导入 FC 应该返回 200: {response.data}"
        result = json.loads(response.data)

        # 应该包含错误信息（已存在）
        # 根据 API 实现，重名会跳过而不是报错
        # 所以只应该有一条记录
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        conflict_fc = [fc for fc in data if fc['covergroup'] == 'CG_Conflict']
        assert len(conflict_fc) == 1, f"重复 FC 应该只存在一条，实际 {len(conflict_fc)} 条"

    def test_fc_import_invalid_project(self, admin_client):
        """导入 FC - 无效项目"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name"],
            ["CG", "CP", "cover", "bin_invalid"]
        ]

        response = admin_client.post('/api/fc/import?project_id=99999',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 404, f"无效项目应该返回 404: {response.data}"


class TestFCExportAPI:
    """FC 导出 API 测试"""

    def test_fc_export(self, admin_client, test_project):
        """API-FC-005: 导出 FC"""
        # 先导入一些 FC 数据
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Export", "CP_Export_1", "cover", "bin_export_1", "1", "50.0", "ready", "Export Test 1"],
            ["CG_Export", "CP_Export_2", "cover", "bin_export_2", "2", "60.0", "missing", "Export Test 2"]
        ]

        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        # 导出 FC
        response = admin_client.get(f'/api/fc/export?project_id={test_project["id"]}')

        assert response.status_code == 200, f"导出 FC 失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert 'csv_data' in result

        csv_data = result['csv_data']
        assert isinstance(csv_data, list)
        assert len(csv_data) >= 2, f"期望至少 2 行数据(含表头)，实际 {len(csv_data)} 行"

        # 验证表头
        headers = csv_data[0]
        assert "Covergroup" in headers
        assert "Coverpoint" in headers
        assert "Type" in headers
        assert "Bin_Name" in headers

    def test_fc_export_empty(self, admin_client, test_project):
        """导出 FC - 空数据"""
        response = admin_client.get(f'/api/fc/export?project_id={test_project["id"]}')

        assert response.status_code == 200, f"导出空 FC 应该成功: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert 'csv_data' in result
        # 空数据只有表头行
        assert len(result['csv_data']) >= 1

    def test_fc_export_without_project(self, admin_client):
        """导出 FC - 无 project_id"""
        response = admin_client.get('/api/fc/export')

        assert response.status_code == 400, f"无 project_id 应该返回 400: {response.data}"

    def test_fc_export_invalid_project(self, admin_client):
        """导出 FC - 无效项目"""
        response = admin_client.get('/api/fc/export?project_id=99999')

        assert response.status_code == 404, f"无效项目应该返回 404: {response.data}"


class TestFCBoundaryConditions:
    """FC 边界条件测试"""

    def test_fc_import_empty_csv(self, admin_client, test_project):
        """API-BOUND-001: 导入空 CSV"""
        csv_data = []

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400, f"空 CSV 应该返回 400: {response.data}"

    def test_fc_import_missing_header(self, admin_client, test_project):
        """API-BOUND-003: 缺少必填字段"""
        # 缺少 Covergroup
        csv_data = [
            ["Coverpoint", "Type", "Bin_Name"],
            ["CP", "cover", "bin"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400, f"缺少必填字段应该返回 400: {response.data}"

    def test_fc_import_invalid_format(self, admin_client, test_project):
        """API-BOUND-002: 格式错误 CSV"""
        # 只有表头没有数据
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        # 根据 API 实现，只有表头可能返回错误或成功但导入 0 条
        result = json.loads(response.data)
        # 应该返回 200 但 imported=0 或返回 400
        assert response.status_code in [200, 400]
