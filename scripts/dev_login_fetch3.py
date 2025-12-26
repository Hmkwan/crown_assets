import requests
s=requests.Session()
resp=s.get('http://127.0.0.1:5020/__dev_login_admin', allow_redirects=True, timeout=5)
print('dev login status', resp.status_code)
print('url', resp.url)
chat=s.get('http://127.0.0.1:5020/chat', timeout=5)
open('chat_logged_in.html','w',encoding='utf-8').write(chat.text)
print('wrote chat_logged_in.html length', len(chat.text))
