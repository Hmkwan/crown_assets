# Lightweight shim of flask_socketio to avoid ImportError during test collection.
# This is intentionally minimal and only intended for tests that import the module
# but don't require full socket behavior. For full integration tests, install the
# real Flask-SocketIO and eventlet/gevent as appropriate.

from functools import wraps

class SocketIO:
    def __init__(self, app=None, **kwargs):
        self.app = app
        self._handlers = {}

    def on(self, event):
        def decorator(func):
            self._handlers.setdefault(event, []).append(func)
            return func
        return decorator

    def emit(self, *args, **kwargs):
        # no-op
        return None

    def start_background_task(self, target, *args, **kwargs):
        import threading
        t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    def run(self, *args, **kwargs):
        return None

# helper functions kept as no-ops for compatibility
def emit(*args, **kwargs):
    return None

def join_room(*args, **kwargs):
    return None

def leave_room(*args, **kwargs):
    return None

def disconnect(*args, **kwargs):
    return None
