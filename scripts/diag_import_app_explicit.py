import traceback, importlib.util, os
try:
    # 确保工作目录在 sys.path 中，这样 app/__init__.py 中的顶层 imports (如 config) 能被找到
    import sys
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    pkg_path = os.path.join(cwd, 'app', '__init__.py')
    spec = importlib.util.spec_from_file_location('app_pkg', pkg_path)
    app_pkg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_pkg)
    create_app = getattr(app_pkg, 'create_app')
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    try:
        # 明确加载 app/models.py，避免包名冲突
        models_path = os.path.join(cwd, 'app', 'models.py')
        spec2 = importlib.util.spec_from_file_location('app_models_pkg', models_path)
        models_pkg = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(models_pkg)
        User = getattr(models_pkg, 'User')
        print('成功导入 app 包（命名为 app_pkg），并加载 models')
        print('用户数:', User.query.count())
    finally:
        ctx.pop()
except Exception:
    traceback.print_exc()
