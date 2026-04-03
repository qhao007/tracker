#!/usr/bin/env python3
"""
Tracker API 测试用例 - FC-CP 关联测试
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

        name = f"FC_CP_Test_{int(time.time())}"

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


# ============ FC-CP 关联 CRUD 测试 ============

class TestFCCPAssociationList:
    """FC-CP 关联列表 API 测试"""

    def test_get_fc_cp_associations(self, admin_client, test_project):
        """API-FC-CP-001: 获取 FC-CP 关联列表"""
        # 先创建一个关联
        # 创建 CP
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'ListTestFeature',
                'sub_feature': 'ListTestSub',
                'cover_point': 'ListTestCP',
                'priority': 'P1'
            }),
            content_type='application/json')
        if cp_resp.status_code != 200:
            pytest.skip("无法创建测试 CP")
        cp_id = json.loads(cp_resp.data).get('item', {}).get('id')

        # 创建 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_ListTest", "CP_ListTest", "cover", "bin_list", "1", "50.0", "ready", "Test"]
        ]
        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')

        fc_list_resp = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_resp.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_ListTest'), None)
        if not fc:
            pytest.skip("无法创建测试 FC")
        fc_id = fc['id']

        # 创建关联
        admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')

        # 获取关联列表
        response = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')

        assert response.status_code == 200, f"获取关联列表失败: {response.data}"
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1, f"期望至少 1 条关联，实际 {len(data)} 条"

        # 验证关联数据结构
        if len(data) > 0:
            assoc = data[0]
            assert 'id' in assoc
            assert 'cp_id' in assoc
            assert 'fc_id' in assoc

    def test_get_fc_cp_associations_empty(self, admin_client, test_project):
        """获取关联列表 - 无数据"""
        response = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_fc_cp_associations_without_project(self, admin_client):
        """获取关联列表 - 无 project_id"""
        response = admin_client.get('/api/fc-cp-association')

        assert response.status_code == 200  # 返回空列表
        data = json.loads(response.data)
        assert data == []

    def test_get_fc_cp_associations_invalid_project(self, admin_client):
        """获取关联列表 - 无效项目"""
        response = admin_client.get('/api/fc-cp-association?project_id=99999')

        assert response.status_code == 200  # 返回空列表
        data = json.loads(response.data)
        assert data == []

    def test_get_fc_cp_associations_filter_by_cp_id(self, admin_client, test_project):
        """API-FC-CP-005: 按 cp_id 过滤 FC-CP 关联 (BUG-130 回归测试)

        验证 get_fc_cp_associations API 支持 cp_id 参数过滤
        """
        # 创建两个测试 CP
        cp1_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'FilterTestFeature',
                'sub_feature': 'FilterTestSub1',
                'cover_point': 'FilterTestCP1',
                'priority': 'P1'
            }),
            content_type='application/json')
        if cp1_resp.status_code != 200:
            pytest.skip("无法创建测试 CP1")
        cp1_id = json.loads(cp1_resp.data).get('item', {}).get('id')

        cp2_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'FilterTestFeature',
                'sub_feature': 'FilterTestSub2',
                'cover_point': 'FilterTestCP2',
                'priority': 'P1'
            }),
            content_type='application/json')
        if cp2_resp.status_code != 200:
            pytest.skip("无法创建测试 CP2")
        cp2_id = json.loads(cp2_resp.data).get('item', {}).get('id')

        # 创建两个 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["FilterTestCG", "FilterTestCP_1", "cover", "filter_bin_1", "1", "60.0", "ready", "Test1"],
            ["FilterTestCG", "FilterTestCP_2", "cover", "filter_bin_2", "1", "70.0", "ready", "Test2"]
        ]
        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')

        fc_list_resp = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_resp.data)
        fc1 = next((f for f in fc_list if f['bin_name'] == 'filter_bin_1'), None)
        fc2 = next((f for f in fc_list if f['bin_name'] == 'filter_bin_2'), None)
        if not fc1 or not fc2:
            pytest.skip("无法创建测试 FC")

        # CP1 关联 FC1，CP2 关联 FC2
        admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp1_id,
                'fc_id': fc1['id']
            }),
            content_type='application/json')

        admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp2_id,
                'fc_id': fc2['id']
            }),
            content_type='application/json')

        # 测试不过滤时返回 2 条关联
        response_all = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')
        data_all = json.loads(response_all.data)
        assocs_for_project = [a for a in data_all if a.get('cp_id') in (cp1_id, cp2_id)]
        assert len(assocs_for_project) == 2, f"期望 2 条关联，实际 {len(assocs_for_project)} 条"

        # 测试按 cp1_id 过滤只返回 1 条关联
        response_cp1 = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}&cp_id={cp1_id}')
        data_cp1 = json.loads(response_cp1.data)
        assert isinstance(data_cp1, list), "返回数据应为列表"
        assert len(data_cp1) == 1, f"按 cp_id={cp1_id} 过滤后期望 1 条关联，实际 {len(data_cp1)} 条"
        assert data_cp1[0]['cp_id'] == cp1_id, f"过滤结果 cp_id 应为 {cp1_id}"
        assert data_cp1[0]['fc_id'] == fc1['id'], f"过滤结果 fc_id 应为 {fc1['id']}"

        # 测试按 cp2_id 过滤只返回 1 条关联
        response_cp2 = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}&cp_id={cp2_id}')
        data_cp2 = json.loads(response_cp2.data)
        assert len(data_cp2) == 1, f"按 cp_id={cp2_id} 过滤后期望 1 条关联，实际 {len(data_cp2)} 条"
        assert data_cp2[0]['cp_id'] == cp2_id
        assert data_cp2[0]['fc_id'] == fc2['id']


class TestFCCPAssociationCreate:
    """FC-CP 关联创建 API 测试"""

    def test_create_fc_cp_association(self, admin_client, test_project):
        """API-FC-CP-002: 创建 FC-CP 关联"""
        # 创建测试 CP
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'TestCP_Feature',
                'sub_feature': 'TestSubFeature',
                'cover_point': 'TestCP_ForAssoc',
                'priority': 'P1'
            }),
            content_type='application/json')
        assert cp_response.status_code == 200, f"创建CP失败: {cp_response.data}"
        cp_data = json.loads(cp_response.data)
        cp_id = cp_data.get('item', {}).get('id')
        assert cp_id is not None, f"CP ID should not be None, response: {cp_data}"

        # 创建测试 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_TestAssoc", "CP_TestAssoc", "cover", "bin_assoc", "1", "50.0", "ready", "Test"]
        ]
        fc_response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')
        assert fc_response.status_code == 200, f"创建FC失败: {fc_response.data}"

        # 获取 FC ID
        fc_list_response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_response.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_TestAssoc'), None)
        assert fc is not None, "FC should exist after import"
        fc_id = fc['id']

        # 创建关联
        response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')

        assert response.status_code == 201, f"创建关联失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert 'id' in result

    def test_create_fc_cp_association_invalid_cp(self, admin_client, test_project):
        """创建关联 - 无效 CP"""
        # 先创建 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_InvalidCP", "CP_InvalidCP", "cover", "bin_invalid", "1", "50.0", "ready", "Test"]
        ]
        fc_resp = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')
        assert fc_resp.status_code == 200

        fc_list_resp = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_resp.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_InvalidCP'), None)
        fc_id = fc['id']

        response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': 99999,
                'fc_id': fc_id
            }),
            content_type='application/json')

        assert response.status_code == 404, f"无效 CP 应该返回 404: {response.data}"

    def test_create_fc_cp_association_invalid_fc(self, admin_client, test_project):
        """创建关联 - 无效 FC"""
        # 先创建 CP
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'InvalidFC_Feature',
                'sub_feature': 'InvalidFC_Sub',
                'cover_point': 'InvalidFC_CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        assert cp_resp.status_code == 200
        cp_id = json.loads(cp_resp.data).get('item', {}).get('id')

        response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': 99999
            }),
            content_type='application/json')

        assert response.status_code == 404, f"无效 FC 应该返回 404: {response.data}"

    def test_create_fc_cp_association_duplicate(self, admin_client, test_project):
        """创建关联 - 重复关联"""
        # 创建 CP
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'Dup_Feature',
                'sub_feature': 'Dup_Sub',
                'cover_point': 'Dup_CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        cp_id = json.loads(cp_resp.data).get('item', {}).get('id')

        # 创建 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Dup", "CP_Dup", "cover", "bin_dup", "1", "50.0", "ready", "Test"]
        ]
        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')
        fc_list_resp = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_resp.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_Dup'), None)
        fc_id = fc['id']

        # 第一次创建
        response1 = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')
        assert response1.status_code == 201

        # 第二次创建相同关联 - 应该报错
        response2 = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')

        assert response2.status_code == 400, f"重复关联应该返回 400: {response2.data}"

    def test_create_fc_cp_association_missing_params(self, admin_client, test_project):
        """创建关联 - 缺少参数"""
        # 缺少 cp_id
        response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'fc_id': 1
            }),
            content_type='application/json')

        assert response.status_code == 400

        # 缺少 fc_id
        response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': 1
            }),
            content_type='application/json')

        assert response.status_code == 400


class TestFCCPAssociationDelete:
    """FC-CP 关联删除 API 测试"""

    def test_delete_fc_cp_association(self, admin_client, test_project):
        """API-FC-CP-003: 删除 FC-CP 关联"""
        # 创建 CP
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'Del_Feature',
                'sub_feature': 'Del_Sub',
                'cover_point': 'Del_CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        cp_id = json.loads(cp_resp.data).get('item', {}).get('id')

        # 创建 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Del", "CP_Del", "cover", "bin_del", "1", "50.0", "ready", "Test"]
        ]
        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')
        fc_list_resp = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_resp.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_Del'), None)
        fc_id = fc['id']

        # 先创建关联
        create_response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')

        assert create_response.status_code == 201
        assoc_id = json.loads(create_response.data)['id']

        # 删除关联
        delete_response = admin_client.delete(
            f'/api/fc-cp-association?id={assoc_id}&project_id={test_project["id"]}')

        assert delete_response.status_code == 200, f"删除关联失败: {delete_response.data}"
        result = json.loads(delete_response.data)
        assert result.get('success') == True

        # 验证关联已被删除
        list_response = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')
        associations = json.loads(list_response.data)

        deleted_assoc = [a for a in associations if a['id'] == assoc_id]
        assert len(deleted_assoc) == 0, "关联应该已被删除"

    def test_delete_fc_cp_association_invalid_id(self, admin_client, test_project):
        """删除关联 - 无效 ID"""
        response = admin_client.delete(
            f'/api/fc-cp-association?id=99999&project_id={test_project["id"]}')

        # 可能会返回 200（删除不存在的数据）或 404
        assert response.status_code in [200, 404]

    def test_delete_fc_cp_association_missing_id(self, admin_client, test_project):
        """删除关联 - 缺少 ID"""
        # API 使用 query parameter，缺少 id 时返回 400
        response = admin_client.delete('/api/fc-cp-association?project_id={}'.format(test_project["id"]))

        assert response.status_code == 400, f"缺少 ID 应该返回 400: {response.status_code}"

    def test_delete_fc_cp_association_missing_project_id(self, admin_client, test_project):
        """删除关联 - 缺少 project_id"""
        # 先创建一个关联
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'MissProj_Feature',
                'sub_feature': 'MissProj_Sub',
                'cover_point': 'MissProj_CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        cp_id = json.loads(cp_resp.data).get('item', {}).get('id')

        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_MissProj", "CP_MissProj", "cover", "bin_miss", "1", "50.0", "ready", "Test"]
        ]
        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')
        fc_list_resp = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_resp.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_MissProj'), None)
        fc_id = fc['id']

        assoc_resp = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')
        assoc_id = json.loads(assoc_resp.data)['id']

        # 缺少 project_id (只传 id，不传 project_id)
        response = admin_client.delete(f'/api/fc-cp-association?id={assoc_id}')

        assert response.status_code == 400, f"缺少 project_id 应该返回 400: {response.status_code}"


class TestFCCPAssociationImport:
    """FC-CP 关联导入 API 测试"""

    def test_import_fc_cp_association(self, admin_client, test_project):
        """API-FC-CP-004: 导入 FC-CP 关联 CSV"""
        # 先创建 CP 和 FC
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'ImportFeature',
                'sub_feature': 'ImportSubFeature',
                'cover_point': 'ImportCP',
                'cover_point_details': 'Import CP Details',
                'priority': 'P1'
            }),
            content_type='application/json')

        if cp_response.status_code != 200:
            pytest.skip("无法创建测试 CP")

        cp_data = json.loads(cp_response.data)
        cp_id = cp_data.get('item', {}).get('id')

        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Import", "CP_Import", "cover", "bin_import", "1", "50.0", "ready", "Import Test"]
        ]

        fc_response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')

        if fc_response.status_code != 200:
            pytest.skip("无法创建测试 FC")

        # 获取 FC ID
        fc_list_response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_response.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_Import'), None)

        if not fc:
            pytest.skip("无法获取测试 FC")

        # 导入关联 CSV
        assoc_csv = [
            ["cp_feature", "cp_sub_feature", "cp_cover_point", "fc_covergroup", "fc_coverpoint", "fc_bin_name"],
            ["ImportFeature", "ImportSubFeature", "ImportCP", "CG_Import", "CP_Import", "bin_import"]
        ]

        import_response = admin_client.post(
            f'/api/fc-cp-association/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': assoc_csv}),
            content_type='application/json')

        assert import_response.status_code == 200, f"导入关联失败: {import_response.data}"
        result = json.loads(import_response.data)

        assert result.get('success') == True or 'errors' in result or 'imported' in result

        # 验证关联已创建
        list_response = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')
        associations = json.loads(list_response.data)

        # 查找我们刚创建的关联
        new_assoc = [a for a in associations
                    if a.get('cp_feature') == 'ImportFeature'
                    and a.get('fc_covergroup') == 'CG_Import']

        assert len(new_assoc) >= 1, f"期望至少 1 条导入的关联，实际 {len(new_assoc)} 条"

    def test_import_fc_cp_association_empty_csv(self, admin_client, test_project):
        """导入关联 - 空 CSV"""
        response = admin_client.post(
            '/api/fc-cp-association/import',
            data=json.dumps({'project_id': test_project['id'], 'csv_data': []}),
            content_type='application/json')

        assert response.status_code == 400

    def test_import_fc_cp_association_missing_header(self, admin_client, test_project):
        """导入关联 - 缺少表头"""
        assoc_csv = [
            ["cp_feature", "cp_cover_point"],  # 缺少 fc 相关字段
            ["Feature", "CP"]
        ]

        response = admin_client.post(
            f'/api/fc-cp-association/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': assoc_csv}),
            content_type='application/json')

        assert response.status_code == 400

    def test_import_fc_cp_association_invalid_cp(self, admin_client, test_project):
        """导入关联 - CP 不存在"""
        # 先创建 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Inv", "CP_Inv", "cover", "bin_inv", "1", "50.0", "ready", "Invalid Test"]
        ]

        admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')

        # 导入关联时使用不存在的 CP
        assoc_csv = [
            ["cp_feature", "cp_sub_feature", "cp_cover_point", "fc_covergroup", "fc_coverpoint", "fc_bin_name"],
            ["NonExistentFeature", "", "NonExistentCP", "CG_Inv", "CP_Inv", "bin_inv"]
        ]

        response = admin_client.post(
            f'/api/fc-cp-association/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': assoc_csv}),
            content_type='application/json')

        # API 返回 200，但 imported=0, failed>0
        assert response.status_code == 200, f"导入 API 应该返回 200: {response.status_code}"
        result = json.loads(response.data)
        assert result.get('success') == True
        assert result.get('imported') == 0  # 没有成功导入
        assert result.get('failed') > 0  # 有失败的行
        assert len(result.get('errors', [])) > 0  # 有错误信息


class TestFCCPAssociationIntegration:
    """FC-CP 关联集成测试"""

    def test_full_flow(self, admin_client, test_project):
        """完整流程测试: 创建 CP -> 创建 FC -> 创建关联 -> 获取关联 -> 删除关联"""
        # 1. 创建 CP
        cp_response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project['id'],
                'feature': 'FlowFeature',
                'sub_feature': 'FlowSubFeature',
                'cover_point': 'FlowCP',
                'priority': 'P1'
            }),
            content_type='application/json')

        assert cp_response.status_code == 200, f"创建CP失败: {cp_response.data}"
        cp_data = json.loads(cp_response.data)
        cp_id = cp_data.get('item', {}).get('id')
        assert cp_id is not None

        # 2. 创建 FC
        fc_csv = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_Flow", "CP_Flow", "cover", "bin_flow", "1", "50.0", "ready", "Flow Test"]
        ]

        # project_id 在 JSON body 中，不在 query string
        fc_response = admin_client.post(f'/api/fc/import?project_id={test_project["id"]}',
            data=json.dumps({'csv_data': fc_csv}),
            content_type='application/json')
        assert fc_response.status_code == 200, f"创建FC失败: {fc_response.data}"

        # 获取 FC ID
        fc_list_response = admin_client.get(f'/api/fc?project_id={test_project["id"]}')
        fc_list = json.loads(fc_list_response.data)
        fc = next((f for f in fc_list if f['covergroup'] == 'CG_Flow'), None)
        assert fc is not None
        fc_id = fc['id']

        # 3. 创建关联
        assoc_response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': test_project['id'],
                'cp_id': cp_id,
                'fc_id': fc_id
            }),
            content_type='application/json')

        assert assoc_response.status_code == 201, f"创建关联失败: {assoc_response.data}"
        assoc_id = json.loads(assoc_response.data)['id']

        # 4. 获取关联列表
        list_response = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')
        associations = json.loads(list_response.data)

        assoc = next((a for a in associations if a['id'] == assoc_id), None)
        assert assoc is not None
        assert assoc['cp_id'] == cp_id
        assert assoc['fc_id'] == fc_id

        # 5. 删除关联
        delete_response = admin_client.delete(
            f'/api/fc-cp-association?id={assoc_id}&project_id={test_project["id"]}')
        assert delete_response.status_code == 200

        # 6. 验证删除
        list_response2 = admin_client.get(f'/api/fc-cp-association?project_id={test_project["id"]}')
        associations2 = json.loads(list_response2.data)

        deleted_assoc = next((a for a in associations2 if a['id'] == assoc_id), None)
        assert deleted_assoc is None
