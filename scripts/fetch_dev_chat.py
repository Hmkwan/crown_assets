import requests
s = requests.Session()
resp = s.get('http://127.0.0.1:5020/_dev/chat')
print('status', resp.status_code, resp.reason)
print('headers:', dict(resp.headers))
if resp.status_code >= 400:
    print('response body (truncated):')
    print(resp.text[:1000])
open('dev_chat_preview.html','w',encoding='utf-8').write(resp.text)
print('saved dev chat preview, len=', len(resp.text))