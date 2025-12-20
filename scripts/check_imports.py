import traceback

try:
    import app.models as m
    print('Imported app.models OK')
    print('Has Announcement:', hasattr(m, 'Announcement'))
    print('Has User:', hasattr(m, 'User'))
except Exception:
    traceback.print_exc()
