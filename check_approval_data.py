#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('/app/app.db')
cursor = conn.cursor()

print("=" * 60)
print("系统用户信息")
print("=" * 60)
cursor.execute("SELECT id, username, role, department FROM user WHERE role IN ('technician', 'department_head', 'admin')")
users = cursor.fetchall()
for u in users:
    dept = u[3] if u[3] else '无'
    print(f"  ID:{u[0]}, 姓名:{u[1]}, 角色:{u[2]}, 部门:{dept}")

print("\n" + "=" * 60)
print("维修单 #1 信息")
print("=" * 60)
cursor.execute("SELECT id, description, requester_id, status FROM repair_order WHERE id=1")
order = cursor.fetchone()
if order:
    print(f"  ID: {order[0]}")
    print(f"  描述: {order[1][:50] if order[1] else '无'}")
    print(f"  申请人ID: {order[2]}")
    print(f"  状态: {order[3]}")
    
    cursor.execute("SELECT username, role, department FROM user WHERE id=?", (order[2],))
    req = cursor.fetchone()
    if req:
        print(f"  申请人: {req[0]}")
        print(f"  申请人角色: {req[1]}")
        print(f"  申请人部门: {req[2]}")

print("\n" + "=" * 60)
print("审批工作流记录")
print("=" * 60)
cursor.execute("""
    SELECT aw.id, aw.order_type, aw.order_id, aw.approver_id, aw.approval_level, aw.status, u.username, u.role, u.department
    FROM approval_workflow aw
    LEFT JOIN user u ON aw.approver_id = u.id
    WHERE aw.order_type = 'repair_order' AND aw.order_id = 1
    ORDER BY aw.id
""")
approvals = cursor.fetchall()
for a in approvals:
    dept = a[8] if a[8] else '无'
    print(f"  审批ID:{a[0]}, 级别:{a[4]}, 状态:{a[5]}")
    print(f"    审批人ID:{a[3]}, 姓名:{a[6]}, 角色:{a[7]}, 部门:{dept}")

print("\n" + "=" * 60)
print("工作流节点配置")
print("=" * 60)
cursor.execute("""
    SELECT id, name, order_type, sequence, role_required, node_type 
    FROM workflow_node 
    ORDER BY order_type, sequence
""")
nodes = cursor.fetchall()
for n in nodes:
    role = n[4] if n[4] else '无'
    print(f"  ID:{n[0]}, 类型:{n[2]}, 顺序:{n[3]}, 名称:{n[1]}, 节点:{n[5]}, 角色:{role}")

conn.close()
