import traceback
try:
    from app import create_app
    app = create_app()
    for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
        print(f"{r.rule} -> endpoint={r.endpoint} methods={','.join(r.methods)}")
except Exception as e:
    traceback.print_exc()
    print('Failed to list routes:', e)
