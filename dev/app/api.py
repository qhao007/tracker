"""
Tracker API 路由 - v0.3 独立数据库版本
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app, g
from datetime import datetime
import json
import os
import sqlite3
import uuid

api = Blueprint('api', __name__)

# 项目列表文件
PROJECTS_FILE = 'data/projects.json'

def get_projects_file():
    """获取项目列表文件路径"""
    return os.path.join(current_app.config['DATA_DIR'], 'projects.json')

def load_projects():
    """加载项目列表"""
    filepath = get_projects_file()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_projects(projects):
    """保存项目列表"""
    filepath = get_projects_file()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def get_db_path(project_name):
    """获取项目数据库文件路径"""
    safe_name = project_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    return os.path.join(current_app.config['DATA_DIR'], f'{safe_name}.db')

def get_db(project_name):
    """获取项目数据库连接"""
    if 'db_connections' not in g:
        g.db_connections = {}
    
    if project_name not in g.db_connections:
        db_path = get_db_path(project_name)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db_connections[project_name] = conn
    
    return g.db_connections[project_name]

def init_project_db(project_name):
    """初始化项目数据库"""
    db_path = get_db_path(project_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建 Cover Points 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cover_point (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            feature TEXT,
            sub_feature TEXT,
            cover_point TEXT,
            cover_point_details TEXT,
            comments TEXT,
            priority TEXT DEFAULT 'P0',
            created_at TEXT
        )
    ''')
    
    # 创建 Test Cases 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_case (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            dv_milestone TEXT,
            testbench TEXT,
            category TEXT,
            owner TEXT,
            test_name TEXT,
            scenario_details TEXT,
            checker_details TEXT,
            coverage_details TEXT,
            comments TEXT,
            status TEXT DEFAULT 'OPEN',
            created_at TEXT,
            coded_date TEXT,
            fail_date TEXT,
            pass_date TEXT,
            removed_date TEXT,
            target_date TEXT
        )
    ''')
    
    # 创建关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tc_cp_connections (
            tc_id INTEGER,
            cp_id INTEGER,
            PRIMARY KEY (tc_id, cp_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def delete_project_db(project_name):
    """删除项目数据库文件"""
    db_path = get_db_path(project_name)
    if os.path.exists(db_path):
        os.remove(db_path)

def jsonify_project(project_name, data):
    """将项目数据转为列表格式"""
    return jsonify(data)

# ============ 版本信息 ============

@api.route('/api/version', methods=['GET'])
def get_version():
    """获取版本信息"""
    import os
    version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
    version = '1.0.0'
    release_date = '2026-02-04'
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == 'VERSION':
                            version = value
                        elif key == 'RELEASE_DATE':
                            release_date = value
        except:
            pass
    return jsonify({
        'version': version,
        'version_type': '正式版',
        'release_date': release_date
    })

# ============ 项目管理 ============

@api.route('/api/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    projects = load_projects()
    result = []
    for p in projects:
        if p.get('is_archived', False):
            continue
        
        # 统计项目数据
        try:
            db = get_db(p['name'])
            cursor = db.cursor()
            cursor.execute('SELECT COUNT(*) FROM cover_point')
            cp_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM test_case')
            tc_count = cursor.fetchone()[0]
        except:
            cp_count = 0
            tc_count = 0
        
        result.append({
            'id': p['id'],
            'name': p['name'],
            'created_at': p.get('created_at', ''),
            'is_archived': False,
            'version': p.get('version', 'stable'),
            'cp_count': cp_count,
            'tc_count': tc_count
        })
    
    return jsonify(result)

@api.route('/api/projects', methods=['POST'])
def create_project():
    """创建新项目"""
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': '项目名称不能为空'}), 400
    
    projects = load_projects()
    if any(p['name'] == name and not p.get('is_archived', False) for p in projects):
        return jsonify({'error': f'项目 "{name}" 已存在'}), 400
    
    # 创建项目数据库
    init_project_db(name)
    
    # 添加到项目列表
    project = {
        'id': len(projects) + 1,
        'name': name,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_archived': False,
        'version': 'stable'
    }
    projects.append(project)
    save_projects(projects)
    
    return jsonify({'success': True, 'project': project})

@api.route('/api/projects/<int:project_id>/archive', methods=['POST'])
def archive_project(project_id):
    """备份项目"""
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    # 收集项目数据
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM cover_point')
    cps = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('SELECT * FROM test_case')
    tcs = [dict(row) for row in cursor.fetchall()]
    
    project_data = {
        'id': project['id'],
        'name': project['name'],
        'created_at': project.get('created_at', ''),
        'version': project.get('version', 'stable'),
        'cover_points': cps,
        'test_cases': tcs,
        'backup_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 生成备份文件
    filename = f"{project['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = f"archives/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        'success': True,
        'filename': filename
    })

@api.route('/api/projects/archive/list', methods=['GET'])
def list_archives():
    """获取归档列表"""
    archives_dir = 'archives'
    if not os.path.exists(archives_dir):
        return jsonify([])
    
    archives = []
    for f in os.listdir(archives_dir):
        if f.endswith('.json') and not f.startswith('ArchiveTest'):
            filepath = os.path.join(archives_dir, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    archives.append({
                        'id': len(archives) + 1,
                        'project_name': data.get('name', f),
                        'backup_date': data.get('backup_date', '')
                    })
            except:
                pass
    
    return jsonify(archives)

@api.route('/api/projects/restore', methods=['POST'])
def restore_project():
    """从归档恢复项目"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': '需要指定备份文件名'}), 400
    
    filepath = f"archives/{filename}"
    if not os.path.exists(filepath):
        return jsonify({'error': '备份文件不存在'}), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        project_data = json.load(f)
    
    project_name = project_data.get('name')
    
    # 检查项目是否已存在
    projects = load_projects()
    if any(p['name'] == project_name and not p.get('is_archived', False) for p in projects):
        return jsonify({'error': f'项目 "{project_name}" 已存在，无法恢复'}), 400
    
    # 初始化新项目数据库
    init_project_db(project_name)
    conn = get_db(project_name)
    cursor = conn.cursor()
    
    # 恢复 Cover Points
    for cp_data in project_data.get('cover_points', []):
        cursor.execute('''
            INSERT INTO cover_point (project_id, feature, sub_feature, cover_point, cover_point_details, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cp_data.get('project_id', project_data['id']), 
              cp_data.get('feature', ''),
              cp_data.get('sub_feature', ''),
              cp_data.get('cover_point', ''),
              cp_data.get('cover_point_details', ''),
              cp_data.get('comments', ''),
              cp_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
    
    # 恢复 Test Cases
    for tc_data in project_data.get('test_cases', []):
        cursor.execute('''
            INSERT INTO test_case (project_id, dv_milestone, priority, testbench, category, owner, test_name, scenario_details, checker_details, coverage_details, comments, status, completed_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tc_data.get('project_id', project_data['id']),
              tc_data.get('dv_milestone', ''),
              tc_data.get('priority', ''),
              tc_data.get('testbench', ''),
              tc_data.get('category', ''),
              tc_data.get('owner', ''),
              tc_data.get('test_name', ''),
              tc_data.get('scenario_details', ''),
              tc_data.get('checker_details', ''),
              tc_data.get('coverage_details', ''),
              tc_data.get('comments', ''),
              tc_data.get('status', 'OPEN'),
              tc_data.get('completed_date', ''),
              tc_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
    
    conn.commit()
    
    # 添加到项目列表
    project = {
        'id': len(projects) + 1,
        'name': project_name,
        'created_at': project_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'is_archived': False,
        'version': project_data.get('version', 'stable')
    }
    projects.append(project)
    save_projects(projects)
    
    return jsonify({'success': True, 'project': project})

@api.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    # 标记为归档
    project['is_archived'] = True
    save_projects(projects)
    
    # 删除数据库文件
    delete_project_db(project['name'])
    
    return jsonify({'success': True})

# ============ Cover Points ============

@api.route('/api/cp', methods=['GET'])
def get_coverpoints():
    """获取 CP 列表（含覆盖率计算）"""
    project_id = request.args.get('project_id', type=int)
    
    if not project_id:
        return jsonify([])
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify([])
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cover_point ORDER BY id')
    
    cps = []
    for row in cursor.fetchall():
        cp_id = row['id']
        
        # 计算覆盖率：统计关联 TC 中 PASS 的比例
        cursor.execute('''
            SELECT tc.status FROM test_case tc
            INNER JOIN tc_cp_connections tcc ON tc.id = tcc.tc_id
            WHERE tcc.cp_id = ?
        ''', (cp_id,))
        
        connected_tcs = cursor.fetchall()
        total = len(connected_tcs)
        passed = sum(1 for tc in connected_tcs if tc['status'] == 'PASS')
        
        # 计算覆盖率
        coverage = round(passed / total * 100, 1) if total > 0 else 0.0
        
        cps.append({
            'id': row['id'],
            'project_id': row['project_id'],
            'feature': row['feature'],
            'sub_feature': row['sub_feature'],
            'cover_point': row['cover_point'],
            'cover_point_details': row['cover_point_details'],
            'comments': row['comments'],
            'created_at': row['created_at'],
            'coverage': coverage,
            'coverage_detail': f'{passed}/{total}'
        })
    
    return jsonify(cps)

@api.route('/api/cp', methods=['POST'])
def create_coverpoint():
    """创建 CP"""
    data = request.json
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO cover_point (project_id, feature, sub_feature, cover_point, cover_point_details, comments, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id,
          data.get('feature', ''),
          data.get('sub_feature', ''),
          data.get('cover_point', ''),
          data.get('cover_point_details', ''),
          data.get('comments', ''),
          data.get('priority', 'P0'),
          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    
    cp_id = cursor.lastrowid
    return jsonify({
        'success': True,
        'item': {
            'id': cp_id,
            'project_id': project_id,
            'feature': data.get('feature', ''),
            'sub_feature': data.get('sub_feature', ''),
            'cover_point': data.get('cover_point', ''),
            'cover_point_details': data.get('cover_point_details', ''),
            'comments': data.get('comments', ''),
            'priority': data.get('priority', 'P0'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@api.route('/api/cp/<int:cp_id>', methods=['PUT'])
def update_coverpoint(cp_id):
    """更新 CP"""
    data = request.json
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE cover_point SET feature=?, sub_feature=?, cover_point=?, cover_point_details=?, comments=?, priority=?
        WHERE id=?
    ''', (data.get('feature', ''),
          data.get('sub_feature', ''),
          data.get('cover_point', ''),
          data.get('cover_point_details', ''),
          data.get('comments', ''),
          data.get('priority', 'P0'),
          cp_id))
    
    conn.commit()
    
    return jsonify({'success': True})

@api.route('/api/cp/<int:cp_id>', methods=['DELETE'])
def delete_coverpoint(cp_id):
    """删除 CP"""
    project_id = request.args.get('project_id', type=int)
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM cover_point WHERE id=?', (cp_id,))
    cursor.execute('DELETE FROM tc_cp_connections WHERE cp_id=?', (cp_id,))
    
    conn.commit()
    
    return jsonify({'success': True})

# ============ Test Cases ============

@api.route('/api/tc', methods=['GET'])
def get_testcases():
    """获取 TC 列表"""
    project_id = request.args.get('project_id', type=int)
    sort_by = request.args.get('sort_by', 'id')
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    
    if not project_id:
        return jsonify([])
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify([])
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    query = 'SELECT * FROM test_case WHERE 1=1'
    params = []
    
    if status_filter:
        query += ' AND status=?'
        params.append(status_filter)
    
    if search:
        query += ' AND (test_name LIKE ? OR testbench LIKE ? OR owner LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    # 排序
    if sort_by == 'testbench':
        query += ' ORDER BY testbench'
    elif sort_by == 'owner':
        query += ' ORDER BY owner'
    elif sort_by == 'status':
        query += ' ORDER BY status'
    elif sort_by == 'created_at':
        query += ' ORDER BY created_at'
    else:
        query += ' ORDER BY id'
    
    cursor.execute(query, params)
    
    tcs = []
    for row in cursor.fetchall():
        # 获取关联的 CP
        cursor.execute('SELECT cp_id FROM tc_cp_connections WHERE tc_id=?', (row['id'],))
        connected_cps = [r[0] for r in cursor.fetchall()]
        
        tcs.append({
            'id': row['id'],
            'project_id': row['project_id'],
            'dv_milestone': row['dv_milestone'],
            'testbench': row['testbench'],
            'category': row['category'],
            'owner': row['owner'],
            'test_name': row['test_name'],
            'scenario_details': row['scenario_details'],
            'checker_details': row['checker_details'],
            'coverage_details': row['coverage_details'],
            'comments': row['comments'],
            'status': row['status'],
            'created_at': row['created_at'],
            'coded_date': row['coded_date'],
            'fail_date': row['fail_date'],
            'pass_date': row['pass_date'],
            'removed_date': row['removed_date'],
            'target_date': row['target_date'],
            'connected_cps': connected_cps
        })
    
    return jsonify(tcs)

@api.route('/api/tc', methods=['POST'])
def create_testcase():
    """创建 TC"""
    data = request.json
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO test_case (
            project_id, dv_milestone, testbench, category, owner, test_name, 
            scenario_details, checker_details, coverage_details, comments, 
            status, created_at, coded_date, fail_date, pass_date, removed_date, target_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, NULL, NULL, NULL, NULL, ?)
    ''', (project_id,
          data.get('dv_milestone', ''),
          data.get('testbench', ''),
          data.get('category', ''),
          data.get('owner', ''),
          data.get('test_name', ''),
          data.get('scenario_details', ''),
          data.get('checker_details', ''),
          data.get('coverage_details', ''),
          data.get('comments', ''),
          today,
          data.get('target_date', '')))
    
    tc_id = cursor.lastrowid
    
    # 关联 CP
    if data.get('connections'):
        for cp_id in data['connections']:
            try:
                cursor.execute('INSERT INTO tc_cp_connections (tc_id, cp_id) VALUES (?, ?)', (tc_id, cp_id))
            except:
                pass
    
    conn.commit()
    
    return jsonify({
        'success': True,
        'item': {
            'id': tc_id,
            'project_id': project_id,
            'dv_milestone': data.get('dv_milestone', ''),
            'testbench': data.get('testbench', ''),
            'category': data.get('category', ''),
            'owner': data.get('owner', ''),
            'test_name': data.get('test_name', ''),
            'scenario_details': data.get('scenario_details', ''),
            'checker_details': data.get('checker_details', ''),
            'coverage_details': data.get('coverage_details', ''),
            'comments': data.get('comments', ''),
            'status': 'OPEN',
            'created_at': today,
            'coded_date': None,
            'fail_date': None,
            'pass_date': None,
            'removed_date': None,
            'target_date': data.get('target_date', ''),
            'connected_cps': data.get('connections', [])
        }
    })

@api.route('/api/tc/<int:tc_id>', methods=['PUT'])
def update_testcase(tc_id):
    """更新 TC"""
    data = request.json
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE test_case SET 
            dv_milestone=?, 
            testbench=?, 
            category=?, 
            owner=?, 
            test_name=?, 
            scenario_details=?, 
            checker_details=?, 
            coverage_details=?, 
            comments=?,
            target_date=?
        WHERE id=?
    ''', (data.get('dv_milestone', ''),
          data.get('testbench', ''),
          data.get('category', ''),
          data.get('owner', ''),
          data.get('test_name', ''),
          data.get('scenario_details', ''),
          data.get('checker_details', ''),
          data.get('coverage_details', ''),
          data.get('comments', ''),
          data.get('target_date', ''),
          tc_id))
    
    # 更新关联
    if 'connections' in data:
        cursor.execute('DELETE FROM tc_cp_connections WHERE tc_id=?', (tc_id,))
        for cp_id in data['connections']:
            try:
                cursor.execute('INSERT INTO tc_cp_connections (tc_id, cp_id) VALUES (?, ?)', (tc_id, cp_id))
            except:
                pass
    
    conn.commit()
    
    return jsonify({'success': True})

@api.route('/api/tc/<int:tc_id>', methods=['DELETE'])
def delete_testcase(tc_id):
    """删除 TC"""
    project_id = request.args.get('project_id', type=int)
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM test_case WHERE id=?', (tc_id,))
    cursor.execute('DELETE FROM tc_cp_connections WHERE tc_id=?', (tc_id,))
    
    conn.commit()
    
    return jsonify({'success': True})

@api.route('/api/tc/<int:tc_id>/status', methods=['POST'])
def update_status(tc_id):
    """更新状态"""
    data = request.json
    new_status = data.get('status')
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({'error': '需要指定项目'}), 400
    
    valid_statuses = ['OPEN', 'CODED', 'FAIL', 'PASS', 'REMOVED']
    if new_status not in valid_statuses:
        return jsonify({'error': '无效状态'}), 400
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    # 获取当前 TC 信息
    cursor.execute('SELECT status FROM test_case WHERE id=?', (tc_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'TC 不存在'}), 404
    
    old_status = row['status']
    
    # 状态日期映射
    status_dates = {
        'CODED': 'coded_date',
        'FAIL': 'fail_date',
        'PASS': 'pass_date',
        'REMOVED': 'removed_date'
    }
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 清除所有状态日期
    cursor.execute('''
        UPDATE test_case SET 
            coded_date=NULL, 
            fail_date=NULL, 
            pass_date=NULL, 
            removed_date=NULL 
        WHERE id=?
    ''', (tc_id,))
    
    # 设置新状态对应的日期
    if new_status in status_dates:
        date_field = status_dates[new_status]
        cursor.execute(f'UPDATE test_case SET {date_field}=? WHERE id=?', (today, tc_id))
    
    # 如果是 REMOVED，清除 CP 关联
    if new_status == 'REMOVED':
        cursor.execute('DELETE FROM tc_cp_connections WHERE tc_id=?', (tc_id,))
    
    # 更新状态
    cursor.execute('UPDATE test_case SET status=? WHERE id=?', (new_status, tc_id))
    
    conn.commit()
    
    # 检查是否需要确认（从 PASS 改为其他状态）
    need_confirm = (old_status == 'PASS' and new_status != 'PASS')
    
    return jsonify({
        'success': True, 
        'status': new_status,
        'need_confirm': need_confirm
    })

# ============ 统计 ============

@api.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    project_id = request.args.get('project_id', type=int)
    
    if not project_id:
        return jsonify({
            'total_cp': 0, 'total_tc': 0,
            'open_tc': 0, 'coded_tc': 0, 'fail_tc': 0, 'pass_tc': 0,
            'coverage': '0%'
        })
    
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({
            'total_cp': 0, 'total_tc': 0,
            'open_tc': 0, 'coded_tc': 0, 'fail_tc': 0, 'pass_tc': 0,
            'coverage': '0%'
        })
    
    conn = get_db(project['name'])
    cursor = conn.cursor()
    
    # CP 统计
    cursor.execute('SELECT COUNT(*) FROM cover_point')
    total_cp = cursor.fetchone()[0]
    
    # TC 统计（REMOVED 不计入 Total）
    cursor.execute('SELECT COUNT(*) FROM test_case WHERE status != "REMOVED"')
    total_tc = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM test_case WHERE status="OPEN" AND status != "REMOVED"')
    open_tc = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM test_case WHERE status="CODED"')
    coded_tc = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM test_case WHERE status="FAIL"')
    fail_tc = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM test_case WHERE status="PASS"')
    pass_tc = cursor.fetchone()[0]
    
    # Pass Rate 计算: PASS / Total * 100%
    pass_rate = 0
    if total_tc > 0:
        pass_rate = round(pass_tc / total_tc * 100, 1)
    
    # 计算覆盖率（只统计非 REMOVED 的 TC）
    coverage = 0
    if total_cp > 0:
        cursor.execute('SELECT id FROM cover_point')
        cp_ids = [row[0] for row in cursor.fetchall()]
        
        total_progress = 0
        for cp_id in cp_ids:
            cursor.execute('SELECT tc_id FROM tc_cp_connections WHERE cp_id=?', (cp_id,))
            tc_ids = [r[0] for r in cursor.fetchall()]
            
            if tc_ids:
                placeholders = ','.join(['?'] * len(tc_ids))
                cursor.execute(f'SELECT COUNT(*) FROM test_case WHERE id IN ({placeholders}) AND status="PASS"', tc_ids)
                passed = cursor.fetchone()[0]
                total_progress += (passed / len(tc_ids)) * 100
        
        coverage = round(total_progress / total_cp, 1)
    
    return jsonify({
        'total_cp': total_cp,
        'total_tc': total_tc,
        'open_tc': open_tc,
        'coded_tc': coded_tc,
        'fail_tc': fail_tc,
        'pass_tc': pass_tc,
        'pass_rate': f'{pass_rate}%',
        'coverage': f'{coverage}%'
    })

# ============ 静态文件 ============

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@api.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@api.route('/<path:path>')
def static_files(path):
    return send_from_directory(BASE_DIR, path)
