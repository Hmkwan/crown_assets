def test_normalize_dry_run_returns_int():
    """Ensure normalize_paths dry-run executes and returns an int (potential changes count)."""
    from scripts.normalize_attachment_paths import normalize_paths
    from app import create_app, db

    app = create_app()
    app.config['TESTING'] = True

    # ensure test DB has expected tables
    with app.app_context():
        db.create_all()

    changed = normalize_paths(app, apply_changes=False)
    assert isinstance(changed, int)
    assert changed >= 0
