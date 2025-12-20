import re
s=open('login.html',encoding='utf-8').read()
m=re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', s)
if not m:
    m=re.search(r'name="csrf_token"\s+value="([^"]+)"', s)
print(m.group(1) if m else '')
