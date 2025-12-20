import re
import requests

base = 'http://localhost:5020'
s = requests.Session()
# Get login page
r = s.get(base + '/auth/login')
if r.status_code != 200:
    print('GET login failed', r.status_code)
    exit(1)

m = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', r.text)
if not m:
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', r.text)
csrf = m.group(1) if m else ''
print('csrf=', csrf)

payload = {
    'username': 'admin',
    'password': 'admin123',
    'csrf_token': csrf
}
# post to login
r2 = s.post(base + '/auth/login', data=payload, allow_redirects=True)
print('login status', r2.status_code, r2.url)

r3 = s.get(base + '/announcements')
print('announcements status', r3.status_code)
out_path = 'scripts/output_announcements.html'
open(out_path, 'w', encoding='utf-8').write(r3.text)
print('saved', out_path)
# print key fragments: first list-group
import sys
if '<div class="list-group">' in r3.text:
    part = r3.text.split('<div class="list-group">',1)[1].split('</div>',1)[0]
    print('\n-- fragment --\n')
    print(part[:1000])
else:
    print('list-group not found')
