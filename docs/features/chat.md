# 功能：聊天与实时通知（Chat & Real-time）

## 概述
基于 Flask-SocketIO 的即时通讯模块，支持对话、附件、在线用户统计与消息通知。

## 关键文件
- SocketIO handler：`app/socketio_handler.py`
- 路由：`app/chat_routes.py`、`app/chat_api.py`
- 模型：`app/chat_models.py`（`ChatConversation`, `ChatParticipant`, `ChatMessage`, `ChatAttachment`）
- 测试：`tests/test_chat_socketio_send_message.py`, `tests/test_chat_notifications.py`, `tests/test_chat_workflow.py`

## 主要功能
- 加入/离开房间、私聊与群聊
- 附件上传（ChatAttachment，注意 upload_user_id 可为 NULL 的迁移细节）
- 在线用户管理（`app/online_users.py`）

## 已知问题与修复
- 迁移/backfill：`chat_attachment.upload_user_id` 在回填前应允许 NULL；已添加 idempotent 的 Alembic migration 并在启动时应用运行时 ALTER 作为兼容补丁。

## 测试覆盖
- SocketIO 连接与消息广播测试（使用 eventlet COW 模式在 CI 中运行）

## 建议
- 增加负载测试和消息队列退避策略
- 对附件存储进行内容类型验证与权限校验
