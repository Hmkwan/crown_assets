#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        pwd_ok = admin.check_password('admin123')
        print('Admin account:', admin.username)
        print('Email:', admin.email)
        print('Role:', admin.role)
        print('Password correct:', pwd_ok)
    else:
        print('Admin account does not exist')
