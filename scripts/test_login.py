from app import create_app, db

app = create_app()
# 启用 TESTING 以允许没有 CSRF 的表单回退认证
app.config['TESTING'] = True
with app.test_client() as c:
    rv = c.post('/auth/login', data={'username':'admin','password':'admin123'}, follow_redirects=True)
    print('状态码:', rv.status_code)
    data = rv.get_data(as_text=True)
    # 打印是否包含某些关键字帮助判断登录是否成功
    indicators = ['管理员仪表板', '首页', '欢迎', '登出', '用户登录', '登录']
    found = [k for k in indicators if k in data]
    print('命中关键字:', found)
    # 打印响应前 800 字符以供快速查看
    print('响应片段:\n', data[:800])
