from app import create_app
from app.models import Announcement
app = create_app()
with app.app_context():
    a = Announcement.query.get(11)
    if not a:
        print('Announcement not found')
    else:
        print('CONTENT:', repr(a.content))
        print('PUBLISH_TIME (raw):', a.publish_time)
        print('PUBLISH_TIME (display):', app.jinja_env.filters['format_dt'](a.publish_time, '%Y-%m-%d %H:%M'))
