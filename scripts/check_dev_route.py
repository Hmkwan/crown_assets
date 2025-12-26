import requests
try:
    r=requests.get('http://127.0.0.1:5020/__dev_login_admin', allow_redirects=True, timeout=5)
    print('status', r.status_code, 'url', r.url)
    print('len', len(r.text))
except Exception as e:
    print('err', e)
