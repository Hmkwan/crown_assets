# 聊天系统测试指南

## 🎯 系统状态

### ✅ 已完成功能
1. **数据库模型** (app/chat_models.py)
   - ✅ ChatConversation - 会话表
   - ✅ ChatParticipant - 参与者表
   - ✅ ChatMessage - 消息表
   - ✅ ChatAttachment - 附件表
   - ✅ ChatPermission - 权限表

2. **后端API** (app/chat_routes.py)
   - ✅ GET /api/chat/users - 获取用户列表(新增)
   - ✅ POST /api/chat/conversations - 创建会话
   - ✅ GET /api/chat/conversations - 获取会话列表
   - ✅ GET /api/chat/conversations/<id> - 获取会话详情
   - ✅ GET /api/chat/conversations/<id>/messages - 获取消息历史
   - ✅ POST /api/chat/conversations/<id>/messages - 发送消息
   - ✅ POST /api/chat/conversations/<id>/pin - 置顶会话
   - ✅ POST /api/chat/conversations/<id>/mute - 静音会话
   - ✅ GET /api/chat/attachments/<id> - 下载附件
   - ✅ POST /api/chat/upload - 上传附件

3. **WebSocket事件** (app/socketio_handler.py)
   - ✅ join_conversation - 加入会话
   - ✅ leave_conversation - 离开会话
   - ✅ send_message - 发送消息
   - ✅ typing - 输入状态
   - ✅ read_receipt - 已读回执
   - ✅ recall_message - 撤回消息

4. **前端界面** (app/templates/chat.html)
   - ✅ 双栏布局(会话列表 + 聊天窗口)
   - ✅ 响应式设计
   - ✅ 新建会话模态框
   - ✅ 文件上传控件

5. **前端逻辑** (app/static/js/chat.js)
   - ✅ Socket.IO连接管理
   - ✅ 会话列表加载和渲染
   - ✅ 新建会话功能(今天新增)
   - ✅ 消息发送和接收
   - ✅ 文件上传
   - ✅ 输入状态显示
   - ✅ 已读回执
   - ✅ 消息撤回

6. **Docker配置**
   - ✅ 使用eventlet worker(修复Bad file descriptor错误)
   - ✅ Redis集成(消息队列)
   - ✅ 健康检查

---

## 🧪 测试步骤

### 1. 访问聊天页面
```
URL: http://localhost:5020/chat
```
- 应该能看到双栏布局
- 左侧显示"消息"标题和"新建"按钮
- 左侧有搜索框
- 左侧会话列表可能为空或显示"暂无会话"

### 2. 测试新建会话
1. 点击"新建"按钮
2. 应该弹出"新建会话"对话框
3. 检查以下元素:
   - ✓ 会话类型选择(一对一/群组)
   - ✓ 选择成员列表(应该显示其他用户)
   - ✓ 群组名称输入框(选择群组时显示)
   - ✓ "创建"和"取消"按钮

4. 创建一对一会话:
   - 选择"一对一"
   - 从成员列表选择一个用户
   - 点击"创建"
   - 应该关闭对话框,左侧会话列表出现新会话

5. 创建群组会话:
   - 选择"群组"
   - 输入群组名称
   - 从成员列表选择多个用户(按住Ctrl多选)
   - 点击"创建"
   - 应该出现新的群组会话

### 3. 测试发送消息
1. 点击左侧任一会话
2. 右侧应该显示:
   - ✓ 会话标题(用户名或群组名)
   - ✓ 消息列表区域
   - ✓ 底部输入框和发送按钮

3. 在输入框输入消息,点击"发送"或按Enter
4. 消息应该出现在聊天窗口右侧(蓝色气泡)

### 4. 测试文件上传
1. 点击输入框上方的📎(回形针)图标
2. 选择文件上传
3. 文件应该作为附件发送

### 5. 测试实时通知
1. 打开两个浏览器窗口,用不同账号登录
2. 在窗口A发送消息
3. 窗口B应该实时收到消息(如果在同一会话中)

---

## ⚠️ 已知问题

### 1. Redis连接警告
```
⚠ Redis连接失败,使用内存模式
```
- **影响**: 使用内存模式,容器重启后消息队列清空
- **状态**: 不影响功能,Redis在启动后会自动连接
- **建议**: 生产环境确保Redis先启动

