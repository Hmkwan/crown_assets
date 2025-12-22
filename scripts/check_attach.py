import requests
from bs4 import BeautifulSoup
s=requests.Session()
base='http://localhost:5020'
# login
r=s.get(base+'/auth/login')
soup=BeautifulSoup(r.text,'html.parser')
token=soup.find('input',{'name':'csrf_token'})
csrf=token['value'] if token else None
payload={'username':'admin','password':'admin','csrf_token':csrf}
r=s.post(base+'/auth/login',data=payload,allow_redirects=False)
print('login',r.status_code)
for aid in (6,8,9,10):
    t=s.get(base+f'/api/chat/attachments/{aid}/thumbnail')
    d=s.get(base+f'/api/chat/attachments/{aid}/download')
    print(aid,'thumb',t.status_code,t.headers.get('content-type'))
    print(aid,'download',d.status_code,d.headers.get('content-type'))
