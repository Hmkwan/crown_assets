"""
系统初始化脚本
功能: 清除所有用户数据，保留系统基础配置
使用: python initialize_system.py
"""

from app import create_app, db
from app.models import (
    AppUser, Role, Permission, EquipmentType, Department,
    Location, ApprovalWorkflow, ApprovalStep, AccessoryType,
    EquipmentStatus, Equipment, EquipmentTransfer, EquipmentLoan,
    EquipmentApplication, PurchaseRequest, PurchaseOrder, ApprovalDecision,
    ActionLog
)
from datetime import datetime
import sys

def get_all_tables():
    """获取数据库中所有表"""
    return db.metadata.tables.keys()

def init_roles_and_permissions():
    """初始化角色和权限"""
    print("  → 初始化角色和权限...")
    
    # 检查是否已存在
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        print("    ✓ 角色已存在，跳过")
        return
    
    # 创建角色
    roles_data = [
        {'name': 'admin', 'display_name': '管理员', 'description': '系统管理员，拥有所有权限'},
        {'name': 'manager', 'display_name': '经理', 'description': '部门经理，可以审批和管理'},
        {'name': 'staff', 'display_name': '员工', 'description': '普通员工，可以申请和查看'},
        {'name': 'viewer', 'display_name': '查看者', 'description': '只读权限，仅查看'},
    ]
    
    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
            print(f"    ✓ 创建角色: {role_data['display_name']}")
    
    db.session.commit()

def init_equipment_types():
    """初始化设备类型"""
    print("  → 初始化设备类型...")
    
    if EquipmentType.query.first():
        print("    ✓ 设备类型已存在，跳过")
        return
    
    types = [
        '台式计算机', '笔记本电脑', '打印机', '扫描仪',
        '显示器', '键盘', '鼠标', '网络交换机',
        '无线路由器', 'UPS电源', '投影仪', '会议系统'
    ]
    
    for type_name in types:
        eq_type = EquipmentType(name=type_name)
        db.session.add(eq_type)
        print(f"    ✓ 创建设备类型: {type_name}")
    
    db.session.commit()

def init_accessory_types():
    """初始化配件类型"""
    print("  → 初始化配件类型...")
    
    if AccessoryType.query.first():
        print("    ✓ 配件类型已存在，跳过")
        return
    
    types = [
        'DDR4内存', 'DDR5内存', 'SSD固态硬盘', 'HDD机械硬盘',
        '显示器线缆', 'USB-C线缆', 'HDMI线缆', '电源适配器',
        '散热风扇', '硅脂', 'USB集线器', '扩展坞'
    ]
    
    for type_name in types:
        acc_type = AccessoryType(name=type_name)
        db.session.add(acc_type)
        print(f"    ✓ 创建配件类型: {type_name}")
    
    db.session.commit()

def init_equipment_status():
    """初始化设备状态"""
    print("  → 初始化设备状态...")
    
    if EquipmentStatus.query.first():
        print("    ✓ 设备状态已存在，跳过")
        return
    
    statuses = [
        ('正常', '设备正常可用'),
        ('维修中', '设备在维修中'),
        ('停用', '设备已停用'),
        ('报废', '设备已报废'),
        ('在库', '设备在仓库中'),
        ('转移中', '设备转移中'),
    ]
    
    for status_name, description in statuses:
        status = EquipmentStatus(name=status_name, description=description)
        db.session.add(status)
        print(f"    ✓ 创建设备状态: {status_name}")
    
    db.session.commit()

def init_departments():
    """初始化基础部门"""
    print("  → 初始化部门...")
    
    if Department.query.filter_by(name='总公司').first():
        print("    ✓ 部门已存在，跳过")
        return
    
    # 创建根部门
    root = Department(name='总公司', description='公司总部')
    db.session.add(root)
    db.session.flush()  # 获取root的ID
    
    # 创建子部门
    sub_depts = [
        '行政部', '技术部', '财务部', '人力资源部',
        '销售部', '采购部', '仓储部', '运维部'
    ]
    
    for dept_name in sub_depts:
        dept = Department(name=dept_name, parent_id=root.id, description=f'{dept_name}')
        db.session.add(dept)
        print(f"    ✓ 创建部门: {dept_name}")
    
    db.session.commit()

def init_locations():
    """初始化位置"""
    print("  → 初始化位置...")
    
    if Location.query.first():
        print("    ✓ 位置已存在，跳过")
        return
    
    locations = [
        ('总部办公室', '公司总部办公地点'),
        ('机房', '服务器机房'),
        ('仓库', '设备仓库'),
        ('配送中心', '设备配送中心'),
    ]
    
    for loc_name, description in locations:
        location = Location(name=loc_name, description=description)
        db.session.add(location)
        print(f"    ✓ 创建位置: {loc_name}")
    
    db.session.commit()

