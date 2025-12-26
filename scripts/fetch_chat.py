import re, requests
s = requests.Session()
r = s.get('http://127.0.0.1:5020/auth/login')
m = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', r.text)
if not m:
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', r.text)
if m:
    token = m.group(1)
else:
    token = ''
print('csrf token len=', len(token))
payload = {'csrf_token': token, 'username': 'admin', 'password': 'TestPass123!', 'remember_me': 'y'}
resp = s.post('http://127.0.0.1:5020/auth/login', data=payload, allow_redirects=True)
print('login resp:', resp.status_code, 'url:', resp.url)
chat = s.get('http://127.0.0.1:5020/chat')
open('chat_page_after_login.html','w',encoding='utf-8').write(chat.text)
print('fetched /chat length:', len(chat.text))