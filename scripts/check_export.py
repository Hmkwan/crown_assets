#!/usr/bin/env python3
import requests, re
BASE='http://localhost:5020'

s=requests.Session()
# get csrf
r=s.get(BASE+'/auth/login')
m=re.search(r"name=['\"]csrf_token['\"]\s+value=['\"]([^'\"]+)['\"]", r.text)
csrf=m.group(1) if m else ''
if not csrf:
    r2=s.get(BASE+'/chat')
    m=re.search(r'<meta name="csrf-token" content="([^"]+)"', r2.text)
    csrf=m.group(1) if m else ''
print('csrf found:', bool(csrf))
headers={'X-CSRFToken':csrf} if csrf else {}
login = s.post(BASE+'/auth/login', data={'username':'admin','password':'TempPass123!','csrf_token':csrf,'submit':'Login'}, headers={**headers,'Referer':BASE+'/auth/login'})
print('login status', login.status_code)
resp = s.get(BASE+'/statistics/export/equipment', headers={'Referer':BASE+'/statistics'})
print('export status', resp.status_code, resp.headers.get('content-type'))
open('scripts/last_export_response.bin','wb').write(resp.content)
print('saved response to scripts/last_export_response.bin')
