import requests, re
s=requests.Session()
resp=s.get('http://127.0.0.1:5020/auth/login')
html=resp.text
m=re.search(r'name="csrf_token" value="([^"]+)"', html)
csrf = m.group(1) if m else ''
print('got csrf', bool(csrf))
login_data={'username':'admin','password':'Password123!','csrf_token':csrf}
resp2=s.post('http://127.0.0.1:5020/auth/login', data=login_data, allow_redirects=True)
print('login status', resp2.status_code)
chat = s.get('http://127.0.0.1:5020/chat')
open('chat_after_login.html','w',encoding='utf-8').write(chat.text)
print('wrote chat_after_login.html, len', len(chat.text))
