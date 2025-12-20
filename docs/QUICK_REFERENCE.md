# 🎯 新功能快速参考

## 📢 系统公告模块

### 管理员使用
```
访问: /admin/announcements
功能: 创建、编辑、发布、删除公告
特性: 定时发布、置顶、富文本、分类管理
```

### 用户查看
```
首页: 自动显示最新3条
列表: /announcements
详情: 点击标题查看
```

---

## 🏢 企业微信集成

### 配置要求
```bash
# 环境变量
WEWORK_CORP_ID=企业ID
WEWORK_AGENT_ID=应用AgentId  
WEWORK_SECRET=应用Secret
WEWORK_ENABLED=true
```

### 核心接口(已预留)
```python
from app.integrations import get_wework_client

client = get_wework_client()

# 获取通讯录
users = client.get_all_users()

# 获取组织架构
departments = client.get_department_list()

# 获取部门成员
members = client.get_department_users(dept_id)

# 同步到本地
client.sync_departments_to_local()
client.sync_users_to_local()
```

### 登录流程
```
用户点击"企业微信登录" 
→ 扫码授权 
→ 回调验证 
→ 自动登录(账号需已存在)
```

### 管理端
```
访问: /admin/wework
功能: 测试连接、预览数据、同步组织架构
```

---

## ⚠️ 重要说明

### ✅ 保留的功能
- 管理员开通账号
- 账号申请审批
- 账号密码登录  
- 角色权限管理
- 部门管理

### 🔶 企业微信特点
- 可选功能(不是必需)
- 补充登录方式
- 需账号已存在
- 不自动创建账号
- 当前返回示例数据

---

## 📦 初始化

### 公告系统
```bash
# Docker中
docker exec equipment-management-system python init_announcement_system.py

# 本地
python init_announcement_system.py
```

### 企业微信
```bash
# 1. 配置环境变量
# 2. 取消wework.py中TODO注释
# 3. 访问/admin/wework测试
```

---

## 📚 完整文档

- [公告系统文档](ANNOUNCEMENT_SYSTEM.md)
- [企业微信文档](WEWORK_INTEGRATION.md)  
- [开发总结](NEW_FEATURES_SUMMARY.md)
