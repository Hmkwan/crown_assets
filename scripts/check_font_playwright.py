from playwright.sync_api import sync_playwright
import sys
BASE='http://127.0.0.1:5020'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context(viewport={'width':1366,'height':900})
    page=c.new_page()
    failed=[]
    def onrequestfailed(request):
        # request.failure can be None, a string, or an object with error_text
        failure = getattr(request, 'failure', None)
        if failure is None:
            failure_text = 'unknown'
        elif isinstance(failure, str):
            failure_text = failure
        else:
            failure_text = getattr(failure, 'error_text', str(failure))
        failed.append({'url': request.url, 'failure': failure_text})
    page.on('requestfailed', onrequestfailed)
    # block CDN
    page.route('**/cdnjs.cloudflare.com/**', lambda route: route.abort())
    page.goto(BASE + '/__dev_login_admin')
    page.goto(BASE + '/chat', wait_until='domcontentloaded')
    page.wait_for_timeout(1000)
    hrefs = page.evaluate('() => Array.from(document.styleSheets).map(s => s.href)')
    print('stylesheets total:', len(hrefs))
    for h in hrefs:
        print('-', h)
    # create a test element
    page.evaluate("() => { const el=document.createElement('i'); el.className='fas fa-smile test-fa'; el.style.position='absolute'; el.style.left='0'; el.style.top='0'; document.body.appendChild(el);} ")
    fam = page.evaluate("() => getComputedStyle(document.querySelector('.test-fa')).getPropertyValue('font-family')")
    print('computed font-family for .test-fa ->', fam)
    print('request failures:', failed)
    b.close()