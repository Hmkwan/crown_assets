from app import create_app
from app import db
from app.models import User, Announcement
from app.services.announcement_service import create_announcement_from_form

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    data = {'title':'TZ测试','content':'<p>tz test</p>','type':'notice','priority':'normal','is_pinned':'0','is_active':'1','publish_time':'2025-12-20T09:30'}
    ann = create_announcement_from_form(data, [], user)
    print('created', ann.id, ann.title, 'publish_time(DB):', ann.publish_time)
    print('formatted:', app.jinja_env.filters['format_dt'](ann.publish_time, '%Y-%m-%d %H:%M'))
