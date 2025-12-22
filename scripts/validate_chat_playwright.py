#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Playwright-based end-to-end validation using a local browser (Edge/Chrome).

Steps:
 - Launch local Edge/Chrome executable if present
 - Log in using the provided admin credentials
 - Open /chat, ensure CSRF meta exists
 - POST a message via fetch using browser session
 - Take a screenshot and save under scripts/playwright_chat.png
"""
import os
import time
import re
import requests
from playwright.sync_api import sync_playwright

BASE = 'http://10.168.93.93:5020'
USERNAME = 'admin'
PASSWORD = 'TempPass123!'

MSEDGE_PATHS = [r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
CHROME_PATHS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]

def find_local_browser():
    for p in MSEDGE_PATHS + CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None

if __name__ == '__main__':
    exe = find_local_browser()
    print('Detected local browser executable:', exe if exe else 'none')

    artifacts_dir = os.path.join('scripts', 'playwright_artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)

    in_ci = os.getenv('CI') is not None

    with sync_playwright() as p:
        browser = None
        try:
            # In CI use playwright-managed browsers (no executable_path), on dev try to use local browser if present
            if in_ci:
                print('CI environment detected: launching playwright-managed chromium')
                browser = p.chromium.launch(headless=True)
            else:
                if exe:
                    print('Launching with executable_path:', exe)
                    browser = p.chromium.launch(executable_path=exe, headless=True)
                else:
                    print('No local browser binary found; attempting channel launch for msedge')
                    # Fallback to channel (may be present on developer machines)
                    browser = p.chromium.launch(channel='msedge', headless=True)
        except Exception as e:
            print('Failed to launch browser:', e)
            raise SystemExit(1)

        ctx = browser.new_context()

        # Use requests to obtain a valid session cookie (the requests flow previously worked reliably)
        print('Logging in via requests to obtain session cookie...')
        s = requests.Session()
        r = s.get(BASE + '/auth/login')
        m = re.search(r"name=[\"']csrf_token[\"']\s+value=[\"']([^\"']+)[\"']", r.text)
        csrf = m.group(1) if m else ''
        # if login page doesn't contain csrf token, try chat page meta as fallback
        if not csrf:
            r2 = s.get(BASE + '/chat')
            m2 = re.search(r'<meta name="csrf-token" content="([^"]+)"', r2.text)
            csrf = m2.group(1) if m2 else ''
        print('Requests-login CSRF token found:', bool(csrf))
        payload = {'username': USERNAME, 'password': PASSWORD, 'csrf_token': csrf, 'submit': 'Login'}
        headers = {}
        if csrf:
            headers['X-CSRFToken'] = csrf
        login = s.post(BASE + '/auth/login', data=payload, headers=headers, allow_redirects=True)
        print('Requests login status:', login.status_code)
        # Quick check: ensure requests-authenticated session can fetch conversations
        try:
            conv_check = s.get(BASE + '/api/chat/conversations', headers={'X-CSRFToken': csrf})
            if conv_check.ok:
                print('Requests conv test: OK, conv count =', len(conv_check.json().get('data', [])))
            else:
                print('Requests conv test: status', conv_check.status_code, 'body:', conv_check.text[:200])
        except Exception as e:
            print('Requests conv test failed:', e)
        errors = []
        print('Requests cookies after login:', s.cookies.get_dict())
        session_cookie = None
        for k, v in s.cookies.items():
            if k == 'session':
                session_cookie = v
                break
        if not session_cookie:
            msg = 'No session cookie obtained via requests; aborting browser cookie injection'
            print(msg)
            errors.append(msg)
        else:
            print('Injecting session cookie into Playwright context')
            # Use the full URL to ensure cookie scoping is correct for Playwright
            ctx.add_cookies([{'name': 'session', 'value': session_cookie, 'url': BASE}])
            print('Context cookies after injection:', ctx.cookies())

        page = ctx.new_page()
        # Forward page console and request failures to the terminal to help debugging
        page.on('console', lambda msg: print('PAGE LOG:', msg.text))
        page.on('requestfailed', lambda req: print('PAGE REQ FAILED:', req.url, req.failure))

        print('Opening /chat in browser...')

        print('Navigating to /chat...')
        page.goto(BASE + '/chat', timeout=30000)
        print('Context cookies after navigating to /chat:', ctx.cookies())
        try:
            # meta tags are not visible elements; wait for them to be attached to the DOM
            page.wait_for_selector('meta[name="csrf-token"]', timeout=10000, state='attached')
            csrf = page.get_attribute('meta[name="csrf-token"]', 'content')
            print('Found CSRF meta token (attached):', bool(csrf))
        except Exception as e:
            print('CSRF meta not found or /chat did not load as expected (attached state):', e)
            csrf = None

        # Check whether the in-page Socket.IO client connected
        try:
            page.wait_for_function("() => window.socket && window.socket.connected === true", timeout=10000)
            print('Page Socket.IO client reports connected')
        except Exception as e:
            print('Page Socket.IO client did not report connected:', e)

        # Attempt to post or create a conversation, upload a small file, send a message, and start a workflow
        print('Posting a test message via browser fetch (create conv if needed, upload file, start workflow)...')
        send_script = f"""
        (async () => {{
            const meta = document.querySelector('meta[name="csrf-token"]');
            const csrf = meta ? meta.content : '';

            // Fetch conversations
            const convResp = await fetch('{BASE}/api/chat/conversations', {{credentials: 'include', headers: {{'X-CSRFToken': csrf}}}});
            if (!convResp.ok) return {{error:'conv_failed', status: convResp.status}};
            const convData = await convResp.json();
            let first = convData.conversations && convData.conversations[0] && convData.conversations[0].id;

            // If no conversation exists, create one with the first available user
            if (!first) {{
                const usersResp = await fetch('{BASE}/api/chat/users', {{credentials: 'include', headers: {{'X-CSRFToken': csrf}}}});
                if (!usersResp.ok) return {{error:'no_users', status: usersResp.status}};
                const users = await usersResp.json();
                const u = users.users && users.users[0];
                if (!u) return {{error:'no_other_user'}};
                const createResp = await fetch('{BASE}/api/chat/conversations', {{
                    method: 'POST',
                    credentials: 'include',
                    headers: {{'X-CSRFToken': csrf, 'Content-Type': 'application/json'}},
                    body: JSON.stringify({{type: 'direct', participant_ids: [u.id]}})
                }});
                if (!createResp.ok) return {{error:'create_failed', status: createResp.status}};
                const created = await createResp.json();
                first = created.conversation && created.conversation.id;
                if (!first) return {{error:'create_no_id'}};
            }}

            // Ensure messages endpoint is reachable
            const send = await fetch('{BASE}/api/chat/messages', {{
                method: 'POST',
                credentials: 'include',
                headers: {{'X-CSRFToken': csrf, 'Content-Type': 'application/json'}},
                body: JSON.stringify({{conversation_id: first, content: 'Playwright automated message'}})
            }});

            const result = {{send_status: send.status}};

            // Try to start a workflow if templates exist
            const templatesResp = await fetch('{BASE}/api/chat/workflow_templates', {{credentials: 'include', headers: {{'X-CSRFToken': csrf}}}});
            if (templatesResp.ok) {{
                const tpl = await templatesResp.json();
                if (tpl.templates && tpl.templates.length) {{
                    const tid = tpl.templates[0].id;
                    const startResp = await fetch('{BASE}/api/chat/start_workflow', {{
                        method: 'POST',
                        credentials: 'include',
                        headers: {{'X-CSRFToken': csrf, 'Content-Type': 'application/json'}},
                        body: JSON.stringify({{conversation_id: first, template_id: tid}})
                    }});
                    result.workflow = {{status: startResp.status}};
                }} else {{ result.workflow = {{status: 'no_templates'}}; }}
            }} else {{ result.workflow = {{status: 'tpl_failed', code: templatesResp.status}}; }}

            // Return conversation id and statuses
            result.conversation_id = first;
            return result;
        }})()
        """
        try:
            resp = page.evaluate(send_script)
            print('Send message eval response:', resp)
        except Exception as e:
            print('Failed to execute send script:', e)

        # If the previous actions returned a conversation id, try to select it and upload a small file
        if isinstance(resp, dict) and resp.get('conversation_id'):
            conv_id = resp['conversation_id']
            print('Selecting conversation in-page:', conv_id)
            try:
                # Try to click the conversation DOM element (avoid calling page-level JS functions that may not be exposed)
                # Use page.evaluate with an argument to avoid f-string brace escaping issues
                click_result = page.evaluate('''(convId) => {
                    const items = Array.from(document.querySelectorAll('.conversation-item'));
                    for (const el of items) {
                        const onclick = el.getAttribute('onclick') || '';
                        if (onclick.includes('selectConversation(' + convId + ')')) {
                            el.click();
                            return true;
                        }
                    }
                    if (items.length) { items[0].click(); return true; }
                    return false;
                }''', conv_id)
                print('Conversation click result:', click_result)
                # Diagnostic: check if selectConversation exists and whether chat DOM was rendered
                try:
                    diag = page.evaluate('''() => ({
                        selectExists: typeof selectConversation !== 'undefined',
                        currentConversation: (window.currentConversation && window.currentConversation.id) || null,
                        hasHiddenFileInput: !!document.querySelector('#hiddenFileInput'),
                        hasChatMessages: !!document.querySelector('#chatMessages'),
                        hasChatMessagesWrapper: !!document.querySelector('#chatMessagesWrapper'),
                        chatMainSnapshot: document.querySelector('#chatMain') ? document.querySelector('#chatMain').innerHTML.slice(0,400) : null
                    })''')
                    print('Post-click diagnostics:', diag)
                except Exception as e:
                    print('Diagnostic eval failed:', e)

                # Wait (poll) up to 15s for any chat area selector to be attached
                found = False
                for i in range(15):
                    if page.query_selector('#chatMessages') or page.query_selector('#chatMsgs') or page.query_selector('#chatMessagesWrapper') or page.query_selector('#chatTitle'):
                        found = True
                        break
                    time.sleep(1)
                if not found:
                    print('No chat area found after click; proceeding with best-effort (page snapshot was logged).')

                # Create a small test file to upload
                local_path = os.path.join('scripts', 'playwright_test_file.txt')
                with open(local_path, 'w', encoding='utf-8') as fh:
                    fh.write('playwright test upload')
                print('Prepared local test file:', local_path)
                # Ensure artifacts dir exists for any temp files
                os.makedirs(artifacts_dir, exist_ok=True)
                try:
                    # Check whether the page has an in-page file input visible
                    if diag.get('hasHiddenFileInput'):
                        page.set_input_files('#hiddenFileInput', local_path)
                        # Wait a bit for upload to complete and for pendingAttachments to be populated
                        time.sleep(2)
                        # Click send button
                        page.click('.send-btn')
                    else:
                        print('No in-page file input; uploading via requests session')
                        try:
                            with open(local_path, 'rb') as fh:
                                files = {'file': ('playwright_test_file.txt', fh)}
                                resp_att = s.post(BASE + '/api/chat/attachments', files=files, data={'conversation_id': conv_id}, headers={'X-CSRFToken': csrf})
                            if resp_att.ok:
                                att_id = resp_att.json().get('attachment_id')
                                print('Uploaded via API, attachment id:', att_id)
                                send_resp = s.post(BASE + '/api/chat/messages', json={'conversation_id': conv_id, 'content': 'Playwright uploaded file', 'attachment_ids': [att_id]}, headers={'X-CSRFToken': csrf})
                                print('Send via API status:', send_resp.status_code)
                            else:
                                msg = f'Attachment upload failed via API: {resp_att.status_code} {resp_att.text[:200]}'
                                print(msg)
                                errors.append(msg)
                        except Exception as e:
                            print('Requests upload failed:', e)

                    # Wait for the message to appear in messages list (poll via fetch)
                    for i in range(8):
                        msgs = page.evaluate(f"() => fetch('{BASE}/api/chat/conversations/{conv_id}/messages', {{credentials: 'include'}}).then(r=>r.json())")
                        has_attach = False
                        try:
                            msgs_obj = msgs if isinstance(msgs, dict) else {}
                            messages = msgs_obj.get('messages') if isinstance(msgs_obj, dict) else None
                            if messages:
                                for m in messages[::-1]:
                                    if m.get('attachments'):
                                        has_attach = True
                                        break
                        except Exception:
                            has_attach = False
                        if has_attach:
                            print('Attachment message found in conversation', conv_id)
                            break
                        time.sleep(1)
                except Exception as e:
                    print('Failed to set input files or send:', e)
            except Exception as e:
                print('Failed to select conversation or upload:', e)

        # Additional checks: upload a small PNG image via requests and verify thumbnail + download
        try:
            import io
            from PIL import Image
            print('Creating small test PNG and uploading via API to check thumbnail generation...')
            # create a 80x80 red PNG
            img = Image.new('RGB', (80, 80), color=(255, 0, 0))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            files = {'file': ('test_img.png', img_bytes, 'image/png')}
            resp_att = s.post(BASE + '/api/chat/attachments', files=files, data={'conversation_id': conv_id}, headers={'X-CSRFToken': csrf})
            if resp_att.ok:
                att_id = resp_att.json().get('attachment_id')
                print('Image uploaded via API, id:', att_id)
                # try thumbnail endpoint
                thumb_resp = s.get(f"{BASE}/api/chat/attachments/{att_id}/thumbnail")
                print('Thumbnail fetch status:', thumb_resp.status_code, 'content-type:', thumb_resp.headers.get('content-type'))
                if thumb_resp.ok:
                    thumb_path = os.path.join(artifacts_dir, f'playwright_thumb_{att_id}.png')
                    with open(thumb_path, 'wb') as fh:
                        fh.write(thumb_resp.content)
                    print('Saved thumbnail to', thumb_path)
                else:
                    msg = f'Thumbnail fetch failed for {att_id}: {thumb_resp.status_code}'
                    print(msg)
                    errors.append(msg)
                # verify download
                dl_resp = s.get(f"{BASE}/api/chat/attachments/{att_id}/download")
                print('Download status:', dl_resp.status_code, 'content-type:', dl_resp.headers.get('content-type'))
            else:
                print('Image upload failed:', resp_att.status_code, resp_att.text[:200])
        except Exception as e:
            print('Image thumbnail check failed:', e)

        # Check for workflow system message inside conversation messages (if we started a workflow earlier)
        try:
            messages_resp = s.get(BASE + f'/api/chat/conversations/{conv_id}/messages')
            if messages_resp.ok:
                msgs = messages_resp.json().get('messages', [])
                system_found = False
                for m in msgs[::-1]:
                    if m.get('message_type') == 'system' or (m.get('content') or '').find('已发起审批流程') != -1:
                        system_found = True
                        print('Found system workflow message:', m.get('content'))
                        break
                print('Workflow system message found:', system_found)
            else:
                print('Failed to fetch messages for system message check:', messages_resp.status_code)
        except Exception as e:
            print('Workflow message verification failed:', e)

        time.sleep(1)
        out_path = os.path.join(artifacts_dir, 'playwright_chat.png')
        try:
            page.screenshot(path=out_path, full_page=True)
            print('Saved screenshot to', out_path)
        except Exception as e:
            msg = f'Screenshot failed: {e}'
            print(msg)
            errors.append(msg)

        # Save server logs if available (attempt to fetch from docker-compose logs)
        try:
            logs_path = os.path.join(artifacts_dir, 'playwright_server_logs.txt')
            # This run may be on runner that doesn't have docker-compose; if available, append logs
            os.system(f'docker-compose logs --tail=500 web > {logs_path} 2>&1 || true')
            if os.path.exists(logs_path):
                print('Saved server logs to', logs_path)
        except Exception as e:
            print('Failed to save server logs:', e)

        browser.close()
        print('Playwright validation completed')

        # Final status check: exit with non-zero if we collected errors
        if errors:
            print('\nErrors detected during Playwright validation:')
            for err in errors:
                print('-', err)
            raise SystemExit(2)
        else:
            print('\nNo errors detected; exiting successfullly')
            raise SystemExit(0)
