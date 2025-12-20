# 初始化兼容 shim：将顶层 `app/models.py` 的定义导入到包命名空间
#
# 原因：项目中同时存在 `app/models.py`（模块）和 `app/models/`（包），
# 导致 `app.models` 被解析为包，从而隐藏顶层模块并引发导入冲突。
# 这里按路径动态加载顶层 `models.py` 并把非私有符号拷贝到包中，
# 以兼容现有 `from app.models import Xxx` 的用法，避免大规模重构。

"""按需惰性导入模型符号，避免在包导入阶段触发循环导入。

实现逻辑：当访问 `app.models.<Name>` 时，尝试按顺序从若干候选模块加载该符号：
1. 顶层文件 `app/models.py`（通过文件路径加载，避免与包混淆）；
2. 若干可能包含模型定义的子模块（如 `app.approval_models`、`app.workflow_models` 等）。

这种惰性加载可避免在应用启动（注册蓝图等阶段）立即执行大量相互依赖的顶级导入，从而减少循环导入错误。
"""

from pathlib import Path
import importlib
import importlib.util
from typing import Any


_ROOT_MODELS = Path(__file__).resolve().parents[0].parent / 'models.py'
_CANDIDATE_MODULES = [
	'app.approval_models',
	'app.workflow_models',
	'app.approval_roles',
	'app.asset_models',
	'app.models',  # 最后尝试标准导入
]


import sys

_loaded_module_cache = {}

def _load_module_from_file(path: Path, name: str):
	"""Load module from file path with minimal side-effects.

	- Inserts the module into sys.modules before exec to allow recursive imports
	  during execution to resolve to the same module object (prevents repeated loads).
	- Caches the loaded module to avoid re-executing expensive model code.
	"""
	# Return cached if already loaded
	if name in _loaded_module_cache:
		return _loaded_module_cache[name]

	spec = importlib.util.spec_from_file_location(name, str(path))
	module = importlib.util.module_from_spec(spec)
	# Ensure recursive imports see this module during execution
	sys.modules[name] = module
	try:
		spec.loader.exec_module(module)
		# 如果我们是加载顶层 models.py 的 shim 名称，确保也把它注册为 'app.models'
		_loaded_module_cache[name] = module
		if name == 'app.__models_shim__':
			_loaded_module_cache['app.models'] = module
			sys.modules['app.models'] = module
		return module
	except Exception:
		# Cleanup on failure to avoid leaving a broken module in sys.modules
		if name in sys.modules and sys.modules[name] is module:
			del sys.modules[name]
		raise


# 预先加载常用模型以确保 `from app.models import X` 在测试收集阶段也能正常工作
_common_names = ['User', 'Department', 'Announcement', 'AnnouncementAttachment', 'WorkflowNode', 'WorkflowTemplate']
try:
	if _ROOT_MODELS.exists():
		try:
			_mod = _load_module_from_file(_ROOT_MODELS, 'app.__models_shim__')
			for _n in _common_names:
				if hasattr(_mod, _n):
					globals()[_n] = getattr(_mod, _n)
		except Exception:
			# 忽略错误，保持惰性加载作为回退
			pass
except Exception:
	pass

_LOADING = set()


def __getattr__(name: str) -> Any:
	# 防止重入导致无限递归：如果该符号正在加载中，直接返回 AttributeError
	if name in _LOADING:
		raise AttributeError(f"module {__name__} has no attribute {name} (loading)")

	# 先尝试从顶层 models.py 文件加载（避免与包本身混淆）
	try:
		if _ROOT_MODELS.exists():
			_LOADING.add(name)
			try:
				mod = _load_module_from_file(_ROOT_MODELS, 'app.__models_shim__')
				if hasattr(mod, name):
					val = getattr(mod, name)
					# cache onto package to avoid repeated loader invocations
					globals()[name] = val
					return val
			finally:
				_LOADING.discard(name)
	except Exception:
		# 忽略加载错误，继续尝试其他候选模块
		pass

	# 再尝试从候选模块导入符号（逐个尝试，遇到错误忽略）
	for module_name in _CANDIDATE_MODULES:
		if name in _LOADING:
			break
		try:
			_LOADING.add(name)
			try:
				mod = importlib.import_module(module_name)
				if hasattr(mod, name):
					val = getattr(mod, name)
					# cache onto package to avoid repeated loader invocations
					globals()[name] = val
					return val
			finally:
				_LOADING.discard(name)
		except Exception:
			continue

	raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
	# 保守实现：仅列出常见符号以帮助自动补全（非详尽）
	return list(globals().keys()) + ['User', 'Department', 'Equipment', 'WorkflowNode', 'WorkflowTemplate']