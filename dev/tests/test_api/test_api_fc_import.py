#!/usr/bin/env python3
"""
Tracker API 测试用例 - FC 导入与边界条件测试
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

        name = f"FC_Import_Test_{int(time.time())}"

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


# ============ FC 导入边界条件测试 ============

class TestFCImportBoundary:
    """FC 导入边界条件测试"""

    def test_fc_import_empty_csv(self, admin_client, test_project):
        """API-BOUND-001: 导入空 CSV"""
        csv_data = []

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400, f"空 CSV 应该返回 400，实际: {response.status_code}"
        result = json.loads(response.data)
        assert 'error' in result

    def test_fc_import_only_header(self, admin_client, test_project):
        """API-BOUND-002: 只有表头无数据"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        # API 检查 len(csv_data) < 2，所以只有表头时返回 400
        assert response.status_code == 400

    def test_fc_import_missing_required(self, admin_client, test_project):
        """API-BOUND-003: 缺少必填字段"""
        # 缺少 Covergroup
        csv_data = [
            ["Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CP1", "cover", "bin1", "1", "50.0", "ready", "Test"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400, f"缺少必填字段应该返回 400，实际: {response.status_code}"
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Covergroup' in result['error']

    def test_fc_import_missing_coverpoint(self, admin_client, test_project):
        """API-BOUND-003: 缺少 Coverpoint"""
        csv_data = [
            ["Covergroup", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG1", "cover", "bin1", "1", "50.0", "ready", "Test"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400

    def test_fc_import_missing_type(self, admin_client, test_project):
        """API-BOUND-003: 缺少 Type"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG1", "CP1", "bin1", "1", "50.0", "ready", "Test"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400

    def test_fc_import_missing_bin_name(self, admin_client, test_project):
        """API-BOUND-003: 缺少 Bin_Name"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG1", "CP1", "cover", "1", "50.0", "ready", "Test"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert response.status_code == 400

    def test_fc_import_invalid_format(self, admin_client, test_project):
        """API-BOUND-002: 格式错误"""
        # 不是数组格式
        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': 'not an array'}),
            content_type='application/json')

        # 可能会返回 400 或 500
        assert response.status_code in [400, 500]


class TestFCImportDuplicate:
    """FC 导入重名检查测试"""

    def test_fc_unique_constraint(self, admin_client, test_project):
        """API-BOUND-004: FC 唯一性约束 - 同一 FC 不能重复导入"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Unique", "CP_Unique", "cover", "bin_unique", "1", "50.0", "ready", "Unique Test"]
        ]

        # 第一次导入
        response1 = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response1.status_code == 200

        # 第二次导入相同 FC
        response2 = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response2.status_code == 200

        # 验证只有一条记录
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        unique_fc = [fc for fc in data if fc['covergroup'] == 'CG_Unique']
        assert len(unique_fc) == 1, f"FC 唯一性约束失败，期望 1 条，实际 {len(unique_fc)} 条"

    def test_fc_import_same_covergroup_different_coverpoint(self, admin_client, test_project):
        """同一 covergroup 不同 coverpoint - 应该成功"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Diff_CP", "CP_A", "cover", "bin_1", "1", "50.0", "ready", "Test A"],
            ["CG_Diff_CP", "CP_B", "cover", "bin_2", "2", "60.0", "ready", "Test B"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证两条记录
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        cg_diff_cp = [fc for fc in data if fc['covergroup'] == 'CG_Diff_CP']
        assert len(cg_diff_cp) == 2, f"期望 2 条不同 coverpoint 的 FC，实际 {len(cg_diff_cp)} 条"

    def test_fc_import_same_covergroup_coverpoint_different_bin(self, admin_client, test_project):
        """同一 covergroup/coverpoint 不同 bin - 应该成功"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Same", "CP_Same", "cover", "bin_A", "1", "50.0", "ready", "Test A"],
            ["CG_Same", "CP_Same", "cover", "bin_B", "2", "60.0", "ready", "Test B"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证两条记录
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        cg_same = [fc for fc in data if fc['covergroup'] == 'CG_Same']
        assert len(cg_same) == 2, f"期望 2 条不同 bin 的 FC，实际 {len(cg_same)} 条"

    def test_fc_import_partial_duplicate(self, admin_client, test_project):
        """部分重复 - 一些是新导入，一些是重复的"""
        csv_data_1 = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Partial", "CP_Partial", "cover", "bin_new", "1", "50.0", "ready", "New"],
            ["CG_Partial", "CP_Partial", "cover", "bin_dup", "2", "60.0", "ready", "Dup"]
        ]

        # 第一次导入
        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data_1}),
            content_type='application/json')
        assert response.status_code == 200

        csv_data_2 = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Partial", "CP_Partial", "cover", "bin_new_2", "3", "70.0", "ready", "New 2"],
            ["CG_Partial", "CP_Partial", "cover", "bin_dup", "4", "80.0", "ready", "Dup 2"]
        ]

        # 第二次导入，部分重复
        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data_2}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证应该有 3 条（bin_new, bin_dup, bin_new_2）
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        partial_fc = [fc for fc in data if fc['covergroup'] == 'CG_Partial']
        assert len(partial_fc) == 3, f"期望 3 条 FC，实际 {len(partial_fc)} 条"


class TestFCImportDataValidation:
    """FC 导入数据验证测试"""

    def test_fc_import_with_all_fields(self, admin_client, test_project):
        """导入带所有字段的 FC"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Full", "CP_Full", "cover", "bin_full", "1", "75.5", "ready", "Full test data"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证导入结果
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        full_fc = [fc for fc in data if fc['covergroup'] == 'CG_Full']
        assert len(full_fc) == 1
        assert full_fc[0]['coverpoint'] == 'CP_Full'
        assert full_fc[0]['coverage_type'] == 'cover'
        assert full_fc[0]['bin_name'] == 'bin_full'

    def test_fc_import_with_optional_fields_empty(self, admin_client, test_project):
        """导入可选字段为空的 FC"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Opt", "CP_Opt", "cover", "bin_opt", "", "", "", ""]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证导入成功
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        opt_fc = [fc for fc in data if fc['covergroup'] == 'CG_Opt']
        assert len(opt_fc) == 1

    def test_fc_import_multiple_rows(self, admin_client, test_project):
        """导入多行数据"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Multi", "CP_1", "cover", "bin_1", "1", "10.0", "missing", "Row 1"],
            ["CG_Multi", "CP_2", "cover", "bin_2", "2", "20.0", "missing", "Row 2"],
            ["CG_Multi", "CP_3", "cover", "bin_3", "3", "30.0", "missing", "Row 3"],
            ["CG_Multi", "CP_4", "cover", "bin_4", "4", "40.0", "missing", "Row 4"],
            ["CG_Multi", "CP_5", "cover", "bin_5", "5", "50.0", "missing", "Row 5"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证导入结果
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        multi_fc = [fc for fc in data if fc['covergroup'] == 'CG_Multi']
        assert len(multi_fc) == 5, f"期望 5 条 FC，实际 {len(multi_fc)} 条"

    def test_fc_import_different_types(self, admin_client, test_project):
        """导入不同 coverage_type 的 FC"""
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Type", "CP_Type", "cover", "bin_cover", "1", "50.0", "ready", "Cover type"],
            ["CG_Type", "CP_Type", "coverpoint", "bin_cp", "2", "60.0", "ready", "Coverpoint type"],
            ["CG_Type", "CP_Type", "cross", "bin_cross", "3", "70.0", "ready", "Cross type"]
        ]

        response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')
        assert response.status_code == 200

        # 验证导入结果
        response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        data = json.loads(response.data)

        type_fc = [fc for fc in data if fc['covergroup'] == 'CG_Type']
        assert len(type_fc) == 3

        types = set([fc['coverage_type'] for fc in type_fc])
        assert 'cover' in types
        assert 'coverpoint' in types
        assert 'cross' in types
