# Copilot Instructions for IT资产管理系统

精要：为 AI 编码代理提供在本仓库能快速产出可运行变更的、可执行的指南。目标是：在 1–2 次提问内做出可测试的补丁并通过本地测试。

## 一眼看懂（架构与边界）
- Web 后端：Flask + SQLAlchemy，入口在 `app/__init__.py`（`create_app()` 负责配置DB、登录、SocketIO、调度器、蓝图注册、兼容性修补）。
- 服务分层：路由（`app/main`, `app/api`, `app/admin` 等）只做参数/权限与响应格式，复杂业务放 `app/services/`（示例：`app/services/approval_service.py`）。
- 实时：Flask-SocketIO + Redis（可选 message_queue），事件在 `app/socketio_handler.py` 与 `app/chat_*` 文件夹。
- 调度：APScheduler（`app/scheduler.py`），由 `create_app()` 调用 `init_scheduler(app)`，调度任务须在 app.context 中运行或显式推送上下文。
- 数据库迁移：仓库以 SQL 脚本和导出为主（`migrations/` 下的 `*.sql` / `*.py`），并在 `create_app()` 中有**兼容性修补**（运行时尝试自动 ADD COLUMN，便于渐进迁移）。

## 快速上手（环境与常用命令）
- 建议（Windows）:
  - python -m venv .venv
  - & .\.venv\Scripts\Activate.ps1
  - pip install -r requirements.txt
- 本地启动：`python app.py`（默认 host=0.0.0.0 port=5020）
- 调试变量：`FLASK_DEBUG=True|False`（默认 5020，输出路由仅在 `FLASK_DEBUG` 打开时显示）
- 推荐 Docker Compose：`docker-compose up --build`（包含 postgres, redis）。

## 重要环境变量（必须知道）
- SKIP_SOCKETIO_INIT=1 — 跳过 SocketIO 初始化（用于脚本/CI，避免因 Redis 不可用而阻塞）。
- REDIS_HOST / REDIS_PORT / REDIS_DB — SocketIO 的 message_queue（`app/socketio_handler.py` 使用 `redis://`）。
- ENABLE_FD2_FILTER=1 — 启用底层 stderr 过滤（高级运维调试用）。
- DATABASE_URL — 生产 DB 连接字符串（Postgres）。

## 测试与常见陷阱（实用提示）
- 运行测试：`pytest -q`。Tests 以 `create_app()` 构建应用；常见 pattern：创建 `TestConfig` 覆盖 `SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'`。
- SocketIO 测试：需要 eventlet 的 monkey patch（示例：`tests/test_socketio_connection.py` 中 `import eventlet; eventlet.monkey_patch()`）。
- 若 tests 在导入时因 `apscheduler`、`eventlet`、`redis` 缺失而失败，请先安装 `requirements.txt`（`APScheduler`, `eventlet`, `redis`, `Flask-SocketIO`）。
- 脚本/CI：若需要在没有 Redis 的环境安全运行脚本，请在运行前设置 `SKIP_SOCKETIO_INIT=1`。

## 代码约定（对 AI 的具体指令）
- 将复杂逻辑放服务层：优先在 `app/services/` 添加/更改逻辑，route 负责参数验证与权限检查。
- 延迟导入：为避免循环导入，**在函数内部**导入模型或服务（参见 `app/__init__.py` 中的 `load_user`、`inject_unread_notifications` 示例和 `app/main/inventory_routes.py`）。
- 数据库改动：修改模型时同时添加 `migrations/*.sql` 或 `migrations/versions/*.py` 对应脚本；写测试用 in-memory sqlite 验证行为。
- 日志与噪音：底层有针对 engineio/socketio 的日志过滤与 stderr 拦截（见 `app/__init__.py` 的过滤实现），变更日志时注意不要破坏这些过滤器。

## SocketIO / Redis 注意事项（具体示例）
- 初始化位置：`create_app()` 内调用 `app.socketio = init_socketio(app)`（看 `app/socketio_handler.py: init_socketio`），async_mode 固定为 `eventlet`。
- message_queue：如果 Redis 不可用，handler 会降级为内存模式（`message_queue=None`），但有功能差异；测试时注意模拟或跳过 Redis。
- 客户端事件示例：`join_conversation`、`send_message`、`typing`。实现中会做权限检查并在房间内 broadcast（参见 `app/socketio_handler.py`）。

## 调度（APScheduler）和兼容性修补
- `init_scheduler(app)` 在 `app/scheduler.py` 中定义；APScheduler 是必需依赖以启用定时任务。
- `create_app()` 启动期间有一段**兼容性修补**逻辑，会尝试通过 `ALTER TABLE ADD COLUMN` 自动修复缺失列（便于老库直接启动）。请在做正式 schema 更改时同时提交迁移脚本到 `migrations/`，不要仅依赖运行时修补。

## 常见文件与示例（查阅优先级）
- 核心：`app/__init__.py`, `app/socketio_handler.py`, `app/scheduler.py`, `requirements.txt`
- 服务：`app/services/*.py`（业务逻辑实现）
- 路由：`app/main/*.py`, `app/api/*.py`, `app/admin/*`（蓝图注册在 `create_app()` 中）
- 脚本：`scripts/print_routes.py`, `scripts/init_workflow_templates.py`（如何使用 `create_app()`）
- 迁移：`migrations/*.sql`, `migrations/README_SQLite_to_RDBMS.md`
- 测试样例：`tests/test_socketio_connection.py`（演示 eventlet monkey-patch 与 socketio 测试），`tests/*` 其余文件展示典型测试模式

## 小提示 / 常见 PR checklist ✅
- 包：在本地先 pip install -r requirements.txt 并确认 `pytest -q` 通过
- 路由/新 API：在 `scripts/print_routes.py` 或 `python app.py`（FLASK_DEBUG=True）下验证路由已注册
- 数据库：为每个 schema 改动提交 `migrations/` SQL，并在 tests 中使用 in-memory sqlite 验证行为
- SocketIO：若修改 socket 事件，添加对应的单元/集成测试（参照 `tests/test_chat_auto.py`）

---
如需我把这些要点精简为易核查的 PR Checklist 或补充某个子模块（审批/聊天/调度/迁移）快速入门片段，我可以继续把该部分展开为 10–15 条操作步骤供 CI/Reviewer 使用。请告诉我你想先改进哪一块。✅