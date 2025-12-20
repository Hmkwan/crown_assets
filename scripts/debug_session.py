from app import create_app

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

app = create_app(TestConfig)
with app.app_context():
    client = app.test_client()
    try:
        with client.session_transaction() as sess:
            print('session opened:', sess)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('App config keys relevant:', {k: app.config.get(k) for k in ['SECRET_KEY','SESSION_COOKIE_NAME','TESTING']})
