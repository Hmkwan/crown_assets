"""
实时通信和文件管理系统开发方案
================================================================================

一、系统公告附件功能
================================================================================

1. 数据库设计
-------------
表: announcement_attachment (公告附件表)
- id: 主键
- announcement_id: 公告ID (外键)
- filename: 原始文件名
- stored_filename: 存储文件名(UUID)
- file_path: 文件存储路径
- file_size: 文件大小(字节)
- file_type: 文件类型(MIME)
- upload_user_id: 上传用户ID
- created_date: 上传时间
- is_deleted: 软删除标记

2. 后端功能
-----------
路由:
- POST /announcement/create - 创建公告(支持文件上传)
- POST /announcement/<id>/upload - 为已有公告添加附件
- GET /announcement/<id>/attachments - 获取公告附件列表
- GET /attachment/<id>/download - 下载附件
- GET /attachment/<id>/preview - 预览附件(支持PDF/图片/视频)
- DELETE /attachment/<id> - 删除附件

文件处理:
- 支持类型: 文档(.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx)
           图片(.jpg,.png,.gif,.bmp)
           视频(.mp4,.avi,.mov)
           音频(.mp3,.wav)
- 文件大小限制: 单文件最大50MB
- 存储位置: /app/uploads/announcements/
- 安全检查: 文件类型验证、病毒扫描、文件名过滤

3. 前端功能
-----------
公告发布页面:
- 拖拽上传区域
- 多文件选择
- 上传进度条
- 文件列表展示
- 删除已上传文件

公告查看页面:
- 附件列表展示(文件名、大小、类型)
- 下载按钮
- 在线预览按钮(根据文件类型)
- 预览模态框:
  * PDF: 使用PDF.js渲染
  * 图片: 图片查看器(支持缩放、旋转)
  * 视频: HTML5 video播放器
  * 音频: HTML5 audio播放器
  * Office文档: 转PDF后预览或下载


二、实时聊天系统
================================================================================

1. 数据库设计
-------------
表1: chat_message (聊天消息表)
- id: 主键
- sender_id: 发送者ID
- receiver_id: 接收者ID
- message_type: 消息类型(text/image/file/video/audio)
- content: 消息内容(文本消息)
- attachment_id: 附件ID(外键,可为空)
- is_read: 是否已读
- read_time: 阅读时间
- created_date: 发送时间
- is_deleted: 软删除标记
- deleted_by: 删除人(sender/receiver/both)

表2: chat_attachment (聊天附件表)
- id: 主键
- message_id: 消息ID(外键)
- filename: 原始文件名
- stored_filename: 存储文件名
- file_path: 文件路径
- file_size: 文件大小
- file_type: 文件类型
- thumbnail_path: 缩略图路径(图片/视频)
- created_date: 创建时间

表3: chat_conversation (会话表)
- id: 主键
- user1_id: 用户1 ID
- user2_id: 用户2 ID
- last_message_id: 最后一条消息ID
- last_message_time: 最后消息时间
- user1_unread_count: 用户1未读数
- user2_unread_count: 用户2未读数
- created_date: 会话创建时间
- updated_date: 最后更新时间

表4: chat_permission (聊天权限表)
- id: 主键
- user_id: 用户ID
- can_initiate_chat: 是否可发起聊天
- can_send_file: 是否可发送文件
- granted_by: 授权人ID
- created_date: 授权时间

2. 技术方案
-----------
实时通信: Flask-SocketIO (基于WebSocket)
- 事件: 'connect', 'disconnect', 'send_message', 'typing', 'read_message'
- 房间管理: 每个会话一个房间
- 在线状态: Redis存储用户在线状态

后端路由:
- GET /chat/conversations - 获取会话列表
- GET /chat/messages/<user_id> - 获取与指定用户的聊天记录
- POST /chat/send - 发送消息
- POST /chat/upload - 上传聊天附件
- PUT /chat/read/<message_id> - 标记已读
- DELETE /chat/message/<id> - 删除消息
- GET /chat/permissions - 获取聊天权限
- POST /admin/chat/grant-permission - 授权用户聊天权限

SocketIO事件:
- 'connect': 用户上线
- 'disconnect': 用户下线
- 'send_message': 发送消息(实时推送给接收者)
- 'typing': 正在输入提示
- 'read_message': 已读回执
- 'new_notification': 新通知(审批等)

3. 前端功能
-----------
聊天界面:
- 左侧: 会话列表(显示最后消息、未读数、在线状态)
- 右侧: 聊天窗口
  * 消息列表(滚动加载历史)
  * 输入框(支持Enter发送、Shift+Enter换行)
  * 附件按钮(图片/文件/视频)
  * 表情选择器
  * 发送按钮
  
消息显示:
- 文本消息: 气泡样式
- 图片消息: 缩略图(点击放大)
- 文件消息: 文件图标+文件名+大小+下载按钮
- 视频消息: 视频播放器
- 音频消息: 音频播放器
- 时间戳: 群组显示
- 已读/未读状态

实时更新:
- 新消息自动滚动到底部
- 新消息提示音
- 浏览器通知(需权限)
- 标题闪烁提示
- 未读消息数红点


三、实时审批通知
================================================================================

1. 数据库扩展
-------------
表: approval_notification (审批通知表) - 扩展现有notification表
- 新增字段:
  * is_realtime: 是否实时推送
  * push_time: 推送时间
  * delivery_status: 推送状态(pending/sent/failed)

2. 后端实现
-----------
SocketIO事件:
- 'new_approval': 新审批通知
- 'approval_reminder': 审批提醒
- 'approval_completed': 审批完成通知

推送机制:
- 创建审批时通过SocketIO推送给审批人
- 定时任务检查超时未审批(发送提醒)
- 审批完成后推送给申请人

3. 前端实现
-----------
实时通知组件:
- 顶部通知栏(显示最新通知)
- 右下角弹窗(Toast提示)
- 声音提醒
- 桌面通知
- 审批列表实时更新


四、技术架构
================================================================================

1. 后端技术栈
-------------
- Flask-SocketIO: WebSocket实时通信
- Redis: 在线状态、消息队列
- Celery: 异步任务(文件处理、通知推送)
- PIL/Pillow: 图片处理(缩略图)
- python-magic: 文件类型检测
- PyPDF2: PDF处理

2. 前端技术栈
-------------
- Socket.IO客户端: 实时通信
- PDF.js: PDF预览
- Video.js: 视频播放
- Plyr: 音频播放
- PhotoSwipe: 图片查看器
- Dropzone.js: 文件拖拽上传
- 表情包库: emoji-picker

3. 文件存储
-----------
开发环境: 本地文件系统
生产环境: 
- 本地存储 + Nginx代理
- 或对象存储(OSS/S3)

4. 安全措施
-----------
- 文件上传: 类型白名单、大小限制、病毒扫描
- 下载验证: 权限检查、防盗链
- XSS防护: 文件名过滤、Content-Type设置
- CSRF防护: Token验证
- WebSocket认证: Session/Token验证


五、开发步骤
================================================================================

阶段1: 公告附件功能 (2-3天)
1. 创建数据库表
2. 实现文件上传/下载后端
3. 实现前端上传界面
4. 实现文件预览功能

阶段2: 实时聊天基础功能 (3-4天)
1. 安装配置SocketIO
2. 创建聊天相关数据表
3. 实现消息发送/接收
4. 实现前端聊天界面

阶段3: 聊天附件功能 (2天)
1. 实现聊天文件上传
2. 实现图片/视频预览
3. 生成缩略图

阶段4: 实时审批通知 (1-2天)
1. 集成SocketIO到审批流程
2. 实现实时推送
3. 前端通知组件

阶段5: 权限管理 (1天)
1. 聊天权限管理界面
2. 权限检查中间件

阶段6: 测试优化 (2天)
1. 功能测试
2. 性能优化
3. 安全测试


六、Docker配置调整
================================================================================

docker-compose.yml 需要添加:
- Redis服务(用于WebSocket和缓存)
- 卷挂载(文件上传目录)

Dockerfile 需要添加:
- Flask-SocketIO
- Redis客户端
- 图片处理库
- PDF处理库


七、预估工作量
================================================================================

总计: 约11-14个工作日
- 公告附件: 2-3天
- 实时聊天: 5-6天  
- 实时通知: 1-2天
- 权限管理: 1天
- 测试优化: 2天

建议分阶段开发,先完成基础功能,再逐步完善。

"""

print(__doc__)
