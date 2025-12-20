from app import create_app, db
from app.models import User, Equipment, RepairOrder, SparePart, PartReplacement
import os

app = create_app()

# 根据环境变量决定是否启用调试模式（生产环境建议设置 FLASK_DEBUG=False）
DEBUG_MODE = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Equipment': Equipment,
        'RepairOrder': RepairOrder,
        'SparePart': SparePart,
        'PartReplacement': PartReplacement
    }


if __name__ == '__main__':
    # 仅在调试模式下打印路由
    if DEBUG_MODE:
        print('Registered routes:')
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            print(f"{rule.rule} -> endpoint={rule.endpoint} methods={methods}")

    # 启动开发服务器（Windows PowerShell 下可直接运行: python .\app.py）
    app.run(host='0.0.0.0', port=5020, debug=DEBUG_MODE)