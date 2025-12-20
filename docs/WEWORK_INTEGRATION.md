# 企业微信集成接口文档

## 功能概述

本系统预留了企业微信集成接口,支持以下功能:
1. 扫码登录
2. 获取用户信息
3. 同步组织架构
4. 同步用户信息

**当前状态**: 接口已预留,返回示例数据,实际使用前需配置企业微信参数并启用相关代码。

## 配置说明

### 1. 获取企业微信凭证

#### 1.1 获取企业ID (Corp ID)
1. 登录[企业微信管理后台](https://work.weixin.qq.com/wework_admin/loginpage_wx)
2. 进入"我的企业" → "企业信息"
3. 复制"企业ID"

#### 1.2 创建自建应用
1. 进入"应用管理" → "应用" → "自建"
2. 点击"创建应用"
3. 填写应用信息(名称、logo等)
4. 创建后获取:
   - **AgentId**: 应用ID
   - **Secret**: 应用密钥

#### 1.3 配置应用权限
在应用设置中配置以下权限:
- 通讯录管理(获取部门和成员)
- 身份验证(用于登录)
- 消息发送(可选,用于通知)

### 2. 配置环境变量

#### 方式1: .env 文件
创建或编辑 `.env` 文件:
```bash
# 企业微信配置
WEWORK_CORP_ID=ww1234567890abcdef
WEWORK_AGENT_ID=1000001
WEWORK_SECRET=your_secret_here
WEWORK_ENABLED=true
```

#### 方式2: Docker Compose
在 `docker-compose.yml` 中添加:
```yaml
services:
  web:
    environment:
      - WEWORK_CORP_ID=ww1234567890abcdef
      - WEWORK_AGENT_ID=1000001
      - WEWORK_SECRET=your_secret_here
      - WEWORK_ENABLED=true
```

#### 方式3: 系统环境变量
```bash
export WEWORK_CORP_ID=ww1234567890abcdef
export WEWORK_AGENT_ID=1000001
export WEWORK_SECRET=your_secret_here
export WEWORK_ENABLED=true
```

### 3. 配置回调域名
在企业微信应用设置中配置:
- **可信域名**: 你的系统域名(如 `example.com`)
- **OAuth2.0回调域名**: 同上

## API 接口说明

### 模块位置
```
app/integrations/wework.py
```

### 主要类: WeWorkAPI

#### 初始化
```python
from app.integrations import get_wework_client

# 获取客户端实例
client = get_wework_client()

# 或手动初始化
from app.integrations import WeWorkAPI
client = WeWorkAPI(
    corp_id='your_corp_id',
    agent_id='your_agent_id',
    secret='your_secret'
)
```

### 核心方法

#### 1. get_access_token()
获取访问令牌,自动处理缓存和刷新。

```python
token = client.get_access_token()
```

**返回**: access_token 字符串

**说明**:
- Token有效期7200秒(2小时)
- 自动缓存,提前5分钟刷新
- 失败时抛出异常

---

#### 2. get_user_info(code)
根据授权码获取用户信息(用于扫码登录)。

```python
user_info = client.get_user_info(code='auth_code_from_frontend')
```

**参数**:
- `code`: 前端扫码后获取的临时授权码

**返回示例**:
```python
{
    'UserId': 'zhangsan',
    'DeviceId': 'xxxxx',
    'user_ticket': 'xxxxx'  # 可选
}
```

---

#### 3. get_user_detail(userid)
获取用户详细信息。

```python
user = client.get_user_detail(userid='zhangsan')
```

**参数**:
- `userid`: 企业微信用户ID

**返回示例**:
```python
{
    'userid': 'zhangsan',
    'name': '张三',
    'mobile': '13800138000',
    'department': [1, 2],
    'position': '产品经理',
    'email': 'zhangsan@company.com',
    'avatar': 'http://...'
}
```

---

#### 4. get_department_list(department_id=None)
获取部门列表。

```python
# 获取所有部门
departments = client.get_department_list()

# 获取指定部门的子部门
departments = client.get_department_list(department_id=1)
```

**参数**:
- `department_id` (可选): 部门ID,不传则获取所有部门

**返回示例**:
```python
[
    {
        'id': 1,
        'name': '总部',
        'parentid': 0,
        'order': 1
    },
    {
        'id': 2,
        'name': '技术部',
        'parentid': 1,
        'order': 1
    }
]
```

---

#### 5. get_department_users(department_id, fetch_child=False)
获取部门成员列表。

```python
# 获取指定部门成员
users = client.get_department_users(department_id=2)

# 递归获取子部门成员
users = client.get_department_users(department_id=2, fetch_child=True)
```

**参数**:
- `department_id`: 部门ID
- `fetch_child`: 是否递归获取子部门成员

**返回示例**:
```python
[
    {
        'userid': 'zhangsan',
        'name': '张三',
        'department': [1, 2],
        'position': '产品经理',
        'mobile': '13800138000',
        'email': 'zhangsan@company.com'
    }
]
```

---

#### 6. sync_departments_to_local()
同步企业微信组织架构到本地数据库。

```python
result = client.sync_departments_to_local()
```

**返回示例**:
```python
{
    'success': True,
    'created': 5,   # 新建数量
    'updated': 3,   # 更新数量
    'total': 8      # 总数
}
```

**说明**: 当前返回占位数据,实际使用需实现同步逻辑。

---

#### 7. sync_users_to_local(department_id=None)
同步企业微信用户到本地数据库。

```python
# 同步所有用户
result = client.sync_users_to_local()

# 同步指定部门用户
result = client.sync_users_to_local(department_id=2)
```

**返回示例**: 同 sync_departments_to_local()

---

### 辅助函数

#### generate_wework_login_url(redirect_uri, state='')
生成企业微信扫码登录URL。

```python
from app.integrations import generate_wework_login_url

url = generate_wework_login_url(
    redirect_uri='https://example.com/callback',
    state='random_state_string'
)
```

**参数**:
- `redirect_uri`: 授权后的回调地址
- `state`: 自定义状态参数(可选)

**返回**: 完整的登录URL

## 使用示例

### 示例1: 扫码登录流程

```python
from flask import request, redirect, session
from app.integrations import get_wework_client, generate_wework_login_url

# 步骤1: 生成登录URL并跳转
@app.route('/login/wework')
def wework_login():
    callback_url = url_for('wework_callback', _external=True)
    login_url = generate_wework_login_url(callback_url, state='xxx')
    return redirect(login_url)

# 步骤2: 处理回调
@app.route('/callback/wework')
def wework_callback():
    code = request.args.get('code')
    if not code:
        return '授权失败', 400
    
    # 获取用户信息
    client = get_wework_client()
    user_info = client.get_user_info(code)
    
    # 获取用户详情
    user_detail = client.get_user_detail(user_info['UserId'])
    
    # 创建或更新本地用户
    # ... 业务逻辑 ...
    
    # 登录用户
    session['userid'] = user_info['UserId']
    return redirect('/')
```

### 示例2: 同步组织架构

```python
from app.integrations import get_wework_client

def sync_organization():
    """同步企业微信组织架构"""
    client = get_wework_client()
    
    # 同步部门
    dept_result = client.sync_departments_to_local()
    print(f"部门同步完成: 新建{dept_result['created']}, 更新{dept_result['updated']}")
    
    # 同步用户
    user_result = client.sync_users_to_local()
    print(f"用户同步完成: 新建{user_result['created']}, 更新{user_result['updated']}")
```

### 示例3: 获取部门结构

```python
from app.integrations import get_wework_client

def build_department_tree():
    """构建部门树形结构"""
    client = get_wework_client()
    departments = client.get_department_list()
    
    # 构建树形结构
    dept_map = {d['id']: d for d in departments}
    for dept in departments:
        dept['children'] = []
    
    tree = []
    for dept in departments:
        if dept['parentid'] == 0:
            tree.append(dept)
        else:
            parent = dept_map.get(dept['parentid'])
            if parent:
                parent['children'].append(dept)
    
    return tree
```

## 启用实际接口

当前所有方法返回示例数据。要启用实际接口:

1. **配置环境变量** (见上文"配置说明")

2. **取消注释代码**
   
   在 `app/integrations/wework.py` 中,找到标记为 `# TODO: 实现实际的API调用` 的部分,取消注释:

   ```python
   # 修改前(示例)
   # TODO: 实现实际的API调用
   # response = requests.get(url, params=params, timeout=10)
   # ...
   return 'PLACEHOLDER_ACCESS_TOKEN'
   
   # 修改后
   response = requests.get(url, params=params, timeout=10)
   data = response.json()
   if data.get('errcode') != 0:
       raise Exception(f"API调用失败: {data.get('errmsg')}")
   return data['access_token']
   ```

3. **测试接口**
   
   建议先在测试环境验证:
   ```python
   from app.integrations import get_wework_client
   
   client = get_wework_client()
   try:
       token = client.get_access_token()
       print(f"✓ Access Token: {token}")
   except Exception as e:
       print(f"✗ 错误: {e}")
   ```

## 数据库结构建议

如需同步组织架构,建议在 User 和 Department 表中添加字段:

### User 表
```python
wework_userid = db.Column(db.String(64), unique=True, nullable=True, comment='企业微信用户ID')
wework_avatar = db.Column(db.String(512), nullable=True, comment='企业微信头像')
wework_synced_at = db.Column(db.DateTime, nullable=True, comment='最后同步时间')
```

### Department 表
```python
wework_id = db.Column(db.Integer, unique=True, nullable=True, comment='企业微信部门ID')
wework_parentid = db.Column(db.Integer, nullable=True, comment='企业微信父部门ID')
wework_synced_at = db.Column(db.DateTime, nullable=True, comment='最后同步时间')
```

## 官方文档参考

- [企业微信API文档](https://developer.work.weixin.qq.com/document/)
- [网页授权登录](https://developer.work.weixin.qq.com/document/path/91022)
- [通讯录管理](https://developer.work.weixin.qq.com/document/path/90194)
- [获取access_token](https://developer.work.weixin.qq.com/document/path/91039)

## 注意事项

1. **安全性**
   - Secret 必须保密,不要提交到代码仓库
   - 使用环境变量或密钥管理服务
   - 定期更新 Secret

2. **API限制**
   - access_token 有效期2小时
   - API调用频率有限制(具体见官方文档)
   - 建议使用缓存减少API调用

3. **异常处理**
   - 所有API调用都应包含异常处理
   - 网络超时建议设置10秒
   - 记录错误日志便于排查

4. **测试建议**
   - 先在测试企业微信账号测试
   - 验证所有权限配置正确
   - 测试回调地址可访问性

5. **生产部署**
   - 确保回调域名是HTTPS
   - 配置正确的可信域名
   - 监控API调用状态

## 常见问题

### Q: 如何测试接口是否配置正确?
A: 运行初始化脚本查看配置信息,或在Python环境中测试:
```python
from app.integrations import get_wework_client
client = get_wework_client()
print(client.corp_id, client.agent_id)
```

### Q: 为什么返回的都是示例数据?
A: 需要先配置环境变量并取消注释代码中的TODO部分。

### Q: 如何处理用户不在企业微信中的情况?
A: 建议保留传统登录方式,企业微信登录作为可选方式。

### Q: 同步频率如何控制?
A: 建议:
- 全量同步: 每天凌晨执行
- 增量同步: 用户登录时更新个人信息
- 手动同步: 提供管理员手动触发按钮

## 更新日志

### 2025-12-02
- ✅ 创建企业微信集成模块
- ✅ 预留所有核心接口
- ✅ 提供完整配置说明
- ✅ 添加使用示例
- ✅ 返回占位数据供测试
