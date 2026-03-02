"""
Tracker 数据库模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    """项目表"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    is_archived = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20), default='stable')  # 'stable' 或 'test'
    
    # v0.8.0 新增：项目起止日期
    start_date = db.Column(db.String(10))  # YYYY-MM-DD
    end_date = db.Column(db.String(10))    # YYYY-MM-DD
    
    # 关系
    cover_points = db.relationship('CoverPoint', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'is_archived': self.is_archived,
            'version': self.version,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'cp_count': self.cover_points.count(),
            'tc_count': self.test_cases.count()
        }

class CoverPoint(db.Model):
    """Cover Points 表"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # 字段
    feature = db.Column(db.String(200), nullable=False)          # Feature
    sub_feature = db.Column(db.String(200))                      # Sub-Feature
    cover_point = db.Column(db.String(500), nullable=False)      # Cover Point（首要）
    cover_point_details = db.Column(db.Text)                     # Cover Point Details
    comments = db.Column(db.Text)                                # Comments
    priority = db.Column(db.String(3), default='P0')            # Priority (P0/P1/P2)
    
    created_at = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # 关系
    connected_tcs = db.relationship('TestCase', 
                                     secondary='tc_cp_connections',
                                     back_populates='connected_cps')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'feature': self.feature,
            'sub_feature': self.sub_feature,
            'cover_point': self.cover_point,
            'cover_point_details': self.cover_point_details,
            'comments': self.comments,
            'priority': self.priority,
            'created_at': self.created_at
        }

class TestCase(db.Model):
    """Test Cases 表"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # 字段
    dv_milestone = db.Column(db.String(10))                        # DV Milestone (DV0.3/DV0.5/DV0.7/DV1.0)
    priority = db.Column(db.String(20))                            # Priority (已废弃，保留兼容性)
    testbench = db.Column(db.String(200), nullable=False)          # TestBench
    category = db.Column(db.String(100))                           # Category
    owner = db.Column(db.String(100))                             # Owner
    test_name = db.Column(db.String(500), nullable=False)         # Test Name（首要）
    scenario_details = db.Column(db.Text)                          # Scenario Details
    checker_details = db.Column(db.Text)                           # Checker Details（可隐藏）
    coverage_details = db.Column(db.Text)                         # Coverage Details（可隐藏）
    comments = db.Column(db.Text)                                 # Comments（可隐藏）
    
    # 系统字段
    status = db.Column(db.String(20), default='OPEN')             # OPEN/CODED/FAIL/PASS/REMOVED
    created_at = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # 日期字段
    coded_date = db.Column(db.String(20))                         # 状态变为 CODED 的日期
    fail_date = db.Column(db.String(20))                          # 状态变为 FAIL 的日期
    pass_date = db.Column(db.String(20))                          # 状态变为 PASS 的日期
    removed_date = db.Column(db.String(20))                       # 状态变为 REMOVED 的日期
    target_date = db.Column(db.String(20))                        # 目标完成日期
    
    # 关系
    connected_cps = db.relationship('CoverPoint',
                                    secondary='tc_cp_connections',
                                    back_populates='connected_tcs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'dv_milestone': self.dv_milestone,
            'testbench': self.testbench,
            'category': self.category,
            'owner': self.owner,
            'test_name': self.test_name,
            'scenario_details': self.scenario_details,
            'checker_details': self.checker_details,
            'coverage_details': self.coverage_details,
            'comments': self.comments,
            'status': self.status,
            'created_at': self.created_at,
            'coded_date': self.coded_date,
            'fail_date': self.fail_date,
            'pass_date': self.pass_date,
            'removed_date': self.removed_date,
            'target_date': self.target_date,
            'connected_cps': [cp.id for cp in self.connected_cps]
        }

# 关联表
tc_cp_connections = db.Table('tc_cp_connections',
    db.Column('tc_id', db.Integer, db.ForeignKey('test_case.id'), primary_key=True),
    db.Column('cp_id', db.Integer, db.ForeignKey('cover_point.id'), primary_key=True)
)

class Archive(db.Model):
    """备份归档表"""
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    backup_date = db.Column(db.String(20), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON 格式


# v0.8.2: 项目进度快照表
class ProjectProgress(db.Model):
    """项目进度快照表"""
    __tablename__ = 'project_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    snapshot_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    
    # 覆盖率数据
    actual_coverage = db.Column(db.Float)  # 实际覆盖率 (0-100)
    tc_pass_count = db.Column(db.Integer)  # Pass 状态 TC 数
    tc_total = db.Column(db.Integer)       # 总 TC 数
    cp_covered = db.Column(db.Integer)     # 已覆盖 CP 数
    cp_total = db.Column(db.Integer)       # 总 CP 数
    
    # 时间戳
    created_at = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = db.Column(db.String(20))  # 更新时间
    updated_by = db.Column(db.String(100)) # 更新人
    
    # 关系
    project = db.relationship('Project', backref='progress_snapshots')
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('project_id', 'snapshot_date', name='uq_project_progress_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'snapshot_date': self.snapshot_date,
            'actual_coverage': self.actual_coverage,
            'tc_pass_count': self.tc_pass_count,
            'tc_total': self.tc_total,
            'cp_covered': self.cp_covered,
            'cp_total': self.cp_total,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'updated_by': self.updated_by
        }
    version = db.Column(db.String(20))          # 备份时的版本
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'backup_date': self.backup_date,
            'version': self.version
        }
