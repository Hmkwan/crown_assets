import requests
r=requests.get('http://127.0.0.1:5020/__dev_login_admin', timeout=5)
print('status', r.status_code)
print(r.url)
print('len', len(r.text))
