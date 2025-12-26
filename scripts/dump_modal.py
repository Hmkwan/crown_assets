from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:5020'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    page=b.new_context().new_page()
    page.goto(BASE + '/__dev_login_admin')
    page.goto(BASE + '/chat', wait_until='networkidle')
    page.click('#showInfoBtn')
    page.wait_for_timeout(200)
    content = page.evaluate("() => document.getElementById('conversationInfoModal').innerHTML")
    print(content[:1000])
    b.close()