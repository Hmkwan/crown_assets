def test_normalize_dry_run_returns_int(app):
    """Ensure normalize_paths dry-run executes and returns an int (potential changes count)."""
    from scripts.normalize_attachment_paths import normalize_paths
    changed = normalize_paths(app, apply_changes=False)
    assert isinstance(changed, int)
    assert changed >= 0
