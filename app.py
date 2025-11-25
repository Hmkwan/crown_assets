from app import create_app, db
from app.models import User, Equipment, RepairOrder, SparePart, PartReplacement

app = create_app()


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
    # 打印已注册的路由，方便诊断 404/路由未注册问题
    print('Registered routes:')
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        print(f"{rule.rule} -> endpoint={rule.endpoint} methods={methods}")

    # 启动开发服务器（Windows PowerShell 下可直接运行: python .\app.py）
    app.run(host='0.0.0.0', port=5020, debug=True)