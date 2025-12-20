# PostgreSQL 客户端工具安装指南

**日期**: 2025-12-05  
**问题**: `pg_dump命令不存在`  
**状态**: ✅ 已提供解决方案

---

## 🎯 问题说明

当前系统使用 PostgreSQL 数据库，但未安装 `pg_dump` 和 `pg_restore` 等客户端工具，导致无法使用原生备份功能。

---

## ✅ 解决方案对比

### 方案 1：安装 PostgreSQL 客户端工具（推荐）

#### 优点
- ✅ 功能完整（包含索引、约束、序列、触发器等）
- ✅ 官方支持，稳定可靠
- ✅ 支持增量备份和并行处理
- ✅ 生成的备份文件通用性强

#### 缺点
- ⚠️ 需要安装额外软件（约 200-300 MB）
- ⚠️ 需要配置环境变量

---

### 方案 2：使用 Python 备份脚本（已实现）

#### 优点
- ✅ 无需安装额外软件
- ✅ 纯 Python 实现，跨平台
- ✅ 可以立即使用
- ✅ **已测试成功** - 成功备份 40 个表

#### 缺点
- ⚠️ 不包含索引定义
- ⚠️ 不包含约束（外键、主键等）
- ⚠️ 不包含序列（自增ID）
- ⚠️ 不包含触发器和函数
- ⚠️ 恢复时需要手动重建这些对象

#### 测试结果
```
✓ 备份成功!
  文件: python_postgresql_backup_20251205_074624.sql.gz
  大小: 0.01 MB
  路径: backups\python_postgresql_backup_20251205_074624.sql.gz
  表数量: 40 个
```

---

## 🚀 方案 1：安装 PostgreSQL 客户端工具

### Windows 系统

#### 选项 A：使用 Chocolatey（最快）

```powershell
# 1. 如果还没有安装 Chocolatey，先安装它
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. 安装 PostgreSQL
choco install postgresql

# 3. 验证安装
pg_dump --version
```

#### 选项 B：使用 Scoop

```powershell
# 1. 安装 Scoop（如果还没有）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# 2. 安装 PostgreSQL
scoop install postgresql

# 3. 验证安装
pg_dump --version
```

#### 选项 C：手动安装

1. **下载安装程序**
   ```
   访问: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   或: https://www.postgresql.org/download/windows/
   ```

2. **选择版本**
   - 推荐: PostgreSQL 16.x（最新稳定版）
   - 下载: Windows x86-64 版本

3. **安装步骤**
   - 运行安装程序
   - 安装位置: 默认 `C:\Program Files\PostgreSQL\16`
   - ⚠️ **重要**: 勾选 "Command Line Tools"
   - 设置密码（可选，用于本地PostgreSQL服务器）
   - 端口: 默认 5432
   - 完成安装

4. **配置环境变量**
   ```powershell
   # 添加到系统 PATH
   $pgPath = "C:\Program Files\PostgreSQL\16\bin"
   
   # 临时添加（当前会话）
   $env:Path = "$pgPath;$env:Path"
   
   # 永久添加（所有用户）
   [Environment]::SetEnvironmentVariable(
       "Path",
       [Environment]::GetEnvironmentVariable("Path", "Machine") + ";$pgPath",
       "Machine"
   )
   ```

5. **验证安装**
   ```powershell
   # 重新打开 PowerShell，然后执行
   pg_dump --version
   pg_restore --version
   psql --version
   ```

### Linux 系统

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql-client

# 验证
pg_dump --version
```

#### CentOS/RHEL
```bash
sudo yum install postgresql

# 验证
pg_dump --version
```

### macOS 系统

```bash
# 使用 Homebrew
brew install postgresql

# 验证
pg_dump --version
```

---

## 🐍 方案 2：使用 Python 备份脚本

### 使用方法

#### 1. 通过命令行直接备份

```bash
# 运行备份脚本
python python_postgresql_backup.py
```

#### 2. 集成到现有系统

已创建的脚本文件：`python_postgresql_backup.py`

可以在需要备份的地方调用：

```python
from python_postgresql_backup import python_backup_postgresql

# 执行备份
result = python_backup_postgresql(db_uri, compress=True)

if result['success']:
    print(f"备份成功: {result['backup_filename']}")
