# 新功能测试清单

## 📋 测试准备

### 1. 初始化公告系统
```bash
# 在Docker容器中运行
docker exec equipment-management-system python init_announcement_system.py
```

**预期结果:**
- ✅ 创建announcements表
- ✅ 插入3条示例公告
- ✅ 显示企业微信配置指南

---

## 🎯 功能测试清单

### 一、系统公告模块测试

#### 1.1 用户查看公告
- [ ] 访问首页,查看是否显示最新公告(最多3条)
- [ ] 点击"查看更多"跳转到 `/announcements`
- [ ] 验证公告列表分页功能
- [ ] 点击公告标题查看详情
- [ ] 检查公告详情页显示完整内容
- [ ] 验证不同公告类型的徽章颜色
  - 系统公告 - 蓝色(primary)
  - 功能更新 - 绿色(success)
  - 通知公告 - 橙色(warning)
  - 紧急公告 - 红色(danger)

#### 1.2 管理员创建公告
- [ ] 访问 `/admin/announcements`
- [ ] 点击"新建公告"
- [ ] 填写公告信息:
  - [ ] 标题
  - [ ] 内容(测试富文本编辑器)
  - [ ] 公告类型
  - [ ] 优先级
  - [ ] 发布时间(可选)
  - [ ] 过期时间(可选)
- [ ] 勾选"发布状态"
- [ ] 勾选"置顶显示"(可选)
- [ ] 点击"提交"保存

#### 1.3 管理员编辑公告
- [ ] 在公告列表点击"编辑"
- [ ] 修改公告内容
- [ ] 保存并验证更新成功

#### 1.4 管理员删除公告
- [ ] 点击"删除"按钮
- [ ] 确认删除操作
- [ ] 验证公告已从列表移除

#### 1.5 快速操作
- [ ] 测试"发布/取消发布"按钮
- [ ] 测试"置顶/取消置顶"按钮
- [ ] 验证操作后状态更新

#### 1.6 过期公告测试
- [ ] 创建一个过期时间为"昨天"的公告
- [ ] 验证用户端不显示过期公告
- [ ] 验证管理端仍可看到过期公告

---

### 二、企业微信集成测试

#### 2.1 检查配置状态
- [ ] 访问 `/admin/wework`
- [ ] 查看"企业微信集成状态"
- [ ] 验证显示"未配置"或配置信息

#### 2.2 测试连接(未配置状态)
- [ ] 点击"测试连接"
- [ ] 预期返回示例数据(PLACEHOLDER_ACCESS_TOKEN)
- [ ] 确认提示需要配置环境变量

#### 2.3 预览组织架构
- [ ] 点击"预览部门列表"
- [ ] 验证返回示例部门数据
- [ ] 检查部门层级关系

#### 2.4 预览用户列表
- [ ] 点击"预览用户列表"
- [ ] 验证返回示例用户数据
- [ ] 检查用户字段(姓名、手机、部门等)

#### 2.5 扫码登录按钮
- [ ] 访问登录页
- [ ] 检查是否显示"企业微信登录"按钮
- [ ] 点击按钮跳转到 `/login/wework`
- [ ] 验证提示"企业微信功能未启用"(未配置时)

#### 2.6 账号绑定界面
- [ ] 登录后访问个人中心
- [ ] 查看是否有"绑定企业微信"选项
- [ ] 点击绑定(未配置时应提示未启用)

---

### 三、配置企业微信(可选高级测试)

#### 3.1 准备配置信息
需要从企业微信后台获取:
- [ ] 企业ID (CORP_ID)
- [ ] 应用AgentId (AGENT_ID)
- [ ] 应用Secret (SECRET)

#### 3.2 配置环境变量
```bash
# 方式1: 修改docker-compose.yml
environment:
  - WEWORK_CORP_ID=你的企业ID
  - WEWORK_AGENT_ID=应用AgentId
  - WEWORK_SECRET=应用Secret
  - WEWORK_ENABLED=true

# 方式2: 修改.env文件
WEWORK_CORP_ID=你的企业ID
WEWORK_AGENT_ID=应用AgentId
WEWORK_SECRET=应用Secret
WEWORK_ENABLED=true
```

#### 3.3 取消注释API调用
编辑 `app/integrations/wework.py`,将TODO部分取消注释:
- [ ] `get_access_token()` - 取消注释实际API调用
- [ ] `get_user_info()` - 取消注释实际API调用
- [ ] `get_all_users()` - 取消注释实际API调用
- [ ] `get_department_list()` - 取消注释实际API调用

