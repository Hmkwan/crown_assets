import os
import json

# Normalize and set TEST_DATABASE_URI
raw = os.environ.get('TEST_DATABASE_URI') or 'postgresql://postgres:difyai123456@localhost:15432/it_asset'
# Replace accidental double slash before db name
normalized = raw.replace('://', '://', 1)
# ensure only single slash after host:port
normalized = normalized.replace('//it_asset', '/it_asset')
os.environ['TEST_DATABASE_URI'] = normalized
print('Using TEST_DATABASE_URI:', os.environ['TEST_DATABASE_URI'])

try:
    # Ensure project root is on sys.path
    import sys
    import pathlib
    project_root = str(pathlib.Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from app import create_app
    from app.utils import db_management
    app = create_app()
    with app.app_context():
        print('Calling initialize_system() ...')
        res = db_management.initialize_system()
        print(json.dumps(res, indent=2, ensure_ascii=False))
except Exception as e:
    import traceback
    print('Exception while running initialize_system:', str(e))
    traceback.print_exc()