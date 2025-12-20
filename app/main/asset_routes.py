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
    generate_asset_label, generate_qrcode, image_to_base64, image_to_bytes
)
from app.utils.import_export import content_disposition
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import base64


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
            asset = Equipment.query.get(asset_id)
            if not asset:
                return jsonify({'success': False, 'message': f'设备ID {asset_id} 不存在'}), 404
            asset_name = asset.name
            asset_code = asset.serial_number or f"EQ{asset_id:06d}"
            department = asset.department
            purchase_date = asset.purchase_date
            location = getattr(asset, 'location', None)
        elif asset_type == 'spare_part':
            asset = SparePart.query.get(asset_id)
            if not asset:
                return jsonify({'success': False, 'message': f'配件ID {asset_id} 不存在'}), 404
            asset_name = asset.name
            asset_code = asset.part_number or f"SP{asset_id:06d}"
            department = getattr(asset, 'department', None)
            purchase_date = asset.purchase_date if hasattr(asset, 'purchase_date') else None
            location = getattr(asset, 'location', None)
        else:
            return jsonify({'success': False, 'message': '无效的资产类型'}), 400
        
        # 生成标签 (使用较低DPI以便在屏幕上预览)
        label_img = generate_asset_label(
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_code=asset_code,
            department=department,
            purchase_date=purchase_date,
            location=location,
            dpi=150  # 降低DPI使文字在屏幕预览时更清晰
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
    下载资产标签（PDF格式，70*70mm）
    
    Args:
        asset_type: 'equipment' 或 'spare_part'
        asset_id: 资产ID
    """
    try:
        if asset_type == 'equipment':
            asset = Equipment.query.get(asset_id)
            if not asset:
                flash(f'设备ID {asset_id} 不存在', 'error')
                return redirect(url_for('main.asset_center'))
            asset_name = asset.name
            asset_code = asset.serial_number or f"EQ{asset_id:06d}"
            department = asset.department
            purchase_date = asset.purchase_date
            location = getattr(asset, 'location', None)
            pdf_filename = f'设备标签_{asset_code}.pdf'
        elif asset_type == 'spare_part':
            asset = SparePart.query.get(asset_id)
            if not asset:
                flash(f'配件ID {asset_id} 不存在', 'error')
                return redirect(url_for('main.asset_center'))
            asset_name = asset.name
            asset_code = asset.part_number or f"SP{asset_id:06d}"
            department = getattr(asset, 'department', None)
            purchase_date = asset.purchase_date if hasattr(asset, 'purchase_date') else None
            location = getattr(asset, 'location', None)
            pdf_filename = f'配件标签_{asset_code}.pdf'
        else:
            flash('无效的资产类型', 'error')
            return redirect(url_for('main.asset_center'))
        
        # 生成标签图像（PNG）
        label_img = generate_asset_label(
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_code=asset_code,
            department=department,
            purchase_date=purchase_date,
            location=location
        )
        
        # 获取PNG图像字节
        img_bytes = image_to_bytes(label_img, format='PNG')
        img_bytes.seek(0)
        
        # 创建PDF，嵌入PNG图像（70mm x 70mm 标签）
        import tempfile
        pdf_buffer = BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(70*mm, 70*mm))
        
        # reportlab的drawImage需要文件路径，所以用临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(img_bytes.getvalue())
            tmp_path = tmp.name
        
        try:
            # 在PDF上绘制PNG图像
            pdf_canvas.drawImage(
                tmp_path,
                x=0,
                y=0,
                width=70*mm,
                height=70*mm
            )
            pdf_canvas.save()
        finally:
            # 清理临时文件
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        pdf_buffer.seek(0)
        
        _log_activity('下载标签', f'{asset_type}#{asset_id}')
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': content_disposition(pdf_filename, 'label.pdf')
            }
        )
    except Exception as e:
        current_app.logger.error(f'下载标签失败: {str(e)}')
        flash(f'下载失败: {str(e)}')
        return redirect(url_for('main.asset_center'))


@bp.route('/asset/print_label/<asset_type>/<int:asset_id>')
@login_required
def print_asset_label(asset_type, asset_id):
    """
    在线打印资产标签（HTML页面）
    
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
            purchase_date = asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else "未录入"
            location = getattr(asset, 'location', None) or "未指定"
            label_title = "设备标签"
        elif asset_type == 'spare_part':
            asset = SparePart.query.get_or_404(asset_id)
            asset_name = asset.name
            asset_code = asset.part_number or f"SP{asset_id:06d}"
            department = getattr(asset, 'department', None) or "未分配"
            purchase_date = asset.purchase_date.strftime('%Y-%m-%d') if hasattr(asset, 'purchase_date') and asset.purchase_date else "未录入"
            location = getattr(asset, 'location', None) or "未指定"
            label_title = "配件标签"
        else:
            flash('无效的资产类型', 'error')
            return redirect(url_for('main.asset_center'))
        
        # 生成完整标签图片（而不是单独的二维码）
        label_img = generate_asset_label(
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_code=asset_code,
            department=department,
            purchase_date=purchase_date,
            location=location
        )
        label_base64 = image_to_base64(label_img, format='PNG')
        
        _log_activity('打印标签', f'{asset_type}#{asset_id}')
        return render_template('main/print_label.html',
            label_title=label_title,
            asset_name=asset_name,
            asset_code=asset_code,
            department=department,
            purchase_date=purchase_date,
            location=location,
            asset_type=asset_type,
            asset_id=asset_id,
            label_base64=label_base64  # 传递完整标签图片
        )
        
    except Exception as e:
        current_app.logger.error(f'生成打印页面失败: {str(e)}')
        flash(f'生成打印页面失败: {str(e)}')
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

