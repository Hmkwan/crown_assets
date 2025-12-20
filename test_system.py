"""快速系统测试脚本"""
from app import create_app, db
from app.models import User, Equipment, MaintenancePlan, MaintenanceRecord

app = create_app()

with app.app_context():
    print("\n=== 系统状态检查 ===\n")
    
    # 检查数据库连接
    try:
        db.session.execute('SELECT 1')
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        exit(1)
    
    # 检查关键表
    tables = {
        'app_user': User,
        'equipment': Equipment,
        'maintenance_plan': MaintenancePlan,
        'maintenance_record': MaintenanceRecord,
    }
    
    for table_name, model in tables.items():
        try:
            count = model.query.count()
            print(f"✅ {table_name} 表存在, 记录数: {count}")
        except Exception as e:
            print(f"❌ {table_name} 表错误: {e}")
    
    # 检查用户
    try:
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"\n✅ 管理员账户: {admin.username}")
        else:
            print("\n⚠️  没有找到管理员账户")
    except Exception as e:
        print(f"\n❌ 查询用户失败: {e}")
    
    # 检查设备
    try:
        eq_count = Equipment.query.count()
        print(f"✅ 设备总数: {eq_count}")
    except Exception as e:
        print(f"❌ 查询设备失败: {e}")
    
    print("\n=== 检查完成 ===\n")
