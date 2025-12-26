from playwright.sync_api import sync_playwright
import os, json
BASE = 'http://127.0.0.1:5020'
OUT = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'dev_login_inspection.json')
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width':1366,'height':900})
    page = context.new_page()
    # use dev auto-login
    r = page.goto(BASE + '/__dev_login_admin')
    # after redirect, go to chat
    page.goto(BASE + '/chat', wait_until='domcontentloaded')
    page.wait_for_timeout(1000)
    def q(sel):
        return page.query_selector(sel) is not None
    res = {
        'url': page.url,
        'has_chat_container': q('.chat-container'),
        'has_chat_sidebar': q('.chat-sidebar'),
        'has_chat_main': q('.chat-main'),
        'has_online_panel': q('.online-users-container'),
        'chat_display': page.evaluate('() => { const el = document.querySelector(".chat-container"); return el?window.getComputedStyle(el).display:null }'),
        'chat_grid_cols': page.evaluate('() => { const el = document.querySelector(".chat-container"); return el?window.getComputedStyle(el).getPropertyValue("grid-template-columns"):null }'),
        'chat_html_snippet': page.content()[:2000]
    }
    # screenshot
    page.screenshot(path=os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'dev_login_layout.png'), full_page=True)
    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(res,f,ensure_ascii=False,indent=2)
    print('Wrote', OUT)
    print(json.dumps(res,ensure_ascii=False,indent=2))
    browser.close()