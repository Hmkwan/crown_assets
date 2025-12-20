#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    print(f'Admin found: {admin is not None}')
    print(f'Admin role: {admin.role if admin else "N/A"}')
    
    with app.test_client() as client:
        # Try to access index without login
        response = client.get('/index')
        print(f'\nWithout login:')
        print(f'  Status: {response.status_code}')
        print(f'  Location: {response.headers.get("Location", "none")}')
        
        # Now try with follow_redirects
        response = client.get('/index', follow_redirects=True)
        print(f'\nWith follow_redirects:')
        print(f'  Status: {response.status_code}')
        
        html = response.get_data(as_text=True)
        print(f'  HTML length: {len(html)}')
        print(f'  Contains "login": {"login" in html.lower()}')
        print(f'  Contains "成本分析": {"成本分析" in html}')
        print(f'  Contains "tiles": {"tiles" in html}')
        
        # Check actual response content
        if "成本分析" in html:
            print("\n✓ 成本分析已在首页")
        else:
            # Check if the page is redirecting to login
            if "/auth/login" in response.request.path or "login" in html.lower():
                print("\n! Redirected to login page, tiles not rendered")
            else:
                print(f"\n! Page is not login, but 成本分析 not found")
                # Print first 500 chars of body to debug
                idx = html.find('<body')
                if idx > 0:
                    print(f"  Body snippet: {html[idx:idx+500]}")
