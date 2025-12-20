"""Minimal socketio client stub for tests"""
import time
class Client:
    def __init__(self):
        self.connected = False
        self._handlers = {}
    def connect(self, url, headers=None):
        self.connected = True
    def on(self, event):
        def decorator(f):
            self._handlers[event] = f
            return f
        return decorator
    def emit(self, event, *args, **kwargs):
        # no-op
        return None
    def wait(self, seconds=None):
        time.sleep(seconds or 0)
    def disconnect(self):
        self.connected = False
