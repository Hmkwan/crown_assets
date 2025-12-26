from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:5020'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context(viewport={'width':1366,'height':900})
    page=c.new_page()
    page.goto(BASE + '/__dev_login_admin')
    page.goto(BASE + '/chat', wait_until='networkidle')
    def info(selector):
        el = page.query_selector(selector)
        if not el:
            print(selector, 'NOT FOUND')
            return
        box = el.bounding_box()
        print(selector, 'box=', box, 'visible=', el.is_visible())
    for sel in ['#emojiBtn','#showInfoBtn','#toggleOnlineUsersBtn','#modalDeleteBtn','#fileUploadBtn','#sendBtn']:
        info(sel)
    # show HTML of header
    header = page.query_selector('#chatHeader')
    print('chatHeader exists:', bool(header))
    if header:
        print('header html snippet:', header.inner_html()[:400])
    b.close()