import requests, re
BASE='http://10.168.93.93:5020'
s=requests.Session()
# get login page
r=s.get(BASE+'/auth/login')
print('GET /auth/login status', r.status_code)
# try to find hidden csrf input
m=re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', r.text)
if m:
    print('hidden csrf input value found')
    csrf = m.group(1)
else:
    # fallback to meta
    m2=re.search(r'<meta name="csrf-token" content="([^"]+)"', r.text)
    csrf = m2.group(1) if m2 else ''
    print('meta csrf token found?', bool(csrf))

headers={'X-CSRFToken': csrf, 'Referer': BASE + '/auth/login', 'User-Agent':'Mozilla/5.0'}
payload={'username':'admin','password':'TempPass123!','csrf_token':csrf,'submit':'Login'}
resp=s.post(BASE+'/auth/login', data=payload, headers=headers, allow_redirects=True)
print('POST status', resp.status_code)
print('history len', len(resp.history))
print('Set-Cookie header:', resp.headers.get('Set-Cookie'))
print('cookie jar after post:', s.cookies.get_dict())
print('login body contains error?', '用户名或密码错误' in resp.text)
# Try API
api = s.get(BASE + '/api/chat/conversations', headers={'X-CSRFToken': csrf, 'Referer': BASE + '/chat'})
print('/api status', api.status_code)
print('api headers', api.headers.get('content-type'))
print('api body', api.text[:200])
