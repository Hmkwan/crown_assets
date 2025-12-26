from app import create_app
app = create_app()
with app.test_request_context('/'):
    from types import SimpleNamespace
    fake_user = SimpleNamespace(id=1, is_authenticated=True)
    html = app.jinja_env.get_or_select_template('chat.html').render(current_user=fake_user)
    open('rendered_chat_preview.html','w',encoding='utf-8').write(html)
    print('Rendered length', len(html))