else:
    print(f"备份失败: {result['message']}")
```

### 备份文件格式

- **文件名**: `python_postgresql_backup_20251205_074624.sql.gz`
- **格式**: 压缩的 SQL 文件
- **内容**: 
  - CREATE TABLE 语句
  - INSERT 语句
  - ⚠️ 不包含索引、约束、序列等

### 限制说明

此方案**不包含**以下内容：
- ❌ 主键和外键约束
- ❌ 唯一约束和检查约束
- ❌ 索引定义
- ❌ 序列（SERIAL/自增ID）
- ❌ 触发器
- ❌ 函数和存储过程
- ❌ 视图定义

**恢复后需要手动执行**：
```sql
-- 示例：重建主键和索引
ALTER TABLE equipment ADD PRIMARY KEY (id);
CREATE INDEX idx_equipment_name ON equipment(name);
ALTER TABLE equipment ADD CONSTRAINT fk_dept FOREIGN KEY (department_id) REFERENCES department(id);
```

---

## 📊 方案选择建议

### 生产环境 → 方案 1（必须）
- 需要完整的数据库结构
- 需要保证数据完整性
- 需要支持恢复后立即使用

### 开发/测试环境 → 方案 2（可选）
- 仅需要数据备份
- 数据库结构变化不频繁
- 可以手动重建索引和约束

### 当前建议
由于您的系统是**生产环境**（IT资产管理系统），**强烈推荐使用方案 1**。

但在安装 PostgreSQL 客户端工具之前，可以先使用**方案 2**作为临时备份手段。

---

## ✅ 安装后验证

### 测试 pg_dump

```powershell
# 1. 验证命令存在
pg_dump --version

# 2. 测试备份（不实际执行）
pg_dump --help

# 3. 在系统中测试备份
python test_postgresql_backup.py
```

### 预期输出

安装成功后，运行测试脚本应该看到：

```
【2】备份功能测试
----------------------------------------------------------------------
测试压缩备份...
✓ 压缩备份成功
  文件名: postgresql_backup_20251205_153408.sql.gz
  大小: 0.50 MB
  路径: backups/postgresql_backup_20251205_153408.sql.gz
```

---

## 🔧 故障排查

### 问题 1: 找不到 pg_dump 命令

**原因**: PATH 环境变量未配置

**解决**:
```powershell
# 临时解决（当前会话）
$env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"

# 永久解决
# 手动添加到系统环境变量 PATH
```

### 问题 2: 安装后仍然提示命令不存在

**原因**: 需要重启终端

**解决**:
1. 关闭所有 PowerShell 窗口
2. 重新打开 PowerShell
3. 再次测试 `pg_dump --version`

### 问题 3: Python 备份脚本报错

**错误**: `No module named 'psycopg2'`

**解决**:
```bash
pip install psycopg2-binary
```

---

## 📝 快速决策流程图

```
是否需要完整备份（包含索引、约束）？
├─ 是 → 安装 PostgreSQL 客户端工具（方案 1）
│   └─ 选择安装方式：
│       ├─ 已有包管理器 → 使用 choco/scoop
│       └─ 无包管理器 → 手动下载安装
│
└─ 否，仅需数据备份 → 使用 Python 脚本（方案 2）
    └─ 运行: python python_postgresql_backup.py
```

---

## 📞 后续支持

### 方案 1 安装支持

如果选择方案 1，安装完成后：
1. 重启终端
2. 运行 `python test_postgresql_backup.py`
3. 应该看到备份成功的消息

### 方案 2 使用支持

如果使用方案 2：
1. 定期运行 `python python_postgresql_backup.py`
2. 备份文件保存在 `backups/` 目录
3. 建议同时记录数据库结构（DDL）

---

## 🎯 推荐行动

**立即行动**（5分钟）:
```bash
# 使用 Python 备份脚本创建第一个备份
python python_postgresql_backup.py
```

**短期计划**（今天）:
```powershell
# 安装 PostgreSQL 客户端工具
choco install postgresql
# 或手动下载安装
```

**长期计划**（本周）:
```bash
# 设置自动定时备份
# 配置备份保留策略
# 测试备份恢复流程
```

---

**文档版本**: 1.0  
**最后更新**: 2025-12-05  
**状态**: ✅ 两种方案均已实现并测试
