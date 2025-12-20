"""
初始化设备类型和配件类型数据
"""
from app import create_app, db
from app.models import EquipmentType, SparePartType

def init_types():
    app = create_app()
    with app.app_context():
        # 初始化设备类型
        equipment_types = [
            {'name': '台式电脑', 'description': '办公用台式计算机'},
            {'name': '笔记本电脑', 'description': '便携式笔记本电脑'},
            {'name': '服务器', 'description': '数据中心服务器设备'},
            {'name': '打印机', 'description': '打印、复印设备'},
            {'name': '扫描仪', 'description': '文档扫描设备'},
            {'name': '投影仪', 'description': '会议室投影设备'},
            {'name': '显示器', 'description': '计算机显示器'},
            {'name': '路由器', 'description': '网络路由设备'},
            {'name': '交换机', 'description': '网络交换机'},
            {'name': '防火墙', 'description': '网络安全设备'},
            {'name': 'UPS电源', 'description': '不间断电源'},
            {'name': '网络存储', 'description': 'NAS/SAN存储设备'},
            {'name': '摄像头', 'description': '监控摄像设备'},
            {'name': '会议设备', 'description': '视频会议终端'},
            {'name': '电话设备', 'description': 'IP电话、座机'},
        ]
        
        # 初始化配件类型
        spare_part_types = [
            {'name': '内存条', 'description': 'RAM内存模块'},
            {'name': '硬盘', 'description': '机械硬盘/固态硬盘'},
            {'name': '电源', 'description': '主机电源模块'},
            {'name': '主板', 'description': '计算机主板'},
            {'name': 'CPU', 'description': '中央处理器'},
            {'name': '显卡', 'description': '图形处理卡'},
            {'name': '散热器', 'description': 'CPU散热器'},
            {'name': '机箱风扇', 'description': '散热风扇'},
            {'name': '网卡', 'description': '有线/无线网卡'},
            {'name': '声卡', 'description': '音频处理卡'},
            {'name': '键盘', 'description': '输入设备-键盘'},
            {'name': '鼠标', 'description': '输入设备-鼠标'},
            {'name': '数据线', 'description': 'HDMI/VGA/DP/USB等线缆'},
            {'name': '网线', 'description': '以太网线缆'},
            {'name': '电源线', 'description': '电源连接线'},
            {'name': '墨盒/硒鼓', 'description': '打印机耗材'},
            {'name': '打印纸', 'description': 'A4/A3打印纸'},
            {'name': '投影灯泡', 'description': '投影仪灯泡'},
            {'name': '电池', 'description': 'UPS电池、笔记本电池'},
            {'name': '转接头', 'description': '各类接口转接器'},
        ]
        
        # 添加设备类型
        added_equipment_types = 0
        for type_data in equipment_types:
            existing = EquipmentType.query.filter_by(name=type_data['name']).first()
            if not existing:
                new_type = EquipmentType(**type_data)
                db.session.add(new_type)
                added_equipment_types += 1
                print(f"添加设备类型: {type_data['name']}")
        
        # 添加配件类型
        added_spare_part_types = 0
        for type_data in spare_part_types:
            existing = SparePartType.query.filter_by(name=type_data['name']).first()
            if not existing:
                new_type = SparePartType(**type_data)
                db.session.add(new_type)
                added_spare_part_types += 1
                print(f"添加配件类型: {type_data['name']}")
        
        try:
            db.session.commit()
            print(f"\n初始化完成！")
            print(f"新增设备类型: {added_equipment_types} 个")
            print(f"新增配件类型: {added_spare_part_types} 个")
        except Exception as e:
            db.session.rollback()
            print(f"初始化失败: {str(e)}")

if __name__ == '__main__':
    init_types()
