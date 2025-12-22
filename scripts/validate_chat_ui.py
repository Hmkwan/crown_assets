#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate chat UI: login, fetch conversations/messages, and connect via Socket.IO client."""
import time
import re
import requests

# Try to import python-socketio; if not available, skip socket test
try:
    import socketio
    HAS_SIO = True
except Exception:
    HAS_SIO = False

BASE = 'http://10.168.93.93:5020'
USERNAME = 'admin'
PASSWORD = 'TempPass123!'

s = requests.Session()
# Prefer getting CSRF token from the login page (ensures session cookie matches)
r = s.get(BASE + '/auth/login')
if r.status_code == 200:
    m = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', r.text)
    csrf = m.group(1) if m else ''
    print('CSRF token (from login page):', 'found' if csrf else 'not found')
    # if login page didn't contain token, fallback to chat page meta
    if not csrf:
        r2 = s.get(BASE + '/chat')
        if r2.status_code != 200:
            print('Failed to GET chat page for CSRF fallback', r2.status_code)
            raise SystemExit(1)
        m = re.search(r'<meta name="csrf-token" content="([^"]+)"', r2.text)
        csrf = m.group(1) if m else ''
        print('CSRF token (from chat page fallback):', 'found' if csrf else 'not found')
else:
    # fall back to using chat page meta if login page not reachable
    r2 = s.get(BASE + '/chat')
    if r2.status_code != 200:
        print('Failed to GET any page for CSRF', r.status_code)
        raise SystemExit(1)
    m = re.search(r'<meta name="csrf-token" content="([^"]+)"', r2.text)
    csrf = m.group(1) if m else ''
    print('CSRF token (from chat page fallback 2):', 'found' if csrf else 'not found')

# Post credentials using CSRF token as header + form field
payload = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrf_token': csrf,
    'submit': 'Login'
}
headers = {}
if csrf:
    headers['X-CSRFToken'] = csrf

headers_for_login = headers.copy() if headers else {}
headers_for_login['Referer'] = BASE + '/auth/login'
headers_for_login['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
login = s.post(BASE + '/auth/login', data=payload, headers=headers_for_login, allow_redirects=True)
print('Login status:', login.status_code)
print('Login request headers used:', headers_for_login)
print('Login response headers:', dict(login.headers))
print('Login response body snippet:', login.text[:800])
if login.history:
    print('Login followed redirects, final status', login.status_code)
else:
    print('Login response (no redirects):', login.status_code)

# Fetch chat page and read CSRF meta
r = s.get(BASE + '/chat')
if r.status_code == 200:
    if 'Socket.IO 实时通知' in r.text or 'socket.io' in r.text.lower():
        print('Chat page loaded and includes socket.io markers')
    else:
        print('Chat page loaded but socket markers not obvious')
else:
    print('Failed to load chat page', r.status_code)

# Extract csrf token from meta
m = re.search(r'<meta name="csrf-token" content="([^"]+)"', r.text)
csrf_meta = m.group(1) if m else ''
print('CSRF meta token:', 'found' if csrf_meta else 'not found')

# Print cookies for debugging
print('Session cookies:', s.cookies.get_dict())
api_headers = {}
if 'csrf_meta' in locals() and csrf_meta:
    api_headers['X-CSRFToken'] = csrf_meta
elif csrf:
    api_headers['X-CSRFToken'] = csrf
# mimic a real browser UA + referer
api_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
api_headers['Referer'] = BASE + '/chat'

conv = s.get(BASE + '/api/chat/conversations', headers=api_headers)
print('/api/chat/conversations ->', conv.status_code)
print('Conversations response headers:', conv.headers.get('content-type'))
if conv.status_code == 200:
    try:
        data = conv.json()
        print('Conversations count:', len(data.get('data', [])))
    except Exception:
        print('Conversations: parse error')
else:
    print('Conversations body:', conv.text[:200])

# If we have a conversation, try messages
first_id = None
try:
    items = conv.json().get('data', [])
    if items:
        first_id = items[0]['id']
        msgs = s.get(BASE + f'/api/chat/conversations/{first_id}/messages')
        print(f'/messages for conv {first_id} ->', msgs.status_code)
    else:
        print('No conversations found to fetch messages')
except Exception:
    print('Error parsing conversations JSON')

# Try sending a test message (requires CSRF header too)
if first_id:
    headers = {}
    if csrf_meta:
        headers['X-CSRFToken'] = csrf_meta
    payload = {'conversation_id': first_id, 'content': 'Automated test message (validate_chat_ui)'}
    send = s.post(BASE + '/api/chat/messages', json=payload, headers=headers)
    print('POST /api/chat/messages ->', send.status_code, send.text[:200])

# Attempt a Socket.IO connection using python-socketio client
if HAS_SIO:
    print('python-socketio available; attempting Socket.IO connection...')
    # Grab session cookie value
    cookie = None
    for k, v in s.cookies.items():
        if k == 'session':
            cookie = f'session={v}'
            break
    sio = socketio.Client(logger=False, engineio_logger=False)

    @sio.event
    def connect():
        print('SocketIO connected')

    @sio.event
    def disconnect():
        print('SocketIO disconnected')

    try:
        sio.connect(BASE, headers={'Cookie': cookie} if cookie else None, transports=['websocket'])
        time.sleep(2)
        sio.disconnect()
    except Exception as e:
        print('SocketIO connection failed:', e)
else:
    print('python-socketio not installed; skip realtime connect test')

print('Validation script completed')