def init_approval_workflows():
    """初始化审批流程"""
    print("  → 初始化审批流程...")
    
    if ApprovalWorkflow.query.first():
        print("    ✓ 审批流程已存在，跳过")
        return
    
    workflows = [
        {
            'name': '采购审批流程',
            'description': '设备和配件采购申请审批',
            'workflow_type': 'purchase'
        },
        {
            'name': '设备报废流程',
            'description': '设备报废申请审批',
            'workflow_type': 'scrap'
        },
        {
            'name': '设备转移流程',
            'description': '设备转移申请审批',
            'workflow_type': 'transfer'
        },
        {
            'name': '设备借用流程',
            'description': '设备借用申请审批',
            'workflow_type': 'loan'
        },
    ]
    
    for wf_data in workflows:
        workflow = ApprovalWorkflow(**wf_data)
        db.session.add(workflow)
        print(f"    ✓ 创建审批流程: {wf_data['name']}")
    
    db.session.commit()

def init_admin_user():
    """创建超级管理员"""
    print("  → 初始化超级管理员...")
    
    admin = AppUser.query.filter_by(username='admin').first()
    
    if admin:
        print("    ✓ 管理员已存在，跳过")
        return
    
    admin_role = Role.query.filter_by(name='admin').first()
    admin = AppUser(
        username='admin',
        email='admin@company.com',
        full_name='系统管理员',
        role=admin_role,
        is_active=True
    )
    admin.set_password('admin123456')  # 默认密码
    
    db.session.add(admin)
    db.session.commit()
    print(f"    ✓ 创建管理员账号")
    print(f"      用户名: admin")
    print(f"      密码: admin123456")
    print(f"      ⚠️  请在登录后立即修改密码！")

def clear_user_data():
    """清除所有用户数据"""
    print("\n【清除用户数据】")
    
    tables_to_clear = [
        ('Equipment', '设备记录'),
        ('EquipmentTransfer', '设备转移'),
        ('EquipmentLoan', '设备借用'),
        ('EquipmentApplication', '设备申请'),
        ('PurchaseRequest', '采购请求'),
        ('PurchaseOrder', '采购订单'),
        ('ApprovalDecision', '审批决定'),
        ('ActionLog', '操作日志'),
    ]
    
    for model_name, display_name in tables_to_clear:
        try:
            # 动态获取模型类
            model = globals().get(model_name)
            if model:
                count = db.session.query(model).delete()
                if count > 0:
                    print(f"  ✓ 清空 {display_name}: {count} 条记录")
                else:
                    print(f"  → {display_name}: 无数据")
        except Exception as e:
            print(f"  ✗ 清空 {display_name} 失败: {str(e)}")
    
    # 清除除admin外的所有用户
    admin_user = AppUser.query.filter_by(username='admin').first()
    if admin_user:
        delete_count = AppUser.query.filter(AppUser.id != admin_user.id).delete()
        if delete_count > 0:
            print(f"  ✓ 清空员工账号: {delete_count} 条")
    
    db.session.commit()

def initialize_system():
    """执行系统初始化"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║          系统初始化 - 清除用户数据保留基础配置              ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # 确认
    print("⚠️  警告: 此操作将清除所有用户数据！")
    print("已保留: 角色权限、设备类型、部门、审批流程等基础配置")
    print("已清除: 所有设备、采购、申请、日志等业务数据\n")
    
    confirm = input("请输入 'yes' 确认初始化: ").strip().lower()
    if confirm != 'yes':
        print("❌ 初始化已取消")
        return False
    
    print("\n【初始化过程】")
    
    try:
        # 清除用户数据
        clear_user_data()
        
        print("\n【初始化基础配置】")
        
        # 初始化基础数据
        init_roles_and_permissions()
        init_equipment_types()
        init_accessory_types()
        init_equipment_status()
        init_departments()
        init_locations()
        init_approval_workflows()
        init_admin_user()
        
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║                  ✓ 系统初始化完成！                       ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
        print("【初始化结果】")
        print("✓ 用户数据已清除")
        print("✓ 基础配置已初始化")
        print("✓ 管理员账号已创建")
        print("\n【下一步】")
        print("1. 使用管理员账号登录: admin / admin123456")
        print("2. 修改管理员密码")
        print("3. 创建部门管理员和员工账号")
        print("4. 自定义设备类型和配件类型（如需要）")
        print("5. 配置审批流程规则")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        success = initialize_system()
        sys.exit(0 if success else 1)
