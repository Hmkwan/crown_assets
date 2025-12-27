# 数据库迁移指南

## 📋 概述

本系统支持从 SQLite 迁移到以下数据库:
- ✅ **MySQL/MariaDB**
- ✅ **Microsoft SQL Server**
- ✅ **PostgreSQL**

> 注意：历史的自动转换脚本（`scripts/sqlite_to_*` 系列）已弃用并移到 `docs/legacy/`。当前运行时不再直接支持 `.db` 导入，推荐导出 SQLite SQL 转储并按需清理后导入目标数据库。

## 🔄 迁移方式

### 方式一: 在线导出SQL文件（注意）

1. **登录管理员账号**
2. **进入"数据库管理"页面**
3. **说明**:
   - 页面保留 "导出为 PostgreSQL" 的导出支持
   - "导出为 MySQL" 和 "导出为 SQL Server" 的自动转换按钮已禁用（历史功能已移除）

4. **下载生成的SQL文件或使用 PostgreSQL SQL 转储 (.sql/.sql.gz)**
5. **在目标数据库执行SQL**

如果需要历史自动转换脚本，请参阅 `docs/legacy/`（脚本已归档，使用需谨慎并在测试环境验证）。

### 方式二: 命令行导出（推荐导出为 SQL 转储）

```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 导出 SQLite SQL 转储（推荐）
sqlite3 app.db .dump > migrations/app_db_dump.sql
# 之后请手动清理或转换不兼容的语法（例如 PRAGMA、sqlite_sequence、AUTOINCREMENT 语法等），或参阅 docs/legacy/ 获取历史脚本与建议
```

## 🎯 迁移步骤详解

### 迁移到 MySQL

#### 1. 导出SQLite数据
```powershell
python scripts/sqlite_to_mysql.py --sqlite app.db --out migrations/mysql_dump.sql --src-tz UTC --dst-tz Asia/Shanghai
```

#### 2. 在MySQL创建数据库
```sql
CREATE DATABASE it_asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE it_asset_db;
```

#### 3. 导入SQL文件
```bash
mysql -u root -p it_asset_db < migrations/mysql_dump.sql
```

#### 4. 修改config.py
```python
# 注释掉 SQLite 配置
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# 启用 MySQL 配置
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://用户名:密码@localhost/it_asset_db?charset=utf8mb4'
```

#### 5. 安装MySQL驱动
```powershell
pip install pymysql cryptography
```

#### 6. 重启应用
```powershell
python app.py
```

### 迁移到 SQL Server

#### 1. 导出数据
```powershell
python scripts/sqlite_to_mssql.py --sqlite app.db --out migrations/mssql_dump.sql
```

#### 2. 在SQL Server创建数据库
```sql
CREATE DATABASE ITAssetDB;
GO
USE ITAssetDB;
GO
```

#### 3. 执行SQL文件
在 SQL Server Management Studio (SSMS) 中打开并执行 `mssql_dump.sql`

#### 4. 修改config.py
```python
# 方式1: 使用 Windows 身份验证
SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://服务器名/ITAssetDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

# 方式2: 使用 SQL Server 身份验证
SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://用户名:密码@服务器名/ITAssetDB?driver=ODBC+Driver+17+for+SQL+Server'
```

#### 5. 安装SQL Server驱动
```powershell
pip install pyodbc
```

还需要安装 ODBC Driver:
- 下载: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- 推荐版本: ODBC Driver 17 for SQL Server

#### 6. 重启应用

### 迁移到 PostgreSQL

#### 1. 导出数据
```powershell
python scripts/sqlite_to_postgresql.py --sqlite app.db --out migrations/postgresql_dump.sql
```

#### 2. 创建数据库
```sql
CREATE DATABASE it_asset_db WITH ENCODING 'UTF8';
\c it_asset_db
```

#### 3. 导入数据
```bash
psql -U postgres -d it_asset_db -f migrations/postgresql_dump.sql
```

#### 4. 修改config.py
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://用户名:密码@localhost/it_asset_db'
```

#### 5. 安装PostgreSQL驱动
```powershell
pip install psycopg2-binary
```

#### 6. 重启应用

## ⚠️ 重要注意事项

### 1. 备份数据
**迁移前务必备份!**
```powershell
# 在"数据库管理"页面点击"立即备份"
# 或运行
python scripts/backup_db.py
```

### 2. 时区转换
- SQLite中通常存储UTC时间
- 导出时自动转换为Asia/Shanghai时区
- 如需其他时区,修改 `--dst-tz` 参数

### 3. 数据类型映射

| SQLite | MySQL | SQL Server | PostgreSQL |
|--------|-------|------------|------------|
| INTEGER | INT | INT | INTEGER |
| TEXT | TEXT | NVARCHAR(MAX) | TEXT |
| REAL | DOUBLE | FLOAT | DOUBLE PRECISION |
| BLOB | BLOB | VARBINARY(MAX) | BYTEA |
| BOOLEAN | TINYINT(1) | BIT | BOOLEAN |
| DATETIME | DATETIME | DATETIME2 | TIMESTAMP |

### 4. 自增ID处理
- **MySQL**: AUTO_INCREMENT
- **SQL Server**: IDENTITY(1,1)
- **PostgreSQL**: SERIAL
- 导出脚本会自动处理

### 5. 外键约束
当前导出脚本**不包含外键约束**,需要手动添加或通过Flask-SQLAlchemy的模型定义自动创建。

### 6. 索引优化
导出后建议手动添加索引:
```sql
-- MySQL 示例
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_department ON equipment(department_id);
CREATE INDEX idx_repair_order_status ON repair_order(status);
```

## 🔧 故障排除

### 问题1: 字符编码错误
**MySQL**:
```sql
ALTER DATABASE it_asset_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题2: 驱动无法找到
**Windows SQL Server**:
- 检查ODBC驱动是否安装
- 运行 `odbcad32.exe` 查看可用驱动
- 确保版本匹配 (Driver 17, 18)

### 问题3: 连接超时
- 检查防火墙设置
- 确认数据库服务正在运行
- 验证用户名密码正确

### 问题4: 权限不足
确保数据库用户有足够权限:
```sql
-- MySQL
GRANT ALL PRIVILEGES ON it_asset_db.* TO '用户名'@'localhost';
FLUSH PRIVILEGES;

-- PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE it_asset_db TO 用户名;
```

## 📊 性能对比

| 数据库 | 适用场景 | 优点 | 缺点 |
|--------|---------|------|------|
| SQLite | 小型应用,单用户 | 零配置,轻量 | 并发差,功能少 |
| MySQL | 中小型应用,多用户 | 成熟稳定,生态好 | 配置复杂 |
| PostgreSQL | 企业级应用 | 功能强大,标准兼容 | 资源占用较高 |
| SQL Server | Windows环境,企业级 | 工具完善,性能好 | 商业授权,仅Windows |

## 🚀 建议

1. **小型部署 (< 10用户)**: 保持SQLite即可
2. **中型部署 (10-100用户)**: 迁移到MySQL
3. **大型部署 (> 100用户)**: 考虑PostgreSQL或SQL Server
4. **企业环境**: 根据现有基础设施选择

## 📞 技术支持

如遇到问题,请检查:
1. 数据库服务是否运行
2. 连接字符串是否正确
3. 驱动是否已安装
4. 防火墙端口是否开放
5. 日志文件中的错误信息

---

**最后更新**: 2025-11-29
**版本**: v2.0
