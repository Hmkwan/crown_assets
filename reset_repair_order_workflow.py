#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试维修单审批流程
"""
import sqlite3

conn = sqlite3.connect('/app/app.db')
cursor = conn.cursor()

print("=" * 60)
print("清理维修单 #1 的审批记录")
print("=" * 60)

# 删除维修单 #1 的所有审批记录
cursor.execute("DELETE FROM approval_workflow WHERE order_type='repair_order' AND order_id=1")
print(f"删除了 {cursor.rowcount} 条审批记录")

# 重置维修单状态
cursor.execute("UPDATE repair_order SET status='submitted', department_head_approved=0, admin_approved=0 WHERE id=1")
print("重置维修单状态为 'submitted'")

conn.commit()

print("\n" + "=" * 60)
print("获取第一个审批节点")
print("=" * 60)

cursor.execute("""
    SELECT id, name, sequence, role_required 
    FROM workflow_node 
    WHERE order_type='repair_order' AND is_active=1 
    ORDER BY sequence 
    LIMIT 1
""")
first_node = cursor.fetchone()
if first_node:
    print(f"第一个节点: ID:{first_node[0]}, 名称:{first_node[1]}, 顺序:{first_node[2]}, 角色:{first_node[3]}")
    
    # 获取申请人信息
    cursor.execute("SELECT requester_id FROM repair_order WHERE id=1")
    requester_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT username, department FROM user WHERE id=?", (requester_id,))
    requester = cursor.fetchone()
    print(f"申请人: {requester[0]}, 部门: {requester[1]}")
    
    # 查找该部门的部门负责人
    cursor.execute("SELECT id, username FROM user WHERE role='department_head' AND department=?", (requester[1],))
    approver = cursor.fetchone()
    if approver:
        print(f"找到审批人: ID:{approver[0]}, 姓名:{approver[1]}")
        
        # 创建第一个审批记录
        from datetime import datetime
        cursor.execute("""
            INSERT INTO approval_workflow 
            (order_type, order_id, approver_id, approval_level, node_id, status, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('repair_order', 1, approver[0], first_node[3], first_node[0], 'pending', datetime.now()))
        print(f"创建审批记录成功 (node_id={first_node[0]})")
        conn.commit()
    else:
        print("错误: 未找到部门负责人!")
else:
    print("错误: 未找到工作流节点!")

print("\n" + "=" * 60)
print("当前维修单状态")
print("=" * 60)

cursor.execute("SELECT id, description, status FROM repair_order WHERE id=1")
order = cursor.fetchone()
print(f"维修单 #{order[0]}: {order[1]}, 状态: {order[2]}")

cursor.execute("""
    SELECT aw.id, aw.approval_level, aw.node_id, aw.status, u.username
    FROM approval_workflow aw
    LEFT JOIN user u ON aw.approver_id = u.id
    WHERE aw.order_type='repair_order' AND aw.order_id=1
    ORDER BY aw.id
""")
approvals = cursor.fetchall()
print(f"\n审批记录 ({len(approvals)} 条):")
for a in approvals:
    print(f"  审批ID:{a[0]}, 级别:{a[1]}, node_id:{a[2]}, 状态:{a[3]}, 审批人:{a[4]}")

conn.close()
print("\n✓ 重置完成! 现在可以用部门负责人账号登录测试审批了")
