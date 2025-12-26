import requests
from playwright.sync_api import sync_playwright
import os, json

BASE = 'http://127.0.0.1:5020'
USERNAME = 'admin'
PASSWORD = 'TestPass123!'

s = requests.Session()
r = s.get(BASE + '/auth/login')
# Extract csrf token from hidden input
import re
m = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', r.text)
if not m:
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', r.text)
csrf = m.group(1) if m else ''
print('csrf len=', len(csrf))
resp = s.post(BASE + '/auth/login', data={'csrf_token': csrf, 'username': USERNAME, 'password': PASSWORD, 'remember_me': 'y'}, allow_redirects=True)
print('login status', resp.status_code, 'url', resp.url)

# prepare cookies for playwright
cookies = []
for name, val in s.cookies.items():
    cookies.append({'name': name, 'value': val, 'domain': '127.0.0.1', 'path': '/', 'httpOnly': False, 'secure': False})

OUT = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'layout_inspection_auth.json')
res = {}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width':1280,'height':900})
    # set cookies
    try:
        context.add_cookies(cookies)
    except Exception as e:
        print('add_cookies failed', e)

    page = context.new_page()
    page.goto(BASE + '/chat', wait_until='domcontentloaded')
    page.wait_for_timeout(1000)

    # check presence
    res['has_chat_container'] = page.query_selector('.chat-container') is not None
    res['has_online_users_container'] = page.query_selector('.online-users-container') is not None
    res['conversation_count'] = page.evaluate('() => document.querySelectorAll(".conversation-item").length')
    res['html_sample'] = page.content()[:2000]

    # save screenshot
    page.screenshot(path=os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'layout_after_auth.png'), full_page=True)

    browser.close()

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print('Wrote', OUT)
print(json.dumps(res, ensure_ascii=False, indent=2))