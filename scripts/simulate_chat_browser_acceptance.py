#!/usr/bin/env python3
"""Simulate browser acceptance using Flask test client + SocketIO test client
Produces: chat_page_authenticated.html and acceptance_results.txt
"""
import sys
import pathlib
import tempfile
import os
import traceback
# ensure project root is in sys.path
root = pathlib.Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
try:
    from app import create_app, db
    from app.chat_models import ChatAttachment
except Exception as e:
    print('Import error in simulate script:', e)
    traceback.print_exc()
    raise

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def run():
    app = create_app(TestConfig)
    temp_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = temp_dir

    results = []

    with app.app_context():
        db.drop_all()
        db.create_all()
        client = app.test_client()

        # Create users
        from app.models import User
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        u2 = User(username='tester2', email='t2@example.com', role='user')
        u2.set_password('test123')
        db.session.add_all([admin, u2])
        db.session.commit()

        # Login via session transaction (bypass form)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        results.append('Logged in as admin (session set)')

        # Fetch /chat HTML
        r = client.get('/chat')
        results.append(f'/chat HTML status: {r.status_code}')
        html_path = os.path.join(os.getcwd(), 'chat_page_authenticated.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(r.get_data(as_text=True))
        results.append(f'Wrote HTML snapshot to {html_path}')

        # Create a group conversation
        create_resp = client.post('/api/chat/conversations', json={
            'type': 'group',
            'participant_ids': [u2.id],
            'name': 'Acceptance Group'
        })
        results.append(f'Create conv status: {create_resp.status_code} json: {create_resp.get_json()}')
        conv_id = create_resp.get_json()['conversation']['id']

        # Upload an attachment
        from io import BytesIO
        file_content = b'Test acceptance file'
        data = {
            'conversation_id': str(conv_id)
        }
        file_tuple = (BytesIO(file_content), 'accept.txt')
        resp = client.post('/api/chat/attachments', data={'file': file_tuple, 'conversation_id': conv_id}, content_type='multipart/form-data')
        results.append(f'Upload attachment status: {resp.status_code} json: {resp.get_json()}')
        att_info = resp.get_json().get('attachment')
        att_id = resp.get_json().get('attachment_id')

        # Use socketio test client to simulate WS (use app.socketio)
        sio = app.socketio
        if sio is None:
            results.append('SocketIO not initialized in app; skipping WS tests')
        else:
            try:
                sio_client = sio.test_client(app, flask_test_client=client)
                connected = sio_client.is_connected()
                results.append(f'SocketIO test client connected: {connected}')

                # Join conversation
                sio_client.emit('join_conversation', {'conversation_id': conv_id})
                # send a message with attachment through WS
                sio_client.emit('send_message', {'conversation_id': conv_id, 'content': 'Hello from WS', 'message_type': 'text'})

                # Wait for events
                import time
                time.sleep(0.5)

                received = sio_client.get_received()
                results.append(f'SocketIO events received: {received}')
            except Exception as e:
                results.append(f'SocketIO test client unavailable or failed: {e}')




        # Now upload image and send message referencing attachment via /api/chat/messages
        send_resp = client.post('/api/chat/messages', json={
            'conversation_id': conv_id,
            'content': 'Here is a file',
            'attachment_ids': [att_id]
        })
        results.append(f'Send message (attach) status: {send_resp.status_code} json: {send_resp.get_json()}')

        # fetch messages
        msgs = client.get(f'/api/chat/conversations/{conv_id}/messages')
        results.append(f'Get messages status: {msgs.status_code} count: {len(msgs.get_json().get("messages", []))}')
        results.append(f'Messages sample: {msgs.get_json()}')

        # Edit group name
        patch = client.patch(f'/api/chat/conversations/{conv_id}', json={'name': 'Renamed By Acceptance'})
        results.append(f'Patch conv status: {patch.status_code} json: {patch.get_json()}')

        # Save results
        out = os.path.join(os.getcwd(), 'acceptance_results.txt')
        with open(out, 'w', encoding='utf-8') as f:
            for line in results:
                f.write(line + '\n')

        print('Acceptance simulation complete. Outputs:')
        print(' -', html_path)
        print(' -', out)

if __name__ == '__main__':
    run()