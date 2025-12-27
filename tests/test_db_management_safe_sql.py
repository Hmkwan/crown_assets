import pytest

from app.utils import db_management


def test_is_valid_identifier():
    assert db_management._is_valid_identifier('users')
    assert db_management._is_valid_identifier('user_1')
    assert not db_management._is_valid_identifier('1_invalid')
    assert not db_management._is_valid_identifier('weird-name')
    assert not db_management._is_valid_identifier('injection; DROP TABLE')


def test_get_table_data_with_temp_table():
    # create a fresh app context for the test
    from app import create_app, db
    from sqlalchemy import text
    app = create_app()

    with app.app_context():
        engine = db.engine
        # create a temporary table and insert rows
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS tmp_test_table (id SERIAL PRIMARY KEY, name TEXT);"))
            conn.execute(text("INSERT INTO tmp_test_table (name) VALUES ('a'), ('b'), ('c');"))

        # Fetch via helper
        res = db_management.get_table_data('tmp_test_table', page=1, per_page=2)
        assert res['success'] is True
        assert res['total_count'] == 3
        assert len(res['data']) == 2

        # cleanup
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS tmp_test_table;"))


def test_get_table_data_rejects_invalid_name():
    # Use a clearly malicious name
    from app import create_app
    app = create_app()
    bad_name = 'tmp_test_table; DROP TABLE app_user; --'
    with app.app_context():
        res = db_management.get_table_data(bad_name)
        assert res['success'] is False
        assert '不存在' in res['message'] or '无效' in res['message']