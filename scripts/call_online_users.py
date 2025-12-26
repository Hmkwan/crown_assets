import requests
r = requests.get('http://127.0.0.1:5020/api/online_users')
print('status', r.status_code, r.text)