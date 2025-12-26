import requests, re
s=requests.Session()
r=s.get('http://127.0.0.1:5020/__dev_login_admin')
print('dev login status', r.status_code)
ch=s.get('http://127.0.0.1:5020/chat')
print('chat status', ch.status_code)
print('found chat_modern.css?', 'chat_modern.css' in ch.text)
# print head area
m=re.search(r'<head>(.*?)</head>', ch.text, re.S)
if m:
    head=m.group(1)
    print(head.count('<link'), 'link tags; excerpt:')
    for line in head.splitlines():
        if 'chat_modern.css' in line or '<link' in line:
            print(line.strip())
else:
    print('no head matched')
open('artifacts/chat_html_check.html','w',encoding='utf-8').write(ch.text)
print('wrote artifacts/chat_html_check.html')