### 2. "发送通知失败: name 'user_id' is not defined"
- **位置**: app/socketio_handler.py 或通知系统
- **影响**: 不影响聊天功能,可能影响全局通知
- **状态**: 待修复

### 3. "Bad file descriptor" 错误
- **状态**: ✅ 已修复
- **解决方案**: 使用eventlet worker而不是sync worker

---

## 📊 数据库验证

### 检查聊天表
```bash
docker exec equipment-management-system python -c "
from app import create_app, db
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
app = create_app()
with app.app_context():
    print('会话数:', ChatConversation.query.count())
    print('参与者数:', ChatParticipant.query.count())
    print('消息数:', ChatMessage.query.count())
"
```

### 查看会话列表
```bash
docker exec equipment-management-system python -c "
from app import create_app, db
from app.chat_models import ChatConversation
app = create_app()
with app.app_context():
    convs = ChatConversation.query.all()
    for conv in convs:
        print(f'ID={conv.id}, 类型={conv.conversation_type}, 名称={conv.name}')
"
```

---

## 🚧 待开发功能(图2需求)

### 1. 开发聊天天管理界面
- [ ] 管理员查看所有会话
- [ ] 会话统计(消息数、活跃度等)
- [ ] 消息审计(查看敏感消息)
- [ ] 会话禁用/删除
- [ ] 用户聊天权限管理

### 2. 增强功能
- [ ] 消息搜索
- [ ] @提及功能
- [ ] 表情包支持
- [ ] 语音消息
- [ ] 视频通话集成
- [ ] 消息加密

---

## 🎨 界面截图位置

### 当前界面应该呈现:
1. **聊天列表页** - 左侧会话列表 + 右侧空状态"选择一个会话开始聊天"
2. **新建会话对话框** - 模态框,包含用户列表和会话类型选择
3. **聊天窗口** - 选中会话后,右侧显示消息列表和输入框

---

## 📝 测试用例

### TC-001: 创建一对一会话
- **前置条件**: 系统中至少有2个用户
- **步骤**:
  1. 登录用户A
  2. 访问/chat
  3. 点击"新建"
  4. 选择"一对一"
  5. 选择用户B
  6. 点击"创建"
- **预期结果**: 会话创建成功,左侧列表显示新会话

### TC-002: 发送文本消息
- **前置条件**: 已有会话
- **步骤**:
  1. 选择一个会话
  2. 在输入框输入"测试消息"
  3. 点击"发送"
- **预期结果**: 消息显示在右侧蓝色气泡中

### TC-003: 上传文件
- **前置条件**: 已有会话
- **步骤**:
  1. 选择一个会话
  2. 点击📎图标
  3. 选择一个小于10MB的文件
- **预期结果**: 文件作为附件发送

### TC-004: 实时接收消息
- **前置条件**: 两个用户在同一会话
- **步骤**:
  1. 用户A发送消息
- **预期结果**: 用户B实时收到消息(无需刷新页面)

---

## 🔍 调试技巧

### 1. 查看浏览器控制台
```
F12 → Console
```
查找错误信息,特别是:
- API请求失败
- Socket.IO连接问题
- JavaScript错误

### 2. 查看Network请求
```
F12 → Network
```
检查:
- /api/chat/* 请求是否返回200
- Socket.IO连接是否升级为WebSocket

### 3. 查看Docker日志
```powershell
docker logs equipment-management-system -f
```
实时查看服务器日志

### 4. 测试API
```powershell
# 测试用户列表API
docker exec equipment-management-system python -c "
from app import create_app
from app.models import User
app = create_app()
with app.app_context():
    users = User.query.filter_by(is_active=True).all()
    for u in users:
        print(f'ID={u.id}, 用户名={u.username}')
"
```

---

## 📞 联系支持

如果遇到问题,请提供:
1. 浏览器控制台截图
2. Docker日志(最后50行)
3. 具体操作步骤
4. 预期结果vs实际结果

---

**测试日期**: 2025-12-06  
**版本**: v1.0  
**状态**: 基础功能已完成,待测试和增强
