#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化系统基础数据
包括：
1. 管理员账户
2. 默认部门
3. 设备类型
4. 配件类型
5. 审批流程模板
6. 示例数据（可选）
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import (
    User, Department, EquipmentType, SparePartType,
    WorkflowTemplate, WorkflowStep, Equipment, SparePart
)
import json


def init_admin_user():
    """初始化管理员账户（超级管理员不属于任何部门）"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            department='超级管理员',
            department_id=None  # 超级管理员不属于任何部门
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print('✅ 创建管理员账户: admin / admin123 (超级管理员，不属于任何部门)')
    else:
        print('⏭️  管理员账户已存在')
    return admin


def init_departments():
    """初始化默认部门"""
    departments = [
        {'name': '信息部', 'code': 'IT', 'cost_center': 'CC001', 'location': 'A座5楼', 'description': '信息技术部门'},
        {'name': '财务部', 'code': 'FIN', 'cost_center': 'CC002', 'location': 'A座3楼', 'description': '财务管理部门'},
        {'name': '人力行政部', 'code': 'HR', 'cost_center': 'CC003', 'location': 'A座2楼', 'description': '人力资源部门'},
        {'name': '国内销售中心', 'code': 'SALES', 'cost_center': 'CC004', 'location': 'B座1楼', 'description': '销售部门'},
        {'name': '生产办', 'code': 'PROD', 'cost_center': 'CC005', 'location': 'C厂房', 'description': '生产制造部门'},
        {'name': '企管部', 'code': 'ADMIN', 'cost_center': 'CC006', 'location': 'A座4楼', 'description': '企业管理部门'}
    ]
    
    count = 0
    for dept_data in departments:
        dept = Department.query.filter_by(code=dept_data['code']).first()
        if not dept:
            dept = Department(**dept_data)
            db.session.add(dept)
            count += 1
    
    if count > 0:
        print(f'✅ 创建默认部门: {count} 个')
    else:
        print('⏭️  默认部门已存在')


def init_equipment_types():
    """初始化设备类型"""
    types = [
        {'name': '台式电脑', 'description': '台式办公电脑'},
        {'name': '笔记本电脑', 'description': '笔记本办公电脑'},
        {'name': '服务器', 'description': '服务器设备'},
        {'name': '打印机', 'description': '激光/喷墨打印机'},
        {'name': '扫描仪', 'description': '文档扫描设备'},
        {'name': '投影仪', 'description': '会议投影设备'},
        {'name': '显示器', 'description': '显示器设备'},
        {'name': '路由器', 'description': '网络路由器'},
        {'name': '交换机', 'description': '网络交换机'},
        {'name': '防火墙', 'description': '网络安全设备'},
        {'name': 'UPS电源', 'description': '不间断电源'},
        {'name': '网络存储', 'description': 'NAS/SAN存储设备'},
        {'name': '摄像头', 'description': '监控摄像设备'},
        {'name': '会议设备', 'description': '会议系统设备'},
        {'name': '电话设备', 'description': 'IP电话等通讯设备'}
    ]
    
    count = 0
    for type_data in types:
        equipment_type = EquipmentType.query.filter_by(name=type_data['name']).first()
        if not equipment_type:
            equipment_type = EquipmentType(**type_data)
            db.session.add(equipment_type)
            count += 1
    
    if count > 0:
        print(f'✅ 创建设备类型: {count} 个')
    else:
        print('⏭️  设备类型已存在')


def init_spare_part_types():
    """初始化配件类型"""
    types = [
        {'name': '内存条', 'description': '电脑内存条'},
        {'name': '硬盘', 'description': '机械硬盘/固态硬盘'},
        {'name': '电源', 'description': '电源适配器/电源模块'},
        {'name': '主板', 'description': '电脑主板'},
        {'name': 'CPU', 'description': '中央处理器'},
        {'name': '显卡', 'description': '图形处理器'},
        {'name': '散热器', 'description': 'CPU散热器'},
        {'name': '机箱风扇', 'description': '机箱散热风扇'},
        {'name': '网卡', 'description': '有线/无线网卡'},
        {'name': '声卡', 'description': '声卡设备'},
        {'name': '键盘', 'description': '键盘设备'},
        {'name': '鼠标', 'description': '鼠标设备'},
        {'name': '数据线', 'description': '各类数据传输线'},
        {'name': '网线', 'description': '网络连接线'},
        {'name': '电源线', 'description': '电源连接线'},
        {'name': '墨盒/硒鼓', 'description': '打印机耗材'},
        {'name': '打印纸', 'description': '打印用纸'},
        {'name': '投影灯泡', 'description': '投影仪灯泡'},
        {'name': '电池', 'description': 'UPS/设备电池'},
        {'name': '转接头', 'description': '各类转接器'}
    ]
    
    count = 0
    for type_data in types:
        spare_type = SparePartType.query.filter_by(name=type_data['name']).first()
        if not spare_type:
            spare_type = SparePartType(**type_data)
            db.session.add(spare_type)
            count += 1
    
    if count > 0:
        print(f'✅ 创建配件类型: {count} 个')
    else:
        print('⏭️  配件类型已存在')


def init_workflow_templates(admin_id):
    """初始化审批流程模板"""
    workflows = [
        {
            "name": "标准维修流程",
            "order_type": "repair_order",
            "description": "员工申请 → 部门主管审批 → 管理员审批",
            "steps": [
                {
                    "step_name": "部门主管审批",
                    "approver_role": "department_head",
                    "sequence": 1,
                    "timeout_days": 2
                },
                {
                    "step_name": "管理员审批",
                    "approver_role": "admin",
                    "sequence": 2,
                    "timeout_days": 3
                }
            ]
        },
        {
            "name": "标准配件申请流程",
            "order_type": "part_request_order",
            "description": "员工申请 → 部门主管审批 → 管理员审批",
            "steps": [
                {
                    "step_name": "部门主管审批",
                    "approver_role": "department_head",
                    "sequence": 1,
                    "timeout_days": 2
                },
                {
                    "step_name": "管理员审批",
                    "approver_role": "admin",
                    "sequence": 2,
                    "timeout_days": 3
                }
            ]
        },
        {
            "name": "标准设备调拨流程",
            "order_type": "equipment_transfer",
            "description": "申请调拨 → 部门主管审批 → 管理员审批",
            "steps": [
                {
                    "step_name": "部门主管审批",
                    "approver_role": "department_head",
                    "sequence": 1,
                    "timeout_days": 2
                },
                {
                    "step_name": "管理员审批",
                    "approver_role": "admin",
                    "sequence": 2,
                    "timeout_days": 3
                }
            ]
        },
        {
            "name": "标准设备报废流程",
            "order_type": "equipment_scrap",
            "description": "申请报废 → 部门主管审批 → 管理员审批",
            "steps": [
                {
                    "step_name": "部门主管审批",
                    "approver_role": "department_head",
                    "sequence": 1,
                    "timeout_days": 2
                },
                {
                    "step_name": "管理员审批",
                    "approver_role": "admin",
                    "sequence": 2,
                    "timeout_days": 3
                }
            ]
        },
        {
            "name": "标准设备借用流程",
            "order_type": "equipment_loan",
            "description": "申请借用 → 部门主管审批 → 管理员审批",
            "steps": [
                {
                    "step_name": "部门主管审批",
                    "approver_role": "department_head",
                    "sequence": 1,
                    "timeout_days": 2
                },
                {
                    "step_name": "管理员审批",
                    "approver_role": "admin",
                    "sequence": 2,
                    "timeout_days": 3
                }
            ]
        },
        {
            "name": "标准设备申领流程",
            "order_type": "equipment_application",
            "description": "申请设备 → 部门主管审批 → 管理员审批",
            "steps": [
                {
                    "step_name": "部门主管审批",
                    "approver_role": "department_head",
                    "sequence": 1,
                    "timeout_days": 2
                },
                {
                    "step_name": "管理员审批",
                    "approver_role": "admin",
                    "sequence": 2,
                    "timeout_days": 3
                }
            ]
        }
    ]
    
    count = 0
    for wf in workflows:
        existing = WorkflowTemplate.query.filter_by(
            name=wf["name"],
            order_type=wf["order_type"]
        ).first()
        
        if existing:
            continue
        
        tpl = WorkflowTemplate(
            code=f"{wf['order_type']}_default_v1",  # 添加code字段
            name=wf["name"],
            order_type=wf["order_type"],
            version=1,  # 添加version字段
            description=wf["description"],
            is_active=True,
            is_default=True,  # 设置为默认模板
            created_by_id=admin_id
        )
        db.session.add(tpl)
        db.session.flush()
        
        for step in wf["steps"]:
            ws = WorkflowStep(
                template_id=tpl.id,
                sequence=step["sequence"],
                step_name=step["step_name"],
                approver_role=step["approver_role"],
                is_parallel=False,
                required_approvals=1,
                timeout_days=step["timeout_days"],
                conditions=json.dumps({}),
                actions_on_approve=json.dumps({}),
                actions_on_reject=json.dumps({"return_to": "requester"})
            )
            db.session.add(ws)
        
        count += 1
    
    if count > 0:
        print(f'✅ 创建审批流程模板: {count} 个')
    else:
        print('⏭️  审批流程模板已存在')


def init_sample_data():
    """初始化示例数据（可选）"""
    # 创建示例设备
    if Equipment.query.count() == 0:
        equipments = [
            {
                'name': '办公电脑001',
                'type': '台式电脑',
                'brand': '联想',
                'model': 'ThinkCentre M720',
                'serial_number': 'PC2023001',
                'department': 'IT部',
                'status': 'active'
            }
        ]
        
        for equip_data in equipments:
            dept = Department.query.filter_by(name=equip_data['department']).first()
            equip = Equipment(**equip_data)
            if dept:
                equip.department_id = dept.id
            db.session.add(equip)
        
        print(f'✅ 创建示例设备: {len(equipments)} 个')
    
    # 创建示例配件
    if SparePart.query.count() == 0:
        parts = [
            {'name': '内存条 8GB DDR4', 'part_number': 'MEM001', 'price': 280.0, 'stock_quantity': 10, 'department': 'IT部'},
        ]
        
        for part_data in parts:
            part = SparePart(**part_data)
            db.session.add(part)
        
        print(f'✅ 创建示例配件: {len(parts)} 个')


def main(include_sample=False):
    """主函数"""
    app = create_app()
    with app.app_context():
        print('开始初始化系统基础数据...\n')
        
        # 1. 初始化部门（优先）
        init_departments()
        db.session.commit()
        
        # 2. 初始化管理员
        admin = init_admin_user()
        db.session.commit()
        
        # 3. 初始化设备类型
        init_equipment_types()
        db.session.commit()
        
        # 4. 初始化配件类型
        init_spare_part_types()
        db.session.commit()
        
        # 5. 初始化审批流程模板 - 跳过,使用新的审批系统
        print('⏭️  跳过旧的工作流模板初始化(请运行 init_default_approval_workflows.py)')
        # init_workflow_templates(admin.id)
        # db.session.commit()
        
        # 6. 初始化示例数据(可选)
        if include_sample:
            init_sample_data()
            db.session.commit()
        
        print('\n✨ 系统基础数据初始化完成!')
        print('\n默认管理员账号:')
        print('  用户名: admin')
        print('  密码: admin123')
        print('\n下一步:')
        print('  1. 运行 python init_default_approval_workflows.py 初始化审批流程')
        print('  2. 运行 python app.py 启动应用')


if __name__ == '__main__':
    import sys
    include_sample = '--sample' in sys.argv or '-s' in sys.argv
    main(include_sample=include_sample)
