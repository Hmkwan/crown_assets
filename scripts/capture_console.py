from playwright.sync_api import sync_playwright
import time
import json
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'artifacts')
os.makedirs(OUT_DIR, exist_ok=True)

CONSOLE_LOG = os.path.join(OUT_DIR, 'playwright_console.log')
PAGE_ERRORS = os.path.join(OUT_DIR, 'playwright_errors.log')
REQUEST_FAILS = os.path.join(OUT_DIR, 'playwright_request_fails.log')
SCREENSHOT = os.path.join(OUT_DIR, 'chat_console.png')
HTML = os.path.join(OUT_DIR, 'chat_after_login.html')

USERNAME = 'admin'
PASSWORD = 'TestPass123!'
BASE = 'http://127.0.0.1:5020'

console_entries = []
page_errors = []
request_fails = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width':1280,'height':900})
    page = context.new_page()

    def on_console(msg):
        try:
            entry = {'type': msg.type, 'text': msg.text, 'location': msg.location}
        except Exception:
            entry = {'type': msg.type, 'text': msg.text}
        console_entries.append(entry)

    def on_page_error(exc):
        page_errors.append(str(exc))

    def on_request_failed(request):
        request_fails.append({'url': request.url, 'method': request.method, 'failure': str(request.failure)})

    page.on('console', on_console)
    page.on('pageerror', on_page_error)
    page.on('requestfailed', on_request_failed)

    # Go to login
    page.goto(f"{BASE}/auth/login", wait_until='domcontentloaded')

    # Fill and submit
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('input[type="submit"]')

    # Wait navigation
    try:
        page.wait_for_url(f"{BASE}/", timeout=5000)
    except Exception:
        # may redirect back to chat on next
        pass

    # Navigate to chat
    page.goto(f"{BASE}/chat", wait_until='domcontentloaded')

    # Wait for chat to render
    try:
        page.wait_for_selector('#conversationItems', timeout=5000)
    except Exception:
        pass

    # allow some JS activity
    time.sleep(2)

    # save html
    open(HTML, 'w', encoding='utf-8').write(page.content())

    # screenshot
    page.screenshot(path=SCREENSHOT, full_page=True)

    # write logs
    with open(CONSOLE_LOG, 'w', encoding='utf-8') as f:
        json.dump(console_entries, f, ensure_ascii=False, indent=2)

    with open(PAGE_ERRORS, 'w', encoding='utf-8') as f:
        json.dump(page_errors, f, ensure_ascii=False, indent=2)

    with open(REQUEST_FAILS, 'w', encoding='utf-8') as f:
        json.dump(request_fails, f, ensure_ascii=False, indent=2)

    print('Console messages:', len(console_entries))
    print('Page errors:', len(page_errors))
    print('Request failures:', len(request_fails))

    browser.close()
