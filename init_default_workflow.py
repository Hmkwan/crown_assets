#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化默认的祥光流程（维修、配件、调拨、报废、借用、申请）
这个脚本会为系统创建标准的多级审批流程模板。
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.models import WorkflowStep, User
import json
from datetime import datetime

def create_default_workflows():
    """创建默认的审批流程模板"""
    app = create_app()
    with app.app_context():
        # 获取管理员用户（如果不存在则使用ID=1）
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("⚠️ 未找到管理员用户，使用 User ID 1")
            admin_id = 1
        else:
            admin_id = admin.id
            print(f"✅ 使用管理员用户: {admin.username}")

        workflows = [
            {
                "name": "标准维修流程",
                "order_type": "repair_order",
                "description": "员工申请维修 → 部门主管审批 → 技术部审批 → 完成",
                "steps": [
                    {
                        "step_name": "员工申请维修",
                        "approver_role": "user",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {}
                    },
                    {
                        "step_name": "部门主管审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "技术部审批",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 3,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    }
                ]
            },
            {
                "name": "标准配件申请流程",
                "order_type": "part_request_order",
                "description": "员工申请配件 → 部门主管审批 → 采购部审批 → 完成",
                "steps": [
                    {
                        "step_name": "员工申请配件",
                        "approver_role": "user",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {}
                    },
                    {
                        "step_name": "部门主管审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "采购部审批",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 5,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    }
                ]
            },
            {
                "name": "设备调拨流程",
                "order_type": "equipment_transfer",
                "description": "部门申请调拨 → 当前部门主管审批 → 目标部门主管审批 → 管理员确认 → 完成",
                "steps": [
                    {
                        "step_name": "调拨申请",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {}
                    },
                    {
                        "step_name": "当前部门审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "目标部门审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "管理员确认",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    }
                ]
            },
            {
                "name": "设备报废流程",
                "order_type": "equipment_scrap",
                "description": "部门申请报废 → 部门主管审批 → 管理员财务审批 → 完成",
                "steps": [
                    {
                        "step_name": "报废申请",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {}
                    },
                    {
                        "step_name": "部门主管审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "财务审批",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 3,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    }
                ]
            },
            {
                "name": "设备借用流程",
                "order_type": "equipment_loan",
                "description": "员工借用申请 → 部门主管审批 → 资产管理部审批 → 完成",
                "steps": [
                    {
                        "step_name": "借用申请",
                        "approver_role": "user",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {}
                    },
                    {
                        "step_name": "部门主管审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "资产管理部审批",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    }
                ]
            },
            {
                "name": "设备申请流程",
                "order_type": "equipment_application",
                "description": "员工申请设备 → 部门主管审批 → 采购审批 → 财务审批 → 完成",
                "steps": [
                    {
                        "step_name": "设备申请",
                        "approver_role": "user",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 1,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {}
                    },
                    {
                        "step_name": "部门主管审批",
                        "approver_role": "department_head",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 2,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "采购部审批",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 3,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    },
                    {
                        "step_name": "财务部审批",
                        "approver_role": "admin",
                        "approver_dept": None,
                        "is_parallel": False,
                        "required_approvals": 1,
                        "timeout_days": 3,
                        "conditions": {},
                        "actions_on_approve": {},
                        "actions_on_reject": {"return_to": "requester"}
                    }
                ]
            }
        ]

        for wf in workflows:
            # 检查是否已存在
            existing = WorkflowTemplate.query.filter_by(
                name=wf["name"],
                order_type=wf["order_type"]
            ).first()
            
            if existing:
                print(f"⏭️  流程已存在: {wf['name']} ({wf['order_type']})")
                continue
            
            # 创建新流程模板
            tpl = WorkflowTemplate(
                name=wf["name"],
                order_type=wf["order_type"],
                description=wf["description"],
                is_active=True,
                created_by_id=admin_id
            )
            db.session.add(tpl)
            db.session.flush()
            
            # 创建步骤
            for seq, step in enumerate(wf["steps"], 1):
                ws = WorkflowStep(
                    template_id=tpl.id,
                    sequence=seq,
                    step_name=step["step_name"],
                    approver_role=step["approver_role"],
                    approver_dept=step["approver_dept"],
                    is_parallel=step.get("is_parallel", False),
                    required_approvals=step.get("required_approvals", 1),
                    timeout_days=step.get("timeout_days", 5),
                    conditions=json.dumps(step.get("conditions", {})),
                    actions_on_approve=json.dumps(step.get("actions_on_approve", {})),
                    actions_on_reject=json.dumps(step.get("actions_on_reject", {}))
                )
                db.session.add(ws)
            
            print(f"✅ 已创建流程: {wf['name']} ({wf['order_type']}) - {len(wf['steps'])} 个步骤")
        
        db.session.commit()
        print("\n✨ 默认流程初始化完成！")

if __name__ == '__main__':
    create_default_workflows()
