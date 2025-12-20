from app import create_app, db
from app.models import User

class RunConfig:
    pass

app = create_app()
# Enable testing fallback to allow login without CSRF
app.config['TESTING'] = True

with app.app_context():
    c = app.test_client()
    # Attempt login via testing fallback
    resp = c.post('/auth/login', data={'username':'admin','password':'admin123'}, follow_redirects=True)
    print('login status', resp.status_code)
    a = c.get('/announcements')
    open('scripts/announcements_snapshot.html','w',encoding='utf-8').write(a.get_data(as_text=True))
    print('/announcements fetched, status', a.status_code)
    d = c.get('/announcements/4')
    open('scripts/announcement_4_snapshot.html','w',encoding='utf-8').write(d.get_data(as_text=True))
    print('/announcements/4 fetched, status', d.status_code)
    # Print small fragments
    s = a.get_data(as_text=True)
    start = s.find('<div class="list-group">')
    if start != -1:
        print('\n--- Announcement list fragment ---\n')
        print(s[start:start+800])
    else:
        print('list-group not found in announcements')
    s2 = d.get_data(as_text=True)
    start2 = s2.find('<div class="announcement-meta')
    if start2 != -1:
        print('\n--- Announcement detail meta fragment ---\n')
        print(s2[start2:start2+400])
    else:
        print('announcement meta not found')
