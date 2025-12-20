# PostgreSQL数据库迁移指南

## 概述

本指南帮助你将设备管理系统从SQLite迁移到PostgreSQL数据库(`it_asset`)。

---

## 准备工作

### 1. 安装PostgreSQL

**Windows:**
- 下载安装: https://www.postgresql.org/download/windows/
- 或使用Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15`

**确认PostgreSQL运行:**
```powershell
# 检查PostgreSQL服务状态
Get-Service postgresql*

# 或检查端口
Test-NetConnection localhost -Port 5432
```

### 2. 创建数据库

使用psql命令行工具:

```bash
# 登录PostgreSQL (默认用户postgres)
psql -U postgres

# 在psql中执行:
CREATE DATABASE it_asset;
\q
```

或使用SQL命令:
```powershell
psql -U postgres -c "CREATE DATABASE it_asset;"
```

### 3. 安装Python依赖

```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装PostgreSQL驱动
pip install psycopg2-binary
```

---

## 迁移方法

### 方法一: 自动迁移脚本 (推荐)

使用提供的自动迁移脚本:

```powershell
# 1. 确保虚拟环境已激活
.\.venv\Scripts\Activate.ps1

# 2. 运行迁移脚本
python migrate_to_postgresql.py
```

**脚本会自动:**
- 检查SQLite数据库
- 测试PostgreSQL连接
- 显示所有表和记录数
- 询问确认后开始迁移
- 创建表结构
- 复制所有数据
- 显示迁移结果

**如果数据库连接参数不同,请编辑 `migrate_to_postgresql.py` 文件顶部:**
```python
PG_HOST = 'localhost'      # PostgreSQL主机
PG_PORT = '5432'           # PostgreSQL端口
PG_USER = 'postgres'       # PostgreSQL用户名
PG_PASSWORD = 'postgres'   # PostgreSQL密码
PG_DATABASE = 'it_asset'   # 数据库名
```

---

### 方法二: 手动迁移

#### 步骤1: 导出SQLite数据

```powershell
# 使用SQLite导出为SQL
sqlite3 app.db .dump > backup.sql
```

#### 步骤2: 修改SQL文件

SQLite和PostgreSQL的SQL语法有差异,需要调整:

```powershell
# 使用文本编辑器替换:
# 1. 删除 SQLite 特有语句
#    - PRAGMA...
#    - BEGIN TRANSACTION; 和 COMMIT;
#
# 2. 修改数据类型
#    - INTEGER PRIMARY KEY -> SERIAL PRIMARY KEY
#    - DATETIME -> TIMESTAMP
#
# 3. 修改布尔值
#    - 0/1 -> FALSE/TRUE
```

#### 步骤3: 导入到PostgreSQL

```bash
psql -U postgres -d it_asset -f backup.sql
```

---

## 配置应用使用PostgreSQL

### 选项A: 修改config.py (已完成)

`config.py` 已经更新为默认使用PostgreSQL:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/it_asset'
```

如果你的数据库参数不同,请修改此行。

### 选项B: 使用环境变量 (.env文件)

创建 `.env` 文件 (参考 `.env.example`):

```bash
DATABASE_URL=postgresql://你的用户名:你的密码@localhost:5432/it_asset
```

应用会优先使用环境变量中的配置。

---

## 验证迁移

### 1. 测试数据库连接

```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 测试连接
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print('数据库连接成功!'); print(f'表数量: {len(db.metadata.tables)}')"
```

### 2. 检查数据

```bash
# 登录PostgreSQL
psql -U postgres -d it_asset

# 查看所有表
\dt

# 查看用户表记录数
SELECT COUNT(*) FROM "user";

# 查看设备表记录数
SELECT COUNT(*) FROM equipment;

# 退出
\q
```

### 3. 启动应用测试

```powershell
# 启动Flask应用
python app.py
```

访问 http://localhost:5000 测试功能是否正常。

---

## 常见问题

### Q1: psycopg2安装失败

**错误:** `error: Microsoft Visual C++ 14.0 is required`

**解决:**
```powershell
# 使用二进制版本
pip install psycopg2-binary
```

### Q2: 连接被拒绝

**错误:** `could not connect to server: Connection refused`

**检查:**
1. PostgreSQL服务是否运行
2. 端口5432是否开放
3. pg_hba.conf是否允许本地连接

### Q3: 数据库不存在

**错误:** `database "it_asset" does not exist`

**解决:**
```bash
psql -U postgres -c "CREATE DATABASE it_asset;"
```

### Q4: 认证失败

**错误:** `password authentication failed for user "postgres"`

**解决:**
1. 确认PostgreSQL密码
2. 修改 `config.py` 或 `.env` 中的密码
3. 或重置PostgreSQL密码

### Q5: 中文乱码

**解决:**
创建数据库时指定编码:
```sql
CREATE DATABASE it_asset
  ENCODING 'UTF8'
  LC_COLLATE 'zh_CN.UTF-8'
  LC_CTYPE 'zh_CN.UTF-8';
```

### Q6: 迁移后序列值不正确

**问题:** 新增记录时主键冲突

**解决:**
```sql
-- 为每个表重置序列
SELECT setval('user_id_seq', (SELECT MAX(id) FROM "user"));
SELECT setval('equipment_id_seq', (SELECT MAX(id) FROM equipment));
-- 对其他表重复此操作
```

或运行:
```python
# 自动重置所有序列
python -c "
from app import create_app, db
from sqlalchemy import text
app = create_app()
with app.app_context():
    tables = db.metadata.tables.keys()
    for table in tables:
        try:
            db.session.execute(text(f\"SELECT setval('{table}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {table}));\"))
            db.session.commit()
            print(f'✓ {table}')
        except:
            pass
"
```

---

## 性能优化建议

### 1. 创建索引

```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_repair_order_status ON repair_order(status);
CREATE INDEX idx_user_email ON "user"(email);
```

### 2. 定期维护

```sql
-- 分析表统计信息
ANALYZE;

-- 清理死元组
VACUUM;

-- 完整清理和分析
VACUUM ANALYZE;
```

### 3. 配置连接池

`config.py` 已配置连接池参数:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'max_overflow': 20,
    'pool_pre_ping': True,
}
```

---

## 回滚到SQLite

如果需要回退到SQLite:

1. 修改 `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
```

2. 或删除 `.env` 文件中的 `DATABASE_URL`

3. 重启应用

---

## Docker部署配置

如果使用Docker Compose,更新 `docker-compose.yml`:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/it_asset
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=it_asset
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

---

## 支持

如遇到问题:
1. 检查PostgreSQL日志: `C:\Program Files\PostgreSQL\15\data\log\`
2. 查看Flask应用日志
3. 启用SQL日志: `config.py` 中设置 `SQLALCHEMY_ECHO = True`

---

**迁移完成后记得:**
- ✅ 测试所有核心功能
- ✅ 备份PostgreSQL数据库
- ✅ 更新文档和部署说明
- ✅ 保留SQLite备份以防需要回滚
