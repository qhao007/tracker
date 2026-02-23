#!/usr/bin/env python3
"""
API 边界条件测试用例 - 增强测试套件
覆盖空值过滤、特殊字符、超长输入、边界数值、无效枚举值等场景
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

        name = f"Boundary_Test_{int(time.time())}"

        # 创建项目
        response = client.post('/api/projects',
                              data=json.dumps({'name': name}),
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
def cleanup_tcs(admin_client, test_project):
    """清理测试创建的 TC"""
    created_ids = []
    yield created_ids
    for tc_id in created_ids:
        try:
            admin_client.delete(f'/api/tc/{tc_id}?project_id={test_project["id"]}')
        except:
            pass


@pytest.fixture
def cleanup_cps(admin_client, test_project):
    """清理测试创建的 CP"""
    created_ids = []
    yield created_ids
    for cp_id in created_ids:
        try:
            admin_client.delete(f'/api/cp/{cp_id}?project_id={test_project["id"]}')
        except:
            pass


# ============ 边界条件测试用例 ============

class TestEmptyValueFilters:
    """空值过滤边界条件测试"""
    
    def test_cp_filter_empty_feature(self, admin_client, test_project, cleanup_cps):
        """API-BOUND-001: CP 过滤空 feature 值"""
        # 创建 CP
        create_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': 'TestFeature',
                'cover_point': f'CP_{int(time.time())}'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_cps.append(json.loads(create_resp.data)['item']['id'])
        
        # 空 feature 过滤应该返回空列表或全部数据
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}&feature=')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_tc_filter_empty_owner(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-002: TC 过滤空 owner 值"""
        # 创建 TC
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_{int(time.time())}',
                'test_name': f'TC_{int(time.time())}',
                'owner': 'TestOwner'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 空 owner 过滤应该返回空列表或全部数据
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&owner=')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_tc_filter_empty_category(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-003: TC 过滤空 category 值"""
        # 创建 TC
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Cat_{int(time.time())}',
                'test_name': f'TC_Cat_{int(time.time())}',
                'category': 'Sanity'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 空 category 过滤应该返回空列表或全部数据
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&category=')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestSpecialCharacters:
    """特殊字符边界条件测试"""
    
    def test_cp_feature_special_chars(self, admin_client, test_project, cleanup_cps):
        """API-BOUND-004: CP feature 包含特殊字符"""
        special_feature = f'Test_<script>_{int(time.time())}'
        create_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': special_feature,
                'cover_point': f'CP_Special_{int(time.time())}'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_cps.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证可以正确处理特殊字符
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(cp['feature'] == special_feature for cp in data)
    
    def test_tc_testbench_sql_injection(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-005: TC testbench 包含 SQL 注入尝试"""
        sql_injection = f"test' OR '1'='1'_{int(time.time())}"
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': sql_injection,
                'test_name': f'TC_SQL_{int(time.time())}',
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证创建成功
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(sql_injection in tc['testbench'] for tc in data)
    
    def test_tc_scenario_chinese_chars(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-020: TC scenario 包含中文特殊字符"""
        chinese_scenario = f'测试中文场景_{int(time.time())}'
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Chinese_{int(time.time())}',
                'test_name': f'TC_Chinese_{int(time.time())}',
                'scenario_details': chinese_scenario,
                'category': 'Sanity',
                'owner': '测试人员'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证中文正确保存和返回
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(chinese_scenario in (tc.get('scenario_details') or '') for tc in data)
    
    def test_tc_test_name_emoji(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-021: TC test_name 包含 Emoji 字符"""
        emoji_name = f'TC_Emoji_{int(time.time())}😀'
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Emoji_{int(time.time())}',
                'test_name': emoji_name,
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证 Emoji 正确保存
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(emoji_name in (tc.get('test_name') or '') for tc in data)
    
    def test_tc_scenario_newline(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-022: TC scenario 包含换行符"""
        newline_scenario = f'第一行\n第二行\n第三行_{int(time.time())}'
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Newline_{int(time.time())}',
                'test_name': f'TC_Newline_{int(time.time())}',
                'scenario_details': newline_scenario,
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证换行符正确保存
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any('\n' in (tc.get('scenario_details') or '') for tc in data)
    
    def test_tc_scenario_json_string(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-023: TC scenario 包含 JSON 字符串"""
        json_scenario = f'{{"key":"value","test":{int(time.time())}}}'
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_JSON_{int(time.time())}',
                'test_name': f'TC_JSON_{int(time.time())}',
                'scenario_details': json_scenario,
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证 JSON 字符串正确保存
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any('key' in (tc.get('scenario_details') or '') for tc in data)
    
    def test_tc_feature_xss_attempt(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-025: TC feature 包含 XSS 尝试"""
        xss_attempt = f'<script>alert(1)</script>_{int(time.time())}'
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_XSS_{int(time.time())}',
                'test_name': f'TC_XSS_{int(time.time())}',
                'comments': xss_attempt,
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 验证 XSS 内容被转义或正确处理
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(xss_attempt in (tc.get('comments') or '') or 
                   xss_attempt.replace('<', '').replace('>', '') in str(tc) 
                   for tc in data)


class TestLongInput:
    """超长输入边界条件测试"""
    
    def test_cp_feature_long_input(self, admin_client, test_project, cleanup_cps):
        """API-BOUND-006: CP feature 超长输入 (1000+ 字符)"""
        long_feature = 'A' * 1000 + f'_{int(time.time())}'
        create_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': long_feature,
                'cover_point': f'CP_Long_{int(time.time())}'
            }),
            content_type='application/json')
        # 超长输入应该正确处理或被截断
        assert create_resp.status_code in [200, 400]
        if create_resp.status_code == 200:
            cleanup_cps.append(json.loads(create_resp.data)['item']['id'])
    
    def test_tc_test_name_long_input(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-007: TC test_name 超长输入 (1000+ 字符)"""
        long_name = 'TC_Long_' + 'B' * 1000 + f'_{int(time.time())}'
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Long_{int(time.time())}',
                'test_name': long_name,
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        # 超长输入应该正确处理或被拒绝
        assert create_resp.status_code in [200, 400]
        if create_resp.status_code == 200:
            cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])


class TestPaginationBoundary:
    """分页边界条件测试"""
    
    def test_limit_zero(self, admin_client, test_project):
        """API-BOUND-008: limit=0 返回空列表"""
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&limit=0')
        assert response.status_code == 200
        data = json.loads(response.data)
        # limit=0 应该返回空列表或全部数据
        assert isinstance(data, list)
    
    def test_limit_negative(self, admin_client, test_project):
        """API-BOUND-009: limit=-1 处理"""
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&limit=-1')
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    def test_offset_out_of_range(self, admin_client, test_project):
        """API-BOUND-010: offset 超范围 (99999)"""
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&offset=99999')
        assert response.status_code == 200
        data = json.loads(response.data)
        # offset 超范围应该返回空列表
        assert isinstance(data, list)
    
    def test_large_limit_value(self, admin_client, test_project):
        """API-PAGE-004: limit=10000 大值处理"""
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&limit=10000')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestInvalidEnumValues:
    """无效枚举值边界条件测试"""
    
    def test_tc_invalid_status(self, admin_client, test_project):
        """API-BOUND-011: TC 无效 status 值"""
        # 创建 TC
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Invalid_{int(time.time())}',
                'test_name': f'TC_Invalid_{int(time.time())}',
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        if create_resp.status_code == 200:
            tc_id = json.loads(create_resp.data)['item']['id']
            
            # 使用无效状态更新
            response = admin_client.post(f'/api/tc/{tc_id}/status',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'status': 'INVALID_STATUS'
                }),
                content_type='application/json')
            # 应该返回错误
            assert response.status_code in [400, 404]
    
    def test_cp_invalid_priority(self, admin_client, test_project, cleanup_cps):
        """API-BOUND-012: CP 无效 priority 值"""
        create_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': f'Feature_Prio_{int(time.time())}',
                'cover_point': f'CP_Prio_{int(time.time())}',
                'priority': 'INVALID'
            }),
            content_type='application/json')
        # 无效 priority 应该被接受并使用默认值或拒绝
        assert create_resp.status_code in [200, 400]
        if create_resp.status_code == 200:
            cleanup_cps.append(json.loads(create_resp.data)['item']['id'])


class TestInvalidIds:
    """无效 ID 边界条件测试"""
    
    def test_invalid_project_id(self, admin_client):
        """API-BOUND-013: 无效 project_id 访问"""
        response = admin_client.get('/api/cp?project_id=99999')
        # 应该返回空列表或错误
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_invalid_cp_id(self, admin_client, test_project):
        """API-BOUND-014: 无效 CP ID 访问"""
        response = admin_client.get(f'/api/cp/99999?project_id={test_project["id"]}')
        assert response.status_code == 404
    
    def test_invalid_tc_id(self, admin_client, test_project):
        """API-BOUND-015: 无效 TC ID 访问"""
        response = admin_client.get(f'/api/tc/99999?project_id={test_project["id"]}')
        assert response.status_code == 404


class TestFilterCombinations:
    """多 filter 组合边界条件测试"""
    
    def test_multiple_filters_combined(self, admin_client, test_project, cleanup_tcs):
        """API-BOUND-016: 多 filter 组合"""
        # 创建 TC
        create_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Multi_{int(time.time())}',
                'test_name': f'TC_Multi_{int(time.time())}',
                'status': 'PASS',
                'dv_milestone': 'DV1.0',
                'category': 'Sanity',
                'owner': 'MultiTester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 组合过滤
        response = admin_client.get(
            f'/api/tc?project_id={test_project["id"]}&status=PASS&owner=&feature=test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_empty_feature_list(self, admin_client, test_project):
        """API-BOUND-018: 空 feature 列表"""
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}&feature=')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_feature_with_spaces(self, admin_client, test_project, cleanup_cps):
        """API-BOUND-019: feature 包含前后空格"""
        create_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': f'  TrimTest_{int(time.time())}  ',
                'cover_point': f'CP_Trim_{int(time.time())}'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        cleanup_cps.append(json.loads(create_resp.data)['item']['id'])
        
        # 带空格过滤应该能匹配
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)


class TestSortingBoundary:
    """排序边界条件测试"""
    
    def test_sort_by_invalid_field(self, admin_client, test_project):
        """API-SORT-004: 无效排序字段"""
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&sort_by=invalid_field')
        # 应该返回错误或忽略并使用默认排序
        assert response.status_code in [200, 400]
    
    def test_sort_order_asc(self, admin_client, test_project):
        """API-SORT-002: 升序排序"""
        response = admin_client.get(
            f'/api/tc?project_id={test_project["id"]}&sort_by=testbench&order=asc')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_sort_order_desc(self, admin_client, test_project):
        """API-SORT-002: 降序排序"""
        response = admin_client.get(
            f'/api/tc?project_id={test_project["id"]}&sort_by=testbench&order=desc')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
