# 功能：数据库迁移（Migrations / Alembic）

## 概述
数据库迁移使用 Alembic 管理，迁移文件位于 `alembic/versions/`。

## 注意点与历史问题
- 遇到过多个 head 导致 `alembic upgrade head` 需要手动合并 heads 的情况。建议合并分叉为单一合并点。
- `alembic_version.version_num` 在历史上被定义为 `varchar(32)`，在 revision 名称较长时会导致插入失败，已通过扩列到 `varchar(128)` 修复。
- 在做回填（例如 `chat_attachment.upload_user_id` 回填）时要先将列改为允许 NULL，再执行回填更新，随后可以再设为 NOT NULL（如果业务允许）。迁移脚本应尽可能保持 idempotent 且包含回滚与验证步骤。

## 建议
- 在迁移中避免一次性做大规模的阻塞式更新；对于需要迁移/回填的字段，采用：
  1. Schema change: 放宽约束（允许 NULL）
  2. Backfill in batches
  3. Tighten constraint（如果需要）
- 在迁移中记录每步的执行时间与受影响行数，便于回滚与监控
- 在 PR 模板中加入运维步骤：`alembic upgrade head`（需在部署前执行）
