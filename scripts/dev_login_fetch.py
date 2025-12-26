import requests
s=requests.Session()
resp=s.get('http://127.0.0.1:5020/__dev_login_admin', allow_redirects=True)
print('dev login status', resp.status_code, 'url', resp.url)
chat=s.get('http://127.0.0.1:5020/chat')
open('chat_logged_in.html','w',encoding='utf-8').write(chat.text)
print('wrote chat_logged_in.html len', len(chat.text))
