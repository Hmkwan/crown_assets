import sys
from app import create_app

app = create_app()
# 启用测试回退路径，确保 auth 路由在测试时允许简化验证
app.config['TESTING'] = True

with app.test_client() as client:
    # 先 GET 登录页以获取 CSRF token（若存在）
    resp = client.get('/auth/login')
    print('GET /auth/login ->', resp.status_code)
    # 从表单提取 csrf_token（如果有隐藏字段 'csrf_token' 或 name='csrf_token'）
    import re
    body = resp.get_data(as_text=True)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', body)
    csrf = m.group(1) if m else None
    if csrf:
        print('发现 csrf_token')
    else:
        print('未发现 csrf_token（可能由 WTForms hidden_tag 或 meta 注入）')

    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    if csrf:
        data['csrf_token'] = csrf

    post = client.post('/auth/login', data=data, follow_redirects=True)
    print('POST /auth/login ->', post.status_code)
    text = post.get_data(as_text=True)
    # 打印响应中前 1000 字符摘要
    print('响应摘要（前1000字符）:\n', text[:1000])
    # 检查是否登录成功的常见标志
    if '管理员仪表板' in text or '欢迎' in text or '登出' in text or 'admin' in text:
        print('\n登录可能成功（在响应中找到管理字样/用户名）。')
    else:
        print('\n登录可能失败（未在响应中找到明显标志）。')

    # 打印最终请求路径
    print('最终请求路径:', post.request.path)

print('\n脚本完成')
