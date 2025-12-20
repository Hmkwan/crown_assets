"""
服务层 - 业务逻辑集中处理
"""

__all__ = []

# Lazy-import other services to avoid module-level import-time side-effects in tests
try:
    from .cost_service import CostService
    __all__.append('CostService')
except Exception:
    pass

try:
    from .inventory_service import InventoryService
    __all__.append('InventoryService')
except Exception:
    pass

try:
    from .lifecycle_service import LifecycleService
    __all__.append('LifecycleService')
except Exception:
    pass

try:
    from .notification_service import NotificationService
    __all__.append('NotificationService')
except Exception:
    pass

try:
    from .approval_service import ApprovalService, ApprovalPermissionError
    __all__.extend(['ApprovalService', 'ApprovalPermissionError'])
except Exception:
    pass
