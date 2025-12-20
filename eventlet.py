# Minimal stub for eventlet used in tests/environments where eventlet is not installed.
# Provides monkey_patch() as a no-op to avoid ImportError during tests.

def monkey_patch():
    # No-op monkey patch for environments without eventlet
    return
