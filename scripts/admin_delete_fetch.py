from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:5020'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    page=b.new_context().new_page()
    page.goto(BASE + '/__dev_login_admin')
    page.goto(BASE + '/chat', wait_until='networkidle')
    page.wait_for_timeout(500)
    res = page.evaluate('''async () => {
        const item = document.querySelector('.conversation-item');
        if (!item) return {status:0, body:'no item'};
        const id = item.dataset.id;
        try {
            const r = await fetch('/api/chat/admin/conversations/' + id, { method: 'DELETE' });
            const txt = await r.text();
            return {status: r.status, body: txt};
        } catch (e) { return {status:0, body: String(e)} }
    }''')
    print('admin delete response', res)
    b.close()