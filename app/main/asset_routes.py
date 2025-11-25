"""
统一资产/配件管理中心路由
整合：申请、调拨、借用、归还、报废等功能
"""
from flask import render_template, request, jsonify, flash, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from app.main import bp
from app import db
from app.models import (
    Equipment, SparePart, EquipmentTransfer, EquipmentScrap,
    EquipmentLoan, PartRequestOrder
)
from app.utils.qrcode_generator import (
    generate_asset_label, image_to_base64, image_to_bytes
)


def _log_activity(action, description):
    """记录用户活动日志"""
    try:
        from app.models import UserActivityLog
        from flask import request
        ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr or ''
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action=action,
            description=f"{description} (IP: {ip})"
        )
        db.session.add(activity_log)
        try:
            db.session.commit()
        except Exception:
            pass
    except Exception:
        pass


@bp.route('/asset_center')
@login_required
def asset_center():
    """
    统一的资产/配件管理中心
    整合：申请、调拨、借用、归还、报废等功能
    """
    # 获取统计数据
    equipment_count = Equipment.query.count()
    spare_parts_count = SparePart.query.count()
    
    # 获取待处理事项
    pending_transfers = EquipmentTransfer.query.filter_by(status='submitted').count()
    pending_scraps = EquipmentScrap.query.filter_by(status='submitted').count()
    pending_loans = EquipmentLoan.query.filter_by(status='submitted').count()
    pending_part_requests = PartRequestOrder.query.filter_by(status='submitted').count()
    
    # 根据用户角色过滤
    if current_user.role != 'admin':
        pending_transfers = EquipmentTransfer.query.filter_by(
            status='submitted',
            requester_id=current_user.id
        ).count()
        pending_scraps = EquipmentScrap.query.filter_by(
            status='submitted',
            requester_id=current_user.id
        ).count()
        pending_loans = EquipmentLoan.query.filter_by(
            status='submitted',
            requester_id=current_user.id
        ).count()
        pending_part_requests = PartRequestOrder.query.filter_by(
            status='submitted',
            requester_id=current_user.id
        ).count()
    
    _log_activity('访问页面', '资产/配件管理中心')
    return render_template(
        'main/asset_center.html',
        title='资产/配件管理中心',
        equipment_count=equipment_count,
        spare_parts_count=spare_parts_count,
        pending_transfers=pending_transfers,
        pending_scraps=pending_scraps,
        pending_loans=pending_loans,
        pending_part_requests=pending_part_requests
    )


@bp.route('/asset/generate_qrcode/<asset_type>/<int:asset_id>')
@login_required
def generate_asset_qrcode(asset_type, asset_id):
    """
    生成资产二维码（用于在线预览）
    
    Args:
        asset_type: 'equipment' 或 'spare_part'
        asset_id: 资产ID
    """
    try:
        if asset_type == 'equipment':
            asset = Equipment.query.get_or_404(asset_id)
            asset_name = asset.name
            asset_code = asset.serial_number or f"EQ{asset_id:06d}"
            department = asset.department
        elif asset_type == 'spare_part':
            asset = SparePart.query.get_or_404(asset_id)
            asset_name = asset.name
            asset_code = asset.part_number or f"SP{asset_id:06d}"
            department = asset.department
        else:
            return jsonify({'success': False, 'message': '无效的资产类型'}), 400
        
        # 生成标签
        label_img = generate_asset_label(
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_code=asset_code,
            department=department
        )
        
        # 转换为base64用于在线预览
        img_base64 = image_to_base64(label_img)
        
        _log_activity('生成二维码', f'{asset_type}#{asset_id}')
        return jsonify({
            'success': True,
            'image': img_base64,
            'asset_name': asset_name,
            'asset_code': asset_code
        })
    except Exception as e:
        current_app.logger.error(f'生成二维码失败: {str(e)}')
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'}), 500


@bp.route('/asset/download_label/<asset_type>/<int:asset_id>')
@login_required
def download_asset_label(asset_type, asset_id):
    """
    下载资产标签（70*70mm，PNG格式）
    
    Args:
        asset_type: 'equipment' 或 'spare_part'
        asset_id: 资产ID
    """
    try:
        if asset_type == 'equipment':
            asset = Equipment.query.get_or_404(asset_id)
            asset_name = asset.name
            asset_code = asset.serial_number or f"EQ{asset_id:06d}"
            department = asset.department
            filename = f"设备标签_{asset_code}.png"
        elif asset_type == 'spare_part':
            asset = SparePart.query.get_or_404(asset_id)
            asset_name = asset.name
            asset_code = asset.part_number or f"SP{asset_id:06d}"
            department = asset.department
            filename = f"配件标签_{asset_code}.png"
        else:
            flash('无效的资产类型')
            return redirect(url_for('main.asset_center'))
        
        # 生成标签
        label_img = generate_asset_label(
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_code=asset_code,
            department=department
        )
        
        # 转换为字节流
        img_bytes = image_to_bytes(label_img, format='PNG')
        
        _log_activity('下载标签', f'{asset_type}#{asset_id}')
        return Response(
            img_bytes.getvalue(),
            mimetype='image/png',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        current_app.logger.error(f'下载标签失败: {str(e)}')
        flash(f'下载失败: {str(e)}')
        return redirect(url_for('main.asset_center'))


@bp.route('/asset/batch_generate_labels', methods=['POST'])
@login_required
def batch_generate_labels():
    """
    批量生成标签（用于批量打印）
    
    接收JSON数据：
    {
        "assets": [
            {"type": "equipment", "id": 1},
            {"type": "spare_part", "id": 2}
        ]
    }
    """
    try:
        if current_user.role != 'admin':
            return jsonify({'success': False, 'message': '权限不足'}), 403
        
        data = request.get_json()
        if not data or 'assets' not in data:
            return jsonify({'success': False, 'message': '无效的请求数据'}), 400
        
        assets = data.get('assets', [])
        if len(assets) > 50:  # 限制批量数量
            return jsonify({'success': False, 'message': '批量数量不能超过50个'}), 400
        
        labels = []
        for asset_info in assets:
            asset_type = asset_info.get('type')
            asset_id = asset_info.get('id')
            
            if asset_type == 'equipment':
                asset = Equipment.query.get(asset_id)
                if asset:
                    asset_name = asset.name
                    asset_code = asset.serial_number or f"EQ{asset_id:06d}"
                    department = asset.department
                else:
                    continue
            elif asset_type == 'spare_part':
                asset = SparePart.query.get(asset_id)
                if asset:
                    asset_name = asset.name
                    asset_code = asset.part_number or f"SP{asset_id:06d}"
                    department = asset.department
                else:
                    continue
            else:
                continue
            
            # 生成标签
            label_img = generate_asset_label(
                asset_type=asset_type,
                asset_id=asset_id,
                asset_name=asset_name,
                asset_code=asset_code,
                department=department
            )
            
            labels.append({
                'type': asset_type,
                'id': asset_id,
                'name': asset_name,
                'code': asset_code,
                'image': image_to_base64(label_img)
            })
        
        _log_activity('批量生成标签', f'{len(labels)}个资产')
        return jsonify({
            'success': True,
            'count': len(labels),
            'labels': labels
        })
    except Exception as e:
        current_app.logger.error(f'批量生成标签失败: {str(e)}')
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'}), 500

