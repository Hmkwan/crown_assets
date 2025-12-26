# Copilot Instructions — IT资产管理系统

目的：让 AI 编码代理在 1–2 次交互内产出可运行、可测试的补丁并通过本地测试；保留关键约定、运行/测试命令、与仓库特化示例。

## 快速概览
- 栈：Python (3.8+) + Flask + SQLAlchemy。App 入口由 `app/__init__.py` 的 `create_app()` 创建并配置：DB、登录、SocketIO、APScheduler、蓝图。
- 实时：基于 Flask-SocketIO（`app/socketio_handler.py`），生产通常使用 `eventlet` + Redis（参见 `docker-compose.yml`）。
- 调度：APScheduler（`app/scheduler.py`），`create_app()` 会按环境变量初始化任务。
- 数据库：生产使用 PostgreSQL；迁移由 Alembic 管理（`migrations/`）。注意：`create_app()` 内有运行时的兼容性 ALTER 补丁，但不要依赖其代替正式迁移脚本。

## 关键命令（直接照抄即可）
- 本地开发：
  - 启动：`python app.py`（默认 host=0.0.0.0 port=5020；若启用 SocketIO 则通过 socketio.run 启动）
  - 容器化：`docker-compose up --build`（`web` 映射到 5020；包含 `postgres` & `redis`）
  - 生产：使用 `wsgi.py`，容器/部署用 Gunicorn
- 数据库迁移：
  - 新建迁移：`alembic revision --autogenerate -m "<msg>"`
  - 应用迁移：`alembic upgrade head`（在 CI/本地非破坏性验证）
- 测试：`pytest -q`（`conftest.py` 在 session 启动时创建表并注入种子数据）

## 测试与约束（重要示例）
- 测试安全：`conftest.py` 默认 `TEST_DATABASE_URI=sqlite:///tests_shared.db` 并阻止连接到远程 Postgres，除非设置 `FORCE_ALLOW_REMOTE_DB=1`。
- 测试模式：`create_app()` 会检测 `PYTEST_CURRENT_TEST`、`TESTING=1` 等并启用测试友好配置（内存/SQLite、禁用 CSRF、跳过 Redis）。
- SocketIO 测试：使用 `eventlet.monkey_patch()`（见 `tests/test_socketio_connection.py`）；如果缺少 `flask_socketio` 项目自带一个 stub 以保持多数测试可跑，确保在需要时安装 `eventlet`。

## 项目约定与常见陷阱
- 业务逻辑务必放在 `app/services/`，路由仅做参数校验/权限并调用服务层。
- 为避免循环导入，采用延迟导入（在函数内部导入模型/服务），示例见 `create_app()` 中的 `load_user` 与 `inject_unread_notifications`。
- `create_app()` 有自动 ALTER 补丁（缺列时尝试修复），但每次模型修改仍要提交 Alembic 迁移脚本并在 tests 中验证。
- 日志处理：项目对 engineio/socketio 噪音做了过滤与 fd2 拦截（`ENABLE_FD2_FILTER=1`）；变动日志处理时务必在包含 socket 场景下回归测试。
- 蓝图与路由：大多数蓝图在 `create_app()` 注册（`app.main`, `app.api`, `app.admin`, `app.chat_*` 等）。修改路由后用 `scripts/print_routes.py` 或开启 `FLASK_DEBUG=True` 验证已注册。

## 有用的环境变量（常用）
- `SKIP_SOCKETIO_INIT=1`：跳过 SocketIO 初始化（CI/脚本中避免依赖 Redis）。
- `REDIS_DISABLED=1`：禁用 Redis，SocketIO 回退到内存模式。
- `REDIS_HOST/REDIS_PORT/REDIS_DB`：消息队列配置（Docker 默认服务名为 `equipment-redis`）。
- `SCHEDULER_ENABLED` / `SCHEDULER_JOBS`：控制调度器与单任务启停。
- `ENABLE_FD2_FILTER=1`：启用 stderr 过滤（调试/运维用途）。

## 编辑/测试建议 & PR Checklist ✅
- 本地先安装依赖：`pip install -r requirements.txt`。
- 运行 `pytest -q` 并确保所有 tests（包括 SocketIO 相关）通过；若新增 DB 字段，添加 Alembic migration 并在测试中验证。示例测试位置：`tests/test_chat_auto.py`, `tests/test_socketio_connection.py`。
- 若改动 socket 事件：新增/更新对应的 SocketIO 单/集成测试并在有 `eventlet` 的环境下跑。 
- 修改日志/stderr 处理时：在包含 engineio/socketio 场景下验证没有噪音回归。

---

请帮忙审阅：哪些子模块你想要我补充“快速上手”步骤（例如 scheduler、socketio 或 migrations 的典型补丁流程）？我会据此迭代并把示例补齐。