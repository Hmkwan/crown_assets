from playwright.sync_api import sync_playwright
import requests
BASE='http://127.0.0.1:5020'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context(viewport={'width':1366,'height':900})
    page=c.new_page()
    page.goto(BASE + '/__dev_login_admin')
    page.goto(BASE + '/chat', wait_until='domcontentloaded')
    hrefs = page.evaluate('() => Array.from(document.querySelectorAll("link[rel=stylesheet]"), l => l.href)')
    css_present = any('chat_modern.css' in h for h in hrefs)
    display = page.evaluate('() => { const el = document.querySelector(".chat-container"); return el?getComputedStyle(el).display:null }')
    grid = page.evaluate('() => { const el = document.querySelector(".chat-container"); return el?getComputedStyle(el).getPropertyValue("grid-template-columns"):null }')
    print('stylesheets count', len(hrefs))
    for h in hrefs:
        print('-', h)
    print('chat_modern.css present?', css_present)
    print('chat-container display', display, 'grid-template-columns', grid)
    for h in hrefs:
        if 'chat_modern.css' in h:
            r=requests.get(h)
            print('chat_modern.css status', r.status_code, 'len', len(r.text))
    b.close()