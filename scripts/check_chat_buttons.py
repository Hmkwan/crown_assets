from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:5020'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context()
    page=c.new_page()
    errors=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    console_msgs=[]
    page.on('console', lambda m: console_msgs.append(f"{m.type}: {m.text}"))

    page.goto(BASE + '/__dev_login_admin')
    page.goto(BASE + '/chat', wait_until='networkidle')

    # click emoji
    try:
        page.click('#emojiBtn')
        # 等待 emoji-picker 渲染
        page.wait_for_selector('.emoji-btn', timeout=2000)
        page.click('.emoji-btn')
    except Exception as e:
        console_msgs.append('emoji click failed: '+str(e))

    # open conversation info
    try:
        page.click('#showInfoBtn')
        page.wait_for_timeout(300)
        # ensure modal visible
        modal = page.query_selector('#conversationInfoModal .modal-content')
        console_msgs.append('info modal visible: ' + str(bool(modal)))
    except Exception as e:
        console_msgs.append('showInfo failed: '+str(e))

    # open delete confirmation (clicking delete in modal)
    try:
        page.click('#modalDeleteBtn')
        page.wait_for_timeout(200)
        confirm_visible = page.query_selector('#confirmDeleteModal .modal-content')
        console_msgs.append('confirm delete visible: ' + str(bool(confirm_visible)))
        # close confirm modal (click cancel)
        page.click('#confirmDeleteModal .btn-secondary')
        page.wait_for_timeout(100)
    except Exception as e:
        console_msgs.append('open/close delete confirm failed: '+str(e))

    # 点击结束会话（关闭）
    try:
        page.click('#modalCloseBtn')
        page.wait_for_timeout(500)
        console_msgs.append('clicked end conversation')
    except Exception as e:
        console_msgs.append('end conversation click failed: '+str(e))

    # toggle online users
    try:
        page.click('#toggleOnlineUsersBtn')
        page.wait_for_timeout(200)
        visible = page.evaluate("() => document.querySelector('.online-users-container') && !document.querySelector('.online-users-container').classList.contains('hidden')")
        console_msgs.append('online users visible after toggle: '+str(visible))
    except Exception as e:
        console_msgs.append('toggle online failed: '+str(e))

    print('page errors:', errors)
    print('console msgs:\n', '\n'.join(console_msgs))
    b.close()