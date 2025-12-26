from playwright.sync_api import sync_playwright
import json, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'layout_inspection.json')
BASE = 'http://127.0.0.1:5020'

result = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width':1280,'height':900})
    page = context.new_page()

    page.goto(f"{BASE}/auth/login", wait_until='domcontentloaded')
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'TestPass123!')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    page.goto(f"{BASE}/chat", wait_until='domcontentloaded')

    def eval_safe(expr):
        try:
            return page.evaluate(expr)
        except Exception as e:
            return {'error': str(e)}

    result['innerWidth'] = page.evaluate('() => window.innerWidth')
    result['match_max_768'] = page.evaluate('() => window.matchMedia("(max-width: 768px)").matches')

    # Existence
    result['has_chat_container'] = page.query_selector('.chat-container') is not None
    result['has_online_users_container'] = page.query_selector('.online-users-container') is not None

    # Classes
    result['online_classes'] = page.evaluate('() => { const el = document.querySelector(".online-users-container"); return el ? Array.from(el.classList) : null }')

    # Computed styles
    result['chat_display'] = page.evaluate('() => { const el = document.querySelector(".chat-container"); return el ? window.getComputedStyle(el).display : null }')
    result['chat_grid_columns'] = page.evaluate('() => { const el = document.querySelector(".chat-container"); return el ? window.getComputedStyle(el).getPropertyValue("grid-template-columns") : null }')
    result['online_display'] = page.evaluate('() => { const el = document.querySelector(".online-users-container"); return el ? window.getComputedStyle(el).display : null }')
    result['online_bounds'] = page.evaluate('() => { const el = document.querySelector(".online-users-container"); if(!el) return null; const r = el.getBoundingClientRect(); return {top:r.top,left:r.left,width:r.width,height:r.height}; }')

    # Check if icon font applied
    result['first_icon'] = page.evaluate('() => { const i = document.querySelector(".conversation-list-header i, .chat-empty i, .toolbar-btn i"); if(!i) return null; const cs = window.getComputedStyle(i); return {tag: i.tagName, class: i.className, fontFamily: cs.getPropertyValue("font-family"), width: cs.getPropertyValue("width"), display: cs.getPropertyValue("display")}; }')

    # conversation items count and HTML preview
    result['conversation_count'] = page.evaluate('() => document.querySelectorAll(".conversation-item").length')
    result['conversation_sample'] = page.evaluate('() => { const el = document.querySelector(".conversation-item"); return el ? el.innerText.slice(0,200) : null }')

    # Any computed styles preventing layout (e.g., chat-window display:none)
    result['chat_window_display'] = page.evaluate('() => { const el = document.querySelector(".chat-window"); return el ? window.getComputedStyle(el).display : null }')

    # Save screenshot for visual check
    page.screenshot(path=os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'layout_inspect.png'), full_page=True)

    browser.close()

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('Done. Wrote', OUT)
print(json.dumps(result, ensure_ascii=False, indent=2))