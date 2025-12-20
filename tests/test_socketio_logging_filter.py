import logging
from app import create_app


def test_engineio_socketio_filters_attached():
    app = create_app()
    # Ensure loggers exist and that our suppress filter is attached
    eng_logger = logging.getLogger('engineio')
    sock_logger = logging.getLogger('socketio')

    def has_suppress_filter(lg):
        for f in lg.filters:
            if f.__class__.__name__ == '_SuppressEngineIOSpecificMessages':
                return True
        return False

    assert has_suppress_filter(eng_logger) or has_suppress_filter(sock_logger)
