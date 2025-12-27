PR 标题: Fix: allow chat_attachment.upload_user_id nullable for safe backfills; add migration & tests

问题概述
- 在对 announcements 执行 UPDATE 时，session autoflush 导致 production 中出现 NotNullViolation（announcement.content 被意外设置为 NULL）。
- 在将全部测试套件对 PostgreSQL 运行时，发现一个回填测试失败：在回填运行前 `chat_attachment.upload_user_id` 被声明为 NOT NULL，导致测试插入 NULL 时触发 IntegrityError。

本 PR 做了什么
- 修复/强化：
  - 在 `app/main/announcement_routes.py` 中对编辑/创建流程使用 `db.session.no_autoflush` 并在赋值前做验证，避免意外将 `content` 置为 NULL。
  - 在 `app/models.py` 添加 `before_flush` listener，防止任何情况下把 Announcement.content 刷新为 NULL（回退到旧值或者设置一个安全字符串，并记录警告）。
  - 更健壮的 `is_admin` 判定（函数或布尔属性都兼容），修复了相关装饰器。
- 回填/迁移修复：
  - 在 `app/__init__.py` 的应用运行时兼容性补丁中，添加 idempotent 的 ALTER TABLE 操作：`ALTER TABLE chat_attachment ALTER COLUMN upload_user_id DROP NOT NULL`（仅对 PostgreSQL，安全、可重复）。
  - 新增/更新 Alembic 迁移脚本（`alembic/versions/...patch_chat_attachment_and_workflow_columns.py`），在 migration 中以幂等方式确保 `upload_user_id` 可为 NULL。
- 测试：
  - 新增/修改回归测试：`tests/test_announcement_update_validation.py`、`tests/test_migrations_backfill.py`，分别覆盖 announcement 为空 content 的安全行为以及 chat_attachment 回填前允许 NULL 的场景。

验证方法（本地）
1. 启动本地 PostgreSQL（或用仓库的 docker-compose）。
2. 设置 `TEST_DATABASE_URI` 指向你的测试 DB，例如 `postgresql://postgres:password@localhost:15432/test_it_asset`。
3. 运行 `pytest -q` （项目已验证在 Postgres 上通过：`40 passed, 1 skipped`）。

运维注意事项（必须在生产上执行） ✅
- 在将本 PR 合并到主分支并发布之前或之后（取决于你的发布流程），请在生产环境运行：

  alembic upgrade head

  以确保 Alembic 迁移脚本已应用，使 `chat_attachment.upload_user_id` 在回填之前允许为 NULL，避免回填期间出现 IntegrityError。

建议审阅者与标签
- 标签: migrations, tests, bugfix
- 建议审阅者: @数据库维护小组, @后端开发负责人

变更文件
- app/__init__.py
- alembic/versions/20251222_patch_chat_attachment_and_workflow_columns.py (或类似名称)
- app/models.py
- app/main/announcement_routes.py
- app/decorators.py
- tests/test_announcement_update_validation.py
- tests/test_migrations_backfill.py

合并后建议操作
- 确认 CI 在合并 PR 后运行完整的 Postgres 测试矩阵（如果尚未配置）。
- 在合并后通知运维在生产上运行 Alembic（或在发布流程中自动运行）。

短说明: 本 PR 在请求层、模型层、迁移/运行时层与测试层多重防护以修复生产中由 NULL 引发的约束错误，并确保回填迁移在 Postgres 上能安全执行。