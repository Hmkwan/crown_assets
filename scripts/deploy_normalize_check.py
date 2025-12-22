#!/usr/bin/env python3
"""Deployment helper: run normalization in dry-run and exit non-zero if potential changes exist.

Usage:
    python scripts/deploy_normalize_check.py

This should be run during deployment after migrations to detect whether normalization would change production data.
"""
import sys
from scripts.normalize_attachment_paths import normalize_paths
from app import create_app

if __name__ == '__main__':
    app = create_app()
    print('Running attachment path normalization in dry-run mode...')
    changed = normalize_paths(app, apply_changes=False)
    if changed:
        print(f'WARNING: Dry-run detected {changed} potential changes. Do NOT apply blindly in production. Run the normalize script with --apply after backup.')
        sys.exit(2)
    else:
        print('No potential changes detected. Safe to proceed.')
        sys.exit(0)