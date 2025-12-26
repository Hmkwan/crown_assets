import requests
s = requests.Session()
base='http://127.0.0.1:5020'
r = s.get(base + '/api/chat/conversations')
print('status', r.status_code)
if r.ok:
    convs = r.json().get('conversations', [])
    if convs:
        cid = convs[0]['id']
        print('trying admin delete', cid)
        resp = s.delete(base + f'/api/chat/admin/conversations/{cid}')
        print('delete status', resp.status_code, resp.text[:400])
    else:
        print('no conversations')
else:
    print('GET convs failed', r.text)
