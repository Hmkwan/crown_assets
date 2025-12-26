import requests,re
s=requests.Session()
resp=s.get('http://127.0.0.1:5020/auth/login')
html=resp.text
m=re.search(r'id="csrf_token"[^>]*value="([^"]+)"', html)
if not m:
    m=re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
csrf = m.group(1) if m else ''
login_data={'username':'admin','password':'Password123!','csrf_token':csrf,'submit':'登录','remember_me':'y'}
resp2=s.post('http://127.0.0.1:5020/auth/login', data=login_data, allow_redirects=True)
if '用户名或密码错误' in resp2.text:
    print('login failed: bad credentials')
elif '请先登录以访问此页面' in resp2.text:
    print('still on login page')
else:
    print('login response ok, length', len(resp2.text))
print('status', resp2.status_code, 'url', resp2.url)
