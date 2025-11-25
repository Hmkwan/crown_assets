import sys
import os
# ensure project root is on sys.path when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from config import Config
app = create_app(Config)
print('Routes for app created by create_app():')
for r in sorted([str(r) for r in app.url_map.iter_rules()]):
    print(r)
