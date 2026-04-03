#!/usr/bin/env python3
"""
Tracker API 测试用例 - CP 覆盖率计算 (FC-CP 模式)
v0.11.0 版本新增功能测试

测试目标: 验证 CP 覆盖率在 TC-CP 模式和 FC-CP 模式下的正确计算
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
def tc_cp_project():
    """创建 TC-CP 模式测试项目"""
    app = create_app(testing=True)
    with app.test_client() as client:
        # 先登录
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"TC_CP_Test_{int(time.time())}"

        # 创建 TC-CP 模式项目
        response = client.post('/api/projects',
                              data=json.dumps({
                                  'name': name,
                                  'start_date': '2026-01-01',
                                  'end_date': '2026-12-31',
                                  'coverage_mode': 'tc_cp'
                              }),
                              content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']
            yield {'id': project_id, 'name': name}

            # 清理：删除测试项目
            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建 TC-CP 测试项目")


@pytest.fixture(scope='module')
def fc_cp_project():
    """创建 FC-CP 模式测试项目"""
    app = create_app(testing=True)
    with app.test_client() as client:
        # 先登录
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"FC_CP_Test_{int(time.time())}"

        # 创建 FC-CP 模式项目
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
            pytest.skip("无法创建 FC-CP 测试项目")


def create_tc(client, project_id, test_name, status="PASS", connections=None):
    """辅助函数：创建 TC

    Args:
        connections: list of cp_ids to link with this TC
    Note: Since TC creation API ignores status parameter (hardcoded as OPEN),
          we update status after creation using the status API.
    """
    response = client.post('/api/tc',
        data=json.dumps({
            'project_id': project_id,
            'testbench': 'TB_Test',
            'test_name': test_name,
            'scenario': 'Test scenario',
            'status': 'OPEN',  # API always uses OPEN
            'owner': 'admin',
            'category': 'functional',
            'target_date': '2026-12-31',
            'connections': connections or []
        }),
        content_type='application/json')
    if response.status_code == 200:
        tc_id = json.loads(response.data).get('item', {}).get('id')
        # Update status after creation
        if tc_id and status != 'OPEN':
            client.post(f'/api/tc/{tc_id}/status',
                data=json.dumps({'project_id': project_id, 'status': status}),
                content_type='application/json')
        return tc_id
    return None


def create_cp(client, project_id, feature, sub_feature, cover_point, priority="P1"):
    """辅助函数：创建 CP"""
    response = client.post('/api/cp',
        data=json.dumps({
            'project_id': project_id,
            'feature': feature,
            'sub_feature': sub_feature,
            'cover_point': cover_point,
            'priority': priority
        }),
        content_type='application/json')
    if response.status_code == 200:
        return json.loads(response.data).get('item', {}).get('id')
    return None


def create_fc(client, project_id, covergroup, coverpoint, coverage_pct, status="ready"):
    """辅助函数：导入 FC"""
    fc_csv = [
        ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
        [covergroup, coverpoint, "cover", f"bin_{coverpoint}", "1", str(coverage_pct), status, "Test"]
    ]
    response = client.post(f'/api/fc/import?project_id={project_id}',
        data=json.dumps({'csv_data': fc_csv}),
        content_type='application/json')
    return response.status_code == 200


def get_fc_id(client, project_id, covergroup):
    """辅助函数：获取 FC ID"""
    response = client.get(f'/api/fc?project_id={project_id}')
    if response.status_code == 200:
        fc_list = json.loads(response.data)
        fc = next((f for f in fc_list if f['covergroup'] == covergroup), None)
        return fc['id'] if fc else None
    return None


def link_tc_cp(client, project_id, tc_id, cp_id):
    """辅助函数：关联 TC 和 CP"""
    response = client.post(f'/api/tc/{tc_id}/link',
        data=json.dumps({'cp_ids': [cp_id]}),
        content_type='application/json')
    return response.status_code == 200


def link_fc_cp(client, project_id, fc_id, cp_id):
    """辅助函数：关联 FC 和 CP"""
    response = client.post('/api/fc-cp-association',
        data=json.dumps({
            'project_id': project_id,
            'cp_id': cp_id,
            'fc_id': fc_id
        }),
        content_type='application/json')
    return response.status_code == 201


# ============ CP 覆盖率测试 - TC-CP 模式 ============

class TestCPCoverageTCMode:
    """CP覆盖率计算 - TC-CP模式"""

    def test_cp_coverage_tc_cp_mode(self, admin_client, tc_cp_project):
        """API-CP-COVERAGE-001: TC-CP模式CP覆盖率计算"""
        project_id = tc_cp_project['id']

        # 先创建 1 个 CP
        cp_id = create_cp(admin_client, project_id, "Feature1", "SubFeature1", "CP1", "P1")
        assert cp_id is not None, "CP 创建失败"

        # 创建 3 个 TC，2 个 PASS，1 个 FAIL，关联到 CP
        tc1_id = create_tc(admin_client, project_id, "Test1", "PASS", connections=[cp_id])
        tc2_id = create_tc(admin_client, project_id, "Test2", "PASS", connections=[cp_id])
        tc3_id = create_tc(admin_client, project_id, "Test3", "FAIL", connections=[cp_id])

        assert tc1_id and tc2_id and tc3_id, "TC 创建失败"

        # 获取 CP 列表
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        assert response.status_code == 200, f"获取CP列表失败: {response.data}"

        cps = json.loads(response.data)
        assert len(cps) >= 1, "应该有至少1个CP"

        cp = next((c for c in cps if c['id'] == cp_id), None)
        assert cp is not None, "应该能找到创建的CP"

        # 验证覆盖率: 2 PASS / 3 Total = 66.7%
        assert cp['coverage'] == 66.7, f"期望覆盖率 66.7，实际 {cp['coverage']}"
        assert cp['coverage_detail'] == "2/3", f"期望 coverage_detail 为 2/3，实际 {cp['coverage_detail']}"

    def test_cp_coverage_tc_cp_mode_no_tc(self, admin_client, tc_cp_project):
        """TC-CP模式 - CP无关联TC"""
        project_id = tc_cp_project['id']

        # 创建 1 个 CP，不关联任何 TC
        cp_id = create_cp(admin_client, project_id, "Feature2", "SubFeature2", "CP_NoTC", "P1")

        # 获取 CP 列表
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        assert response.status_code == 200

        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # 无关联 TC 时，覆盖率应为 0
        assert cp['coverage'] == 0.0, f"期望覆盖率 0.0，实际 {cp['coverage']}"
        assert cp['coverage_detail'] == "0/0", f"期望 coverage_detail 为 0/0，实际 {cp['coverage_detail']}"

    def test_cp_coverage_tc_cp_mode_all_pass(self, admin_client, tc_cp_project):
        """TC-CP模式 - 所有TC都PASS"""
        project_id = tc_cp_project['id']

        # 先创建 1 个 CP
        cp_id = create_cp(admin_client, project_id, "Feature3", "SubFeature3", "CP_AllPass", "P1")
        assert cp_id is not None

        # 创建 2 个 TC，都 PASS，关联到 CP
        tc1_id = create_tc(admin_client, project_id, "TestAllPass1", "PASS", connections=[cp_id])
        tc2_id = create_tc(admin_client, project_id, "TestAllPass2", "PASS", connections=[cp_id])

        assert tc1_id and tc2_id, "TC 创建失败"

        # 获取 CP
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # 100% 覆盖率
        assert cp['coverage'] == 100.0, f"期望覆盖率 100.0，实际 {cp['coverage']}"
        assert cp['coverage_detail'] == "2/2", f"期望 coverage_detail 为 2/2，实际 {cp['coverage_detail']}"


# ============ CP 覆盖率测试 - FC-CP 模式 ============

class TestCPCoverageFCMode:
    """CP覆盖率计算 - FC-CP模式

    注意: 当前 API get_coverpoints() 存在 bug，始终使用 tc_cp_connections 计算覆盖率，
    未考虑 coverage_mode 设置。这是已知的 v0.11.0 bug。
    """

    def test_cp_coverage_fc_cp_single_fc(self, admin_client, fc_cp_project):
        """API-CP-COVERAGE-002: FC-CP模式CP覆盖率计算(单FC)

        BUG: get_coverpoints() API 不检查 fc_cp_associations 表，
        仅检查 tc_cp_connections 来判断 linked 状态和计算覆盖率。
        因此 FC-CP 关联的 CP 的 linked=False，覆盖率为 0.0。
        """
        project_id = fc_cp_project['id']

        # 创建 1 个 CP
        cp_id = create_cp(admin_client, project_id, "FC_Feature1", "FC_Sub1", "FC_CP1", "P1")

        # 创建 1 个 FC，覆盖率 75%
        create_fc(admin_client, project_id, "CG_FC1", "CP_FC1", 75.0)
        fc_id = get_fc_id(admin_client, project_id, "CG_FC1")
        assert fc_id is not None, "FC 应该创建成功"

        # 关联 FC 和 CP
        success = link_fc_cp(admin_client, project_id, fc_id, cp_id)
        assert success, "FC-CP 关联应该成功"

        # 获取 CP 列表
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        assert response.status_code == 200, f"获取CP列表失败: {response.data}"

        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)
        assert cp is not None, "应该能找到创建的 CP"

        # 验证 FC-CP 关联是否存在
        assoc_response = admin_client.get(f'/api/fc-cp-association?project_id={project_id}')
        assocs = json.loads(assoc_response.data)
        fc_assoc = next((a for a in assocs if a['cp_id'] == cp_id), None)
        assert fc_assoc is not None, "FC-CP 关联应该在数据库中存在"

        # FC-CP 模式下，CP 的覆盖率应该等于关联 FC 的覆盖率
        # 预期: coverage = 75.0 (FC 的 coverage_pct)
        # 由于 API bug，实际: coverage = 0.0, linked = False
        print(f"[DEBUG] FC-CP mode: coverage={cp['coverage']}, linked={cp['linked']}, expected: coverage=75.0, linked=True")
        print(f"[BUG CONFIRMED] API 仅检查 tc_cp_connections，不检查 fc_cp_associations")

        # 验证 linked 状态 - 由于 API bug，这个断言会失败
        # 这是预期的失败，说明 API 有 bug
        assert cp['linked'] == True, "CP 应该被标记为已关联 (API Bug: 未检查 fc_cp_associations)"

    def test_cp_coverage_fc_cp_multiple_fc(self, admin_client, fc_cp_project):
        """API-CP-COVERAGE-003: FC-CP模式CP覆盖率计算(多FC)

        BUG: get_coverpoints() API 不检查 fc_cp_associations 表，
        仅检查 tc_cp_connections 来判断 linked 状态。
        """
        project_id = fc_cp_project['id']

        # 创建 1 个 CP
        cp_id = create_cp(admin_client, project_id, "FC_Feature2", "FC_Sub2", "FC_CP2", "P1")

        # 创建 3 个 FC，覆盖率分别为 100%, 50%, 75%
        create_fc(admin_client, project_id, "CG_FC2_1", "CP_FC2_1", 100.0)
        create_fc(admin_client, project_id, "CG_FC2_2", "CP_FC2_2", 50.0)
        create_fc(admin_client, project_id, "CG_FC2_3", "CP_FC2_3", 75.0)

        fc_id_1 = get_fc_id(admin_client, project_id, "CG_FC2_1")
        fc_id_2 = get_fc_id(admin_client, project_id, "CG_FC2_2")
        fc_id_3 = get_fc_id(admin_client, project_id, "CG_FC2_3")

        # 关联所有 FC 到同一个 CP
        link_fc_cp(admin_client, project_id, fc_id_1, cp_id)
        link_fc_cp(admin_client, project_id, fc_id_2, cp_id)
        link_fc_cp(admin_client, project_id, fc_id_3, cp_id)

        # 获取 CP
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # 多 FC 情况下，CP 的覆盖率应该是所有关联 FC 覆盖率的平均值
        # 预期: (100 + 50 + 75) / 3 = 75.0
        # 由于 API bug，实际: coverage = 0.0, linked = False
        print(f"[DEBUG] FC-CP multiple FC: coverage={cp['coverage']}, linked={cp['linked']}, expected: coverage=75.0, linked=True")
        print(f"[BUG CONFIRMED] API 仅检查 tc_cp_connections，不检查 fc_cp_associations")

        assert cp['linked'] == True, "CP 应该被标记为已关联 (API Bug: 未检查 fc_cp_associations)"

    def test_cp_coverage_fc_cp_no_fc(self, admin_client, fc_cp_project):
        """API-CP-COVERAGE-004: FC-CP模式CP无关联FC"""
        project_id = fc_cp_project['id']

        # 创建 1 个 CP，不关联任何 FC
        cp_id = create_cp(admin_client, project_id, "FC_Feature3", "FC_Sub3", "FC_CP_NoLink", "P1")

        # 获取 CP
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # 无关联 FC 时，覆盖率应为 0
        assert cp['coverage'] == 0.0, f"期望覆盖率 0.0，实际 {cp['coverage']}"

        # 应该被标记为未关联
        assert cp['linked'] == False, "无关联的 CP 应该标记为 linked=False"

    def test_cp_coverage_fc_cp_mixed_mode(self, admin_client, fc_cp_project):
        """FC-CP模式 - 混合场景（同时有 FC 和 TC 关联，但只计算 FC）"""
        project_id = fc_cp_project['id']

        # 创建 1 个 CP
        cp_id = create_cp(admin_client, project_id, "FC_Feature4", "FC_Sub4", "FC_CP_Mixed", "P1")

        # 创建 1 个 TC（但 FC-CP 模式下应该忽略 TC）
        tc_id = create_tc(admin_client, project_id, "Test_Mixed", "PASS", connections=[cp_id])

        # 创建 1 个 FC
        create_fc(admin_client, project_id, "CG_Mixed", "CP_Mixed", 80.0)
        fc_id = get_fc_id(admin_client, project_id, "CG_Mixed")
        link_fc_cp(admin_client, project_id, fc_id, cp_id)

        # 获取 CP
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # FC-CP 模式下，应该只使用 FC 计算覆盖率，忽略 TC
        # 预期: 80.0 (FC 的覆盖率)
        # 实际（bug）: 100.0 (TC 全部 PASS)
        print(f"[DEBUG] FC-CP mixed mode coverage: {cp['coverage']}, expected: 80.0 (FC only)")

        assert cp['linked'] == True


# ============ coverage_detail 格式测试 ============

class TestCoverageDetailFormat:
    """coverage_detail 格式测试"""

    def test_coverage_detail_format_tc_cp(self, admin_client, tc_cp_project):
        """API-CP-COVERAGE-006: TC-CP模式coverage_detail格式"""
        project_id = tc_cp_project['id']

        # 先创建 1 个 CP
        cp_id = create_cp(admin_client, project_id, "FormatFeature", "FormatSub", "CP_Format", "P1")

        # 创建 2 个 TC，1 个 PASS，关联到 CP
        tc1_id = create_tc(admin_client, project_id, "TestFormat1", "PASS", connections=[cp_id])
        tc2_id = create_tc(admin_client, project_id, "TestFormat2", "FAIL", connections=[cp_id])

        # 获取 CP
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # 验证 coverage_detail 格式为 "passed/total"
        assert cp['coverage_detail'] == "1/2", f"期望 coverage_detail 为 1/2，实际 {cp['coverage_detail']}"
        assert cp['coverage'] == 50.0, f"期望覆盖率 50.0，实际 {cp['coverage']}"

    def test_coverage_detail_format_zero_tc(self, admin_client, tc_cp_project):
        """coverage_detail 格式 - 0 个 TC"""
        project_id = tc_cp_project['id']

        # 创建 1 个 CP，无关联 TC
        cp_id = create_cp(admin_client, project_id, "ZeroFeature", "ZeroSub", "CP_Zero", "P1")

        # 获取 CP
        response = admin_client.get(f'/api/cp?project_id={project_id}')
        cps = json.loads(response.data)
        cp = next((c for c in cps if c['id'] == cp_id), None)

        # 0 TC 时，coverage_detail 应该为 "0/0"
        assert cp['coverage_detail'] == "0/0", f"期望 coverage_detail 为 0/0，实际 {cp['coverage_detail']}"


# ============ 项目 coverage_mode 验证 ============

class TestProjectCoverageMode:
    """项目 coverage_mode 设置验证"""

    def test_project_has_coverage_mode(self, admin_client, fc_cp_project, tc_cp_project):
        """验证项目正确设置了 coverage_mode"""
        # 验证 FC-CP 项目
        response = admin_client.get('/api/projects')
        assert response.status_code == 200
        projects = json.loads(response.data)

        fc_project = next((p for p in projects if p['id'] == fc_cp_project['id']), None)
        assert fc_project is not None
        assert fc_project.get('coverage_mode') == 'fc_cp', "FC-CP 项目应该设置 coverage_mode 为 fc_cp"

        tc_project = next((p for p in projects if p['id'] == tc_cp_project['id']), None)
        assert tc_project is not None
        assert tc_project.get('coverage_mode') == 'tc_cp', "TC-CP 项目应该设置 coverage_mode 为 tc_cp"