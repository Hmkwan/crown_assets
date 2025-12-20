# Bridge stub: try to delegate to the real psycopg2 if available, otherwise provide a helpful error.
try:
    import psycopg2 as _psycopg2_real
    # re-export commonly used attributes
    connect = _psycopg2_real.connect
    OperationalError = _psycopg2_real.OperationalError
    paramstyle = getattr(_psycopg2_real, 'paramstyle', None)
    # re-export extras submodule if present (SQLAlchemy uses this)
    try:
        extras = _psycopg2_real.extras
    except Exception:
        extras = None
    try:
        extensions = _psycopg2_real.extensions
    except Exception:
        extensions = None
except Exception:
    class OperationalError(Exception):
        pass
    def connect(*args, **kwargs):
        raise OperationalError('Real psycopg2 not available; install psycopg2-binary or set TEST_DATABASE_URI to sqlite')
    paramstyle = None
    extras = None
