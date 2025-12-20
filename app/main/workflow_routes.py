from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app import db
# 兼容导入：优先从旧的 app.models 导入 WorkflowStep，若不可用则回退到新的 ApprovalStep
try:
    from app.models import WorkflowStep
except Exception:
    try:
        from app.approval_models import ApprovalStep as WorkflowStep
    except Exception:
        WorkflowStep = None

from app.approval_models import WorkflowTemplate, WorkflowNode
from datetime import datetime
import json


@bp.route('/admin/workflow_templates')
@login_required
def workflow_templates():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    templates = WorkflowTemplate.query.order_by(WorkflowTemplate.created_date.desc()).all()
    # 计算每个模板对应已同步的节点数量，便于在 UI 展示同步状态
    templates_info = []
    for t in templates:
        node_count = WorkflowNode.query.filter_by(template_id=t.id).count()
        templates_info.append({'template': t, 'node_count': node_count})
    return render_template('main/workflow_templates.html', title='审批流程模板管理', templates_info=templates_info)


@bp.route('/admin/workflow_templates/<int:template_id>/set_default', methods=['POST'])
@login_required
def set_default_workflow_template(template_id):
    if current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403

    tpl = WorkflowTemplate.query.get_or_404(template_id)
    # 清除其它模板的默认标记
    WorkflowTemplate.query.update({WorkflowTemplate.is_default: False})
    tpl.is_default = True

    # 同步模板步骤到 WorkflowNode（非破坏性：存在则更新，不存在则创建）
    synced = 0
    for s in tpl.steps:
        # 名称包含模板名与步骤名，便于识别来源
        expected_name = f"{tpl.name} - {s.step_name}"
        node = WorkflowNode.query.filter_by(template_id=tpl.id, sequence=s.sequence).first()
        if node:
            # 更新字段以保持同步
            node.name = expected_name
            node.role_required = s.approver_role or node.role_required
            node.is_parallel = bool(s.is_parallel)
            node.required_approvals = int(getattr(s, 'required_approvals', 1) or 1)
            try:
                node.actions_on_reject = s.actions_on_reject
            except Exception:
                pass
        else:
            node = WorkflowNode(
                name=expected_name,
                order_type=tpl.order_type,
                role_required=s.approver_role or 'department_head',
                sequence=s.sequence,
                is_active=True,
                is_parallel=bool(s.is_parallel),
                required_approvals=int(getattr(s, 'required_approvals', 1) or 1),
                actions_on_reject=(s.actions_on_reject if getattr(s, 'actions_on_reject', None) else None)
            )
            db.session.add(node)
        synced += 1

    db.session.commit()
    return jsonify({'success': True, 'message': f'已将 "{tpl.name}" 设置为默认流程并同步 {synced} 个节点', 'synced': synced})


@bp.route('/admin/workflow_templates/create', methods=['GET', 'POST'])
@login_required
def create_workflow_template():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        order_type = request.form.get('order_type', '').strip()
        description = request.form.get('description', '').strip()
        steps_json = request.form.get('steps', '[]')
        is_default = request.form.get('is_default') == 'on'
        
        if not name or not order_type:
            flash('名称和订单类型为必填项', 'warning')
            return render_template('main/workflow_template_form.html', template=None)

        try:
            steps = json.loads(steps_json)
        except Exception:
            flash('步骤格式必须为 JSON 数组', 'danger')
            return render_template('main/workflow_template_form.html', template=None)

        tpl = WorkflowTemplate(name=name, order_type=order_type, description=description, created_by_id=current_user.id, is_default=is_default)
        db.session.add(tpl)
        db.session.flush()

        seq = 1
        if WorkflowStep is None:
            flash('当前环境不支持旧版 WorkflowStep 模型，请检查审批模型模块是否加载。', 'danger')
            return render_template('main/workflow_template_form.html', template=None)

        for s in steps:
            step = WorkflowStep(template_id=tpl.id,
                                sequence=seq,
                                step_name=s.get('step_name') or f'步骤 {seq}',
                                approver_role=s.get('approver_role'),
                                approver_dept=s.get('approver_dept'),
                                is_parallel=bool(s.get('is_parallel', False)),
                                timeout_days=int(s.get('timeout_days') or 0),
                                conditions=json.dumps(s.get('conditions') or {}),
                                actions_on_approve=json.dumps(s.get('actions_on_approve') or {}),
                                actions_on_reject=json.dumps(s.get('actions_on_reject') or {}))
            db.session.add(step)
            seq += 1

        db.session.commit()
        flash('审批流程模板已创建', 'success')
        return redirect(url_for('main.workflow_templates'))

    return render_template('main/workflow_template_form.html', template=None)


@bp.route('/admin/workflow_templates/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workflow_template(template_id):
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    tpl = WorkflowTemplate.query.get_or_404(template_id)
    if request.method == 'POST':
        try:
            tpl.name = request.form.get('name', tpl.name)
            tpl.order_type = request.form.get('order_type', tpl.order_type)
            tpl.description = request.form.get('description', tpl.description)
            tpl.is_default = request.form.get('is_default') == 'on'
            tpl.updated_date = datetime.now()
            
            # 获取节点数据（前端通过 steps JSON 发送）
            steps_json = request.form.get('steps', '[]')
            try:
                steps = json.loads(steps_json)
            except Exception as e:
                return jsonify({'success': False, 'message': f'步骤格式错误: {str(e)}'}), 400

            # 删除旧节点，重新写入
            WorkflowNode.query.filter_by(template_id=tpl.id).delete()
            
            seq = 1
            for s in steps:
                node = WorkflowNode(
                    template_id=tpl.id,
                    name=s.get('node_name') or s.get('name') or f'节点{seq}',
                    order_type=tpl.order_type,
                    role_required=s.get('role_required'),
                    approval_role_id=s.get('approval_role_id'),
                    sequence=seq,
                    is_active=s.get('is_active', True)
                )
                db.session.add(node)
                seq += 1
            
            db.session.commit()
            flash('审批流程模板已更新', 'success')
            return redirect(url_for('main.workflow_templates'))
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 400

    # 提供 steps 作为 JSON 字符串供前端编辑
    steps = []
    nodes = WorkflowNode.query.filter_by(template_id=template_id).order_by(WorkflowNode.sequence).all()
    for node in nodes:
        steps.append({
            'node_name': node.name,
            'role_required': node.role_required,
            'sequence': node.sequence,
            'approval_role_id': node.approval_role_id,
            'is_active': node.is_active,
        })

    return render_template('main/workflow_template_form.html', template=tpl, steps_json=json.dumps(steps, ensure_ascii=False))


@bp.route('/admin/workflow_templates/<int:template_id>/delete', methods=['POST'])
@login_required
def delete_workflow_template(template_id):
    if current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    tpl = WorkflowTemplate.query.get_or_404(template_id)
    db.session.delete(tpl)
    db.session.commit()
    flash('审批流程模板已删除', 'success')
    return redirect(url_for('main.workflow_templates'))
