import socket as _original_socket
_USE_EVENTLET = False
try:
    import eventlet
    eventlet.monkey_patch()
    _USE_EVENTLET = True
    import sys
    sys.modules['_original_socket'] = _original_socket
except Exception:
    _USE_EVENTLET = False

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

from app import create_app, db
from app.models import User, Equipment, RepairOrder, SparePart, PartReplacement

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
    if DEBUG_MODE:
        print('Registered routes:')
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            print(f"{rule.rule} -> endpoint={rule.endpoint} methods={methods}")

    if hasattr(app, 'socketio') and app.socketio:
        print('✓ 使用SocketIO启动服务器')
        app.socketio.run(app, host='0.0.0.0', port=5020, debug=DEBUG_MODE)
    else:
        print('⚠ SocketIO未初始化,使用标准Flask服务器')
        app.run(host='0.0.0.0', port=5020, debug=DEBUG_MODE)
