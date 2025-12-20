# 从 SQLite 导出到 MySQL / SQL Server

此文档说明如何将当前项目的 SQLite 数据库（例如 `app.db`）导出为可导入到 MySQL 或 SQL Server 的 SQL 文件。脚本位于 `scripts/` 目录：

- `scripts/sqlite_to_mysql.py` — 生成 MySQL 兼容的 SQL 转储
- `scripts/sqlite_to_mssql.py` — 生成 SQL Server 兼容的 SQL 转储

重要提示
- 请在操作前备份原始 `app.db` 文件。导入到其他数据库前请先在测试环境验证转储内容。
- 默认情况下，脚本会把看起来像 ISO 时间字符串的字段从 `UTC` 转为 `Asia/Shanghai`（北京时间）。可通过参数 `--src-tz` / `--dst-tz` 覆盖。

快速使用示例（在项目根目录下）：

PowerShell 示例：

```powershell
# 激活虚拟环境（如果使用）
& .\.venv\Scripts\Activate.ps1
# 生成 MySQL 转储
python scripts/sqlite_to_mysql.py --sqlite app.db --out migrations/app_db_mysql_dump.sql --src-tz UTC --dst-tz Asia/Shanghai
# 生成 SQL Server 转储
python scripts/sqlite_to_mssql.py --sqlite app.db --out migrations/app_db_mssql_dump.sql --src-tz UTC --dst-tz Asia/Shanghai
```

导入 MySQL（示例）：

1. 在目标 MySQL 中创建数据库（例如 `app_db`），并确保字符集为 `utf8mb4`。
2. 将生成的 `migrations/app_db_mysql_dump.sql` 文件上传到服务器或通过命令行访问：

```bash
mysql -u <user> -p -h <host> app_db < migrations/app_db_mysql_dump.sql
```

导入 SQL Server（示例）：

- 使用 SQL Server Management Studio（SSMS）打开生成的 `migrations/app_db_mssql_dump.sql` 并执行，或使用 `sqlcmd`：

```powershell
sqlcmd -S <server> -U <user> -P <password> -d <database> -i migrations\app_db_mssql_dump.sql
```

兼容性与限制
- 脚本对常见的 SQLite 数据类型进行了简单的映射（INTEGER、TEXT、REAL、BLOB、BOOLEAN、DATE/TIME）。复杂类型、CHECK/UNIQUE 约束、触发器、视图、索引与外键约束可能需要手动调整。
- AUTOINCREMENT 行为在目标数据库中需确认：脚本会把主键定义为 PRIMARY KEY，但不会自动检测/迁移 `sqlite_sequence` 中的值作为自增起始值。可在导入后使用 `ALTER TABLE ... AUTO_INCREMENT = <max+1>`（MySQL）或 `DBCC CHECKIDENT`（SQL Server）设置。
- 大型数据库导出/导入可能需要分批处理或工具（mysqldump、SSMS 导出/导入）以提高效率与可靠性。

后续建议
- 在准备迁移到生产 RDBMS 前，在测试实例上执行完整导出/导入，并对数据完整性（行数、约束、时间字段）进行核对。
- 如果计划长期用 MySQL/SQL Server 作为主数据库，建议引入 Alembic / 专业迁移工具并逐步把模型迁移到 SQLAlchemy 的迁移脚本中，避免手动 SQL 的可维护性问题。

如需，我可以：
- 帮你执行一次本地导出并把生成的 SQL 文件存到 `migrations/` 下；
- 协助将导出文件调整为完全兼容你的 MySQL 或 SQL Server 版本（例如处理索引、约束、自增起始值）；
- 为项目配置 Alembic 迁移（如果你希望未来用迁移管理 schema 变更）。
