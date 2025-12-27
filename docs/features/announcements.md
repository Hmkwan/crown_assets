# 功能：公告（Announcements）

## 概述
管理系统内的公告发布/编辑/附件管理与前端富文本编辑器支持。

## 关键文件
- 控制器/路由：`app/main/announcement_routes.py`（管理UI）
- API 路由：`app/routes/announcement_routes.py`（附件、上传、下载等）
- 模型：`app/models.py` / `app/models/announcement.py`（`Announcement`, `AnnouncementAttachment`）
- 服务：`app/services/announcement_service.py`
- 模板：`app/templates/admin/announcements/form_new.html`、`form_simple.html`
- 测试：`tests/test_announcement_update_validation.py`

## 主要端点（示例）
- GET `/admin/announcements` - 列表视图
- POST `/admin/announcements/create` - 创建公告
- POST `/admin/announcements/<id>/edit` - 编辑公告
- POST `/api/announcements/<id>/upload` - 上传附件/内嵌图片
- GET `/api/attachments/<attachment_id>/download` - 下载附件

## 数据库
- Announcement 表：`content`、`title`、`type`、`is_published`、`publish_time`、`expire_time` 等
- AnnouncementAttachment 表：`filename`、`path`、`file_size`、`upload_user_id` 等（注意 upload_user_id 在某些迁移中需允许 NULL）

## 已知问题与修复
- 问题：在生产中曾出现 `NotNullViolation`（Announcement.content 被设置为 NULL 时触发）
  - 解决：请求处理时使用 `db.session.no_autoflush` 防止未完成验证前的 autoflush；加入了 model-layer 的 `before_flush` 监听来阻止 `content` 被意外置为 NULL；增加回归测试。

- 前端兼容性：Summernote 在旧浏览器中抛语法错误
  - 解决：在模板中加入更严格的特性检测与 `script.onerror` 回退到纯 textarea 的逻辑。

## 测试覆盖
- 已有单元/集成测试覆盖创建/编辑/附件上传的关键场景（见 `tests/test_announcement_update_validation.py`）

## 建议与改进
- 增加对附件的异步病毒扫描/内容类型白名单验证
- 为公告内容变更添加更详细的审计日志（已记录大体操作，建议保存变更 diff）
- 添加 Playwright/端到端的浏览器测试覆盖 Summernote 回退逻辑
