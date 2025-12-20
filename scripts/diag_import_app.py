import traceback
try:
    from app import create_app
    from app.models import User
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    try:
        print('create_app imported and context pushed')
        print('User table access test: count =', User.query.count())
    finally:
        ctx.pop()
except Exception:
    traceback.print_exc()
