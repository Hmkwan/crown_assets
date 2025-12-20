"""Quick diagnostic: attempt to import key model classes and report results.
Run with: python scripts/validate_models_import.py
"""
import sys
import importlib

print('Python:', sys.executable)
print('sys.path[0]:', sys.path[0])

try:
    # Try importing the package first
    import app
    print('app module:', getattr(app, '__file__', 'built-in'))
except Exception as e:
    print('Failed to import app package:', e)

# Attempt to import models via importlib (module)
try:
    m = importlib.import_module('app.models')
    print('app.models loaded as:', type(m), getattr(m, '__file__', None))
    for name in ['User', 'Department', 'Equipment', 'WorkflowNode', 'WorkflowTemplate']:
        print(f"Has {name}:", hasattr(m, name))
except Exception as e:
    print('Failed to import app.models:', e)

# Try attribute access on package
try:
    import app as app_pkg
    for name in ['User', 'Department', 'Equipment']:
        try:
            val = getattr(app_pkg.models, name)
            print(f'package access {name}:', type(val))
        except Exception as ex:
            print(f'package access {name} failed:', ex)
except Exception as e:
    print('Error accessing app_pkg.models:', e)

print('\nModules with app.models or __models_shim__ in sys.modules:')
for k in sorted(s for s in sys.modules.keys() if 'app.models' in s or '__models_shim__' in s):
    print(' -', k)