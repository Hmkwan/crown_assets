# 简化聊天系统使用说明

## 概述
为解决WebSocket连接不稳定的问题,创建了基于HTTP轮询的简化聊天系统,适合局域网环境使用。

## 技术方案

### 轮询机制
- **会话列表**: 每5秒自动刷新一次
- **消息列表**: 当前会话每3秒轮询一次新消息
- **无需WebSocket**: 纯AJAX + REST API实现

### 核心文件

#### 1. 前端页面
- **文件**: `app/templates/chat_simple.html`
- **功能**:
  - 会话列表显示
  - 消息发送与接收
  - 自动轮询更新
  - 新建会话对话框

#### 2. 后端API
- **文件**: `app/chat_routes.py`
- **新增路由**:
  ```python
  POST /api/chat/messages  # 发送消息(HTTP方式)
  ```

#### 3. 主路由
- **文件**: `app/main/routes.py`
- **路由**:
  ```python
  GET /chat  # 简化版聊天页面(轮询)
  GET /chat_websocket  # WebSocket版本(保留)
  ```

## 使用方法

### 1. 访问聊天页面
```
http://localhost:5020/chat
```

### 2. 创建会话
1. 点击"新建会话"按钮
2. 选择参与者(可多选)
3. 输入会话名称(可选)
4. 点击"创建"

### 3. 发送消息
1. 在会话列表中选择一个会话
2. 在输入框中输入消息
3. 按Enter或点击发送按钮

### 4. 接收消息
- 消息会自动每3秒刷新一次
- 新消息会显示在聊天窗口中

## API接口

### 获取会话列表
```http
GET /api/chat/conversations
```

### 获取消息
```http
GET /api/chat/messages/<conversation_id>?limit=50
```

### 发送消息
```http
POST /api/chat/messages
Content-Type: application/json

{
  "conversation_id": 1,
  "content": "你好",
  "message_type": "text"
}
```

### 创建会话
```http
POST /api/chat/conversations
Content-Type: application/json

{
  "participants": [2, 3, 4],
  "name": "项目讨论组"
}
```

## 优势
1. ✅ **稳定性高**: 无WebSocket连接问题
2. ✅ **简单部署**: 无需Redis或额外配置
3. ✅ **局域网友好**: 轮询延迟在局域网中可接受(3-5秒)
4. ✅ **兼容性好**: 所有浏览器都支持
5. ✅ **易维护**: 纯HTTP请求,易于调试

## 注意事项
- 轮询间隔可在`chat_simple.html`中调整:
  ```javascript
  setInterval(loadConversations, 5000);  // 会话列表5秒
  setInterval(loadMessages, 3000);       // 消息3秒
  ```
- 不适合超高频率消息(秒级响应),适合一般办公交流

## 对比WebSocket版本

| 特性 | 简化版(轮询) | WebSocket版 |
|------|-------------|------------|
| 实时性 | 3-5秒延迟 | 即时 |
| 连接稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 部署复杂度 | 低 | 高(需Redis) |
| 资源消耗 | 中等 | 低 |
| 适用场景 | 局域网办公 | 互联网实时聊天 |

## 故障排查

### 1. 会话列表为空
- 检查是否登录
- 查看浏览器控制台错误
- 确认API `/api/chat/conversations` 返回200

### 2. 消息发送失败
- 检查POST `/api/chat/messages` 是否返回成功
- 确认是会话参与者
- 查看浏览器Network面板

### 3. 消息不更新
- 检查轮询是否正常运行(控制台有日志)
- 确认GET `/api/chat/messages/<id>` 返回200
- 刷新页面重试

## 开发日志
- **2025-12-06**: 创建简化聊天系统
  - 修复Redis DNS解析问题(使用IP地址)
  - 修复department.name错误
  - 修复user_id未定义错误
  - 移除烦人的连接成功弹窗
  - 创建基于轮询的简化版本
