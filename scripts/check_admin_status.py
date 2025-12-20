#!/usr/bin/env python
"""Check admin account status in the application's configured database.

Usage:
    python scripts/check_admin_status.py [--password <plaintext>]

If --password is provided the script will check whether that password
matches the stored admin password (useful to verify hashing/DB consistency).

This script is intended for local debugging only.
"""
import sys
import argparse
from app import create_app, db
from app.models import User

parser = argparse.ArgumentParser()
parser.add_argument('--password', '-p', help='Plaintext password to verify against admin account')
args = parser.parse_args()

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print('No admin user found in the configured database.')
        sys.exit(1)

    print(f'Found admin: username={admin.username}, email={admin.email}, role={admin.role}')
    if args.password:
        ok = admin.check_password(args.password)
        print(f'Password match for provided password: {ok}')
    else:
        print('Run with --password <plaintext> to verify a password against the stored hash.')

    # print some basic flags
    print('Permissions flags:')
    print(f'  can_manage_equipment: {admin.can_manage_equipment}')
    print(f'  can_manage_spare_parts: {admin.can_manage_spare_parts}')
    print(f'  can_view_reports: {admin.can_view_reports}')