#### 3.4 重启容器
```bash
docker-compose down
docker-compose up -d
```

#### 3.5 测试实际集成
- [ ] 访问 `/admin/wework`
- [ ] 点击"测试连接"验证配置
- [ ] 点击"同步部门"获取真实组织架构
- [ ] 点击"同步用户"获取真实员工名单
- [ ] 测试扫码登录功能

---

## 🔍 数据库验证

### 检查announcements表
```bash
# 进入容器
docker exec -it equipment-management-system bash

# 进入Python shell
python
```

```python
from app import create_app
from app.models import Announcement
from app.extensions import db

app = create_app()
with app.app_context():
    # 查看所有公告
    announcements = Announcement.query.all()
    for a in announcements:
        print(f"ID: {a.id}, 标题: {a.title}, 类型: {a.type}, 状态: {a.is_published}")
    
    # 查看活跃公告
    active = Announcement.get_active_announcements()
    print(f"\n活跃公告数量: {len(active)}")
```

### 检查User模型(企业微信字段)
```python
from app.models import User

with app.app_context():
    # 检查User模型是否有wework_userid字段
    user = User.query.first()
    print(f"用户字段: {[c.name for c in User.__table__.columns]}")
```

---

## 📊 性能测试

### 首页加载性能
- [ ] 访问首页,检查加载时间
- [ ] 验证公告查询不影响首页性能(应该<100ms)
- [ ] 使用浏览器开发者工具查看SQL查询次数

### 公告列表分页
- [ ] 创建20+条公告
- [ ] 测试分页性能
- [ ] 验证每页显示10条

---

## 🐛 错误处理测试

### 公告模块
- [ ] 提交空标题公告(应验证失败)
- [ ] 提交空内容公告(应验证失败)
- [ ] 设置过期时间早于发布时间(应提示错误)
- [ ] 删除不存在的公告(应返回404)

### 企业微信模块
- [ ] 未配置时访问 `/login/wework` (应提示未启用)
- [ ] 配置错误时测试连接(应返回错误信息)
- [ ] 同步时企业微信API不可用(应优雅处理错误)

---

## 📱 浏览器兼容性测试

- [ ] Chrome (最新版)
- [ ] Firefox (最新版)
- [ ] Edge (最新版)
- [ ] Safari (如有Mac)

### 测试项目
- [ ] 公告显示正常
- [ ] 富文本编辑器正常
- [ ] AJAX操作正常
- [ ] 响应式布局正常

---

## ✅ 用户体验验证

### 普通用户视角
- [ ] 首页公告是否醒目
- [ ] 公告内容是否易读
- [ ] 分类标签是否清晰
- [ ] 操作流程是否顺畅

### 管理员视角
- [ ] 公告管理界面是否友好
- [ ] 富文本编辑是否方便
- [ ] 快速操作是否高效
- [ ] 企业微信配置是否清晰

---

## 📝 测试报告模板

### 测试环境
- 操作系统: Windows/Linux
- 浏览器: Chrome/Firefox/Edge
- Docker版本: 
- 数据库: PostgreSQL（已移除 SQLite 运行时支持；测试请配置 TEST_DATABASE_URI）

### 测试结果

#### 系统公告模块
| 功能点 | 状态 | 备注 |
|--------|------|------|
| 用户查看公告 | ✅/❌ | |
| 管理员创建公告 | ✅/❌ | |
| 管理员编辑公告 | ✅/❌ | |
| 管理员删除公告 | ✅/❌ | |
| 快速操作 | ✅/❌ | |
| 过期公告处理 | ✅/❌ | |

#### 企业微信集成
| 功能点 | 状态 | 备注 |
|--------|------|------|
| 配置检查 | ✅/❌ | |
| 预览组织架构 | ✅/❌ | |
| 预览用户列表 | ✅/❌ | |
| 登录按钮显示 | ✅/❌ | |
| 未配置提示 | ✅/❌ | |

### 发现的问题
1. 
2. 
3. 

### 建议改进
1. 
2. 
3. 

---

## 🚀 上线前检查

- [ ] 所有测试用例通过
- [ ] 性能测试达标
- [ ] 错误处理完善
- [ ] 用户手册更新
- [ ] 备份当前数据库
- [ ] 准备回滚方案

---

**测试人员:** ________________  
**测试日期:** ________________  
**测试状态:** ⭕ 通过 / ❌ 失败 / 🔄 待测试
