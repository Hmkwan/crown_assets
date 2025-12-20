from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    # 获取admin用户
    admin = User.query.filter_by(username='admin').first()
    print(f"管理员账号: {admin.username}")
    print(f"角色: {admin.role}")
    
    # 模拟登录并获取首页tiles
    with app.test_request_context():
        from flask_login import login_user
        from flask import url_for
        
        # 登录admin
        login_user(admin)
        
        # 导入index视图函数
        from app.main.routes import index
        
        # 手动设置current_user
        import flask_login
        flask_login.utils._request_ctx_stack.top.user = admin
        
        # 构建tiles
        tiles = []
        if admin.role == 'admin':
            tiles.extend([
                # 第一组：账号和权限管理
                {'title':'账号申请','text':'查看待审批的账号申请','url': url_for('main.account_request_list')},
                {'title':'用户管理','text':'管理系统中的所有用户','url': url_for('main.user_management')},
                {'title':'权限管理','text':'管理自定义角色和权限','url': url_for('main.role_permission_management')},
                {'title':'部门管理','text':'管理系统中的所有部门','url': url_for('main.department_management')},
                {'title':'公开仓库','text':'查看和管理所有部门公开的设备和配件','url': url_for('main.public_pool'), 'class': 'border-success'},
                {'title':'审批流配置','text':'按工单类型配置审批流程','url': url_for('main.admin_workflow_nodes'), 'class': 'border-info'},
                
                # 第二组：资产和配件管理
                {'title':'资产/配件管理中心','text':'统一管理资产和配件，整合所有功能','url': url_for('main.asset_center')},
                {'title':'设备管理','text':'查看和管理 IT 设备','url': url_for('main.equipment_list')},
                {'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')},
                {'title':'设备类型管理','text':'管理设备类型字典','url': url_for('main.equipment_types')},
                {'title':'配件类型管理','text':'管理配件类型字典','url': url_for('main.spare_part_types')},
                
                # 第三组：工单和申请管理
                {'title':'维修工单','text':'查看和管理维修工单','url': url_for('main.repair_orders')},
                {'title':'配件申请管理','text':'查看和管理配件申请','url': url_for('main.part_request_orders')},
                {'title':'发起设备调拨','text':'发起或管理设备调拨申请','url': url_for('main.create_transfer')},
                {'title':'发起设备报废','text':'发起或管理设备报废申请','url': url_for('main.create_scrap')},
                
                # 第四组：分析和报表
                {'title':'成本分析','text':'查看资产成本分析和成本预算','url': url_for('main.cost_analysis')},
                {'title':'库存预警','text':'查看库存不足预警和采购建议','url': url_for('main.inventory_warning')},
                {'title':'生命周期','text':'查看资产生命周期和报废分析','url': url_for('main.lifecycle_dashboard')},
                {'title':'报表统计','text':'查看各类统计报表','url': url_for('main.reports')},
                
                # 第五组：系统管理
                {'title':'操作日志','text':'查看用户操作日志','url': url_for('main.user_activity_logs')},
                {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')},
                {'title':'通知中心','text':'查看系统通知与消息','url': url_for('main.notifications')},
                {'title':'数据库管理','text':'备份、恢复、重置数据库','url': url_for('main.database_management')},
            ])
        
        print(f"\nAdmin应该看到的卡片数量: {len(tiles)}")
        print("\n卡片列表:")
        for i, tile in enumerate(tiles, 1):
            print(f"{i}. {tile['title']} - {tile['url']}")
