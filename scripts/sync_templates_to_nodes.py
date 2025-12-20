"""
将激活的 WorkflowTemplate 同步为 WorkflowNode（使系统默认使用这些节点）
此脚本会：
- 遍历所有 is_active 的 WorkflowTemplate
- 对于每个步骤，若对应 order_type 和 sequence 的 WorkflowNode 不存在则创建
"""
from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode

app = create_app()
with app.app_context():
    templates = WorkflowTemplate.query.filter_by(is_active=True).all()
    if not templates:
        print('未找到激活的 WorkflowTemplate，跳过。')
    for tpl in templates:
        print(f'同步模板: {tpl.name} ({tpl.order_type})')
        for s in tpl.steps:
            # 如果已有相同 order_type 和 sequence 的节点，跳过
            existing = WorkflowNode.query.filter_by(order_type=tpl.order_type, sequence=s.sequence).first()
            if existing:
                print(f'  跳过已存在节点 sequence={s.sequence}, name={existing.name}')
                continue
            node_name = f"{tpl.name} - {s.step_name}"
            wn = WorkflowNode(
                name=node_name,
                order_type=tpl.order_type,
                role_required=s.approver_role or 'department_head',
                sequence=s.sequence,
                is_active=True,
                is_parallel=bool(s.is_parallel),
                required_approvals=int(getattr(s, 'required_approvals', 1) or 1),
                actions_on_reject=(s.actions_on_reject if getattr(s, 'actions_on_reject', None) else None)
            )
            db.session.add(wn)
            print(f'  创建节点: {node_name} (role={wn.role_required}, parallel={wn.is_parallel}, req={wn.required_approvals})')
    db.session.commit()
    print('同步完成。')
