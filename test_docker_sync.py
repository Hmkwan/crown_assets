"""
测试Docker实时同步配置
修改此文件,容器内应立即看到变化
"""
from app import create_app, db
from datetime import datetime

def test_sync():
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("  Docker实时同步测试")
        print("=" * 70)
        print(f"\n测试时间: {datetime.now()}")
        print("如果能看到这行,说明容器已成功挂载本地代码!")
        print("\n配置详情:")
        print("  - 本地代码修改会立即反映到容器")
        print("  - 数据库修改会实时同步")
        print("  - 无需重新构建镜像")
        print("  - Flask Debug模式已启用(自动重载)")
        print("\n" + "=" * 70)

if __name__ == '__main__':
    test_sync()
