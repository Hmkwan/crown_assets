# 历史（Legacy）: SQLite 迁移与备份资料

本目录用于归档与说明与旧版 SQLite 相关的脚本、转储和迁移文档。仓库已移除对 SQLite 的运行时支持；下列资料仅供迁移参考或回滚审计使用。

重要说明
- 运行时已不再支持 `.db` 文件的导入/恢复。请使用 PostgreSQL SQL 转储（`.sql` / `.sql.gz`）或专业迁移工具。
- 若需要将 SQLite 数据迁移到 PostgreSQL，请先导出 SQLite 的 SQL（例如：`sqlite3 app.db .dump > backup.sql`），并参阅下面的资源完成转换与语法调整。

常见资源位置（仓库内）
- scripts/sqlite_to_mysql.py — （历史）将 SQLite 转换为 MySQL 格式的脚本（已归档）。
- scripts/sqlite_to_mssql.py — （历史）将 SQLite 转换为 SQL Server 的脚本（已归档）。
- migrations/README_SQLite_to_RDBMS.md — 迁移说明文档（历史文档，包含转换建议与注意点）。
- migrations/*_dump_*.sql — 由历史转换脚本生成的 SQL 转储文件（供参考）。

操作建议
1. 导出 SQLite 数据：
   - `sqlite3 app.db .dump > backup.sql`
2. 清理 SQLite 特有语句（例如 PRAGMA、sqlite_sequence、AUTOINCREMENT 行为修正等），确保 SQL 兼容 PostgreSQL。
3. 在测试环境中导入并运行 `alembic upgrade head` 以应用迁移脚本，修复可能的约束/类型差异。

如果你需要我们帮助完成迁移（清理脚本、检视并生成 PostgreSQL 兼容 SQL），请发起请求并提供 sqlite 转储文件或允许我们访问数据库转储。
