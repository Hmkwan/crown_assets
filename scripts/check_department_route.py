from app import create_app

app = create_app()
# disable CSRF for test client
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

with app.test_client() as c:
    login_resp = c.post('/auth/login', data={'username':'admin','password':'admin123'}, follow_redirects=True)
    print('Login status code:', login_resp.status_code)
    # After login, try to access department management
    dept_resp = c.get('/admin/departments')
    print('/admin/departments status code:', dept_resp.status_code)
    if dept_resp.status_code == 200:
        print('Department page length:', len(dept_resp.get_data(as_text=True)))
    else:
        print('Department response snippet:', dept_resp.get_data(as_text=True)[:200])
