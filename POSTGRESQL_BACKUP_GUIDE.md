# PostgreSQL 数据库备份和恢复功能 - 使用指南

**更新日期**: 2025-12-05  
**版本**: 2.0  
**适用数据库**: PostgreSQL 和 SQLite

---

## 📋 功能概览

系统现已完全支持PostgreSQL和SQLite双数据库备份和恢复功能。

### ✅ 新增功能

1. **PostgreSQL备份支持**
   - 使用 `pg_dump` 导出SQL文件
   - 支持压缩备份（.sql.gz格式）
   - 自动添加时间戳
   - 不包含所有者和权限信息（便于跨环境迁移）

2. **PostgreSQL恢复支持**
   - 使用 `pg_restore` 恢复压缩备份
   - 使用 `psql` 恢复SQL文件
   - 恢复前自动备份当前数据库
   - 支持错误处理和超时控制

3. **多格式文件验证**
   - 验证SQLite数据库文件（.db）
   - 验证PostgreSQL SQL文件（.sql）
   - 验证压缩备份文件（.sql.gz）
   - 检测文件完整性和有效性

4. **前端界面优化**
   - 根据数据库类型显示对应功能
   - 区分SQLite和PostgreSQL备份
   - 显示压缩状态和文件类型
   - 支持多格式文件上传

---

## 🔧 环境准备

### Windows系统

1. **下载PostgreSQL**
   ```
   访问: https://www.postgresql.org/download/windows/
   下载并安装PostgreSQL（包含客户端工具）
   ```

2. **配置环境变量**
   ```
   添加到系统PATH:
   C:\Program Files\PostgreSQL\{version}\bin
   ```

3. **验证安装**
   ```powershell
   pg_dump --version
   pg_restore --version
   psql --version
   ```

### Linux系统

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-client

# CentOS/RHEL
sudo yum install postgresql

# 验证
pg_dump --version
```

### macOS系统

```bash
# 使用Homebrew
brew install postgresql

# 验证
pg_dump --version
```

---

## 📖 使用方法

### 1. 创建备份

#### 通过Web界面
1. 访问 `http://your-server/admin/database`
2. 点击"立即备份"按钮
3. 系统自动创建压缩备份文件

#### 通过Python代码
```python
from app import create_app
from app.utils.db_management import backup_database

app = create_app()
with app.app_context():
    # 创建压缩备份
    result = backup_database(compress=True)
    if result.get('success'):
        print(f"备份成功: {result['backup_filename']}")
    else:
        print(f"备份失败: {result['message']}")
```

#### 备份文件命名规则
- **PostgreSQL**: `postgresql_backup_20251205_153408.sql.gz`
- **SQLite**: `app_backup_20251205_153408.db`

### 2. 恢复备份

#### 通过Web界面
1. 访问数据库管理页面
2. 在备份列表中找到要恢复的备份
3. 点击"恢复"按钮
4. 系统会自动备份当前数据库后再恢复

#### 通过Python代码
```python
from app.utils.db_management import restore_database

# 恢复指定备份（自动备份当前数据库）
result = restore_database('postgresql_backup_20251205_153408.sql.gz', auto_backup=True)
if result.get('success'):
    print("恢复成功")
```

### 3. 导入备份文件

#### 通过Web界面上传
1. 点击"导入数据库文件"
2. 选择文件（支持 .db, .sql, .sql.gz）
3. 点击"导入"按钮
4. 系统自动验证并恢复

#### 支持的文件格式
- `.db` - SQLite数据库文件
- `.sql` - PostgreSQL SQL转储文件
- `.sql.gz` - PostgreSQL压缩备份文件

### 4. 管理备份文件

#### 查看备份列表
```python
from app.utils.db_management import list_backups

# 获取所有备份
result = list_backups()
backups = result.get('backups', [])

# 按数据库类型筛选
postgresql_backups = list_backups(db_type='postgresql')
sqlite_backups = list_backups(db_type='sqlite')

# 按日期筛选
today_backups = list_backups(filter_date='today')
week_backups = list_backups(filter_date='week')
```

#### 删除备份
```python
from app.utils.db_management import delete_backup

result = delete_backup('postgresql_backup_20251205_153408.sql.gz')
```

---

## 🎯 备份策略建议

### 生产环境

1. **定期自动备份**
   - 每天凌晨3点自动备份
   - 保留最近30天的备份
   - 每周日创建长期备份

2. **重要操作前手动备份**
   - 数据库结构变更前
   - 大批量数据导入前
   - 系统升级前

3. **异地备份**
   - 将备份文件复制到其他服务器
   - 上传到云存储（OSS、S3等）

### 开发环境

1. **每日备份**
   - 开发结束前手动备份
   - 重要功能完成后备份

2. **测试前备份**
   - 执行破坏性测试前
   - 性能测试前

---

## 📊 备份文件信息

### PostgreSQL压缩备份

```
文件名: postgresql_backup_20251205_153408.sql.gz
格式: pg_dump自定义压缩格式 (-F c)
特点:
  - 压缩比约5-10倍
  - 包含完整数据库结构和数据
  - 不包含所有者和权限信息
  - 支持选择性恢复
```

### SQLite备份

```
文件名: app_backup_20251205_153408.db
格式: SQLite数据库文件副本
特点:
  - 直接文件复制
  - 100%数据完整性
  - 可以直接打开查看
  - 恢复速度快
```

---

## ⚠️ 注意事项

### 1. PostgreSQL备份

- **需要客户端工具**: 必须安装`pg_dump`和`pg_restore`
- **密码处理**: 系统自动通过环境变量`PGPASSWORD`传递密码
- **超时设置**: 备份超时5分钟，恢复超时10分钟
- **权限问题**: 确保数据库用户有足够权限

### 2. 恢复操作

- **自动备份**: 恢复前会自动创建当前数据库备份
- **数据丢失风险**: 恢复会覆盖当前数据，请谨慎操作
- **连接中断**: 恢复期间不要关闭浏览器
- **大数据库**: 大数据库恢复可能需要较长时间

### 3. 文件管理

- **存储位置**: 所有备份存储在`backups/`目录
- **磁盘空间**: 定期清理旧备份，避免占用过多空间
- **文件权限**: 确保应用有读写备份目录的权限

---

## 🔍 故障排查

### 问题1: pg_dump命令不存在

**错误信息**:
```
pg_dump命令不存在，请安装PostgreSQL客户端工具
```

**解决方法**:
1. 安装PostgreSQL客户端（见环境准备章节）
2. 配置PATH环境变量
3. 重启终端/服务
4. 验证: `pg_dump --version`

### 问题2: 备份失败 - 连接超时

**可能原因**:
- 数据库服务未启动
- 网络连接问题
- 防火墙阻止
- 数据库地址错误

**解决方法**:
1. 检查数据库连接配置
2. 测试数据库连接: `psql -h host -U user -d database`
3. 检查防火墙设置
4. 查看数据库日志

### 问题3: 恢复失败 - 权限不足

**错误信息**:
```
ERROR: must be owner of table xxx
```

**解决方法**:
1. 使用`--no-owner`选项（已默认启用）
2. 使用超级用户恢复
3. 修改备份文件权限设置

### 问题4: 文件验证失败

**可能原因**:
- 文件损坏
- 格式不正确
- 压缩文件损坏

**解决方法**:
1. 重新创建备份
2. 检查文件完整性
3. 使用其他工具验证文件

---

## 📈 性能优化

### 备份优化

1. **压缩备份**
   - 使用压缩格式减小文件大小
   - 节省存储空间
   - 加快传输速度

2. **并行处理**（未来版本）
   - 大表并行导出
   - 提高备份速度

3. **增量备份**（未来版本）
   - 仅备份变更数据
   - 减少备份时间

### 恢复优化

1. **预检查**
   - 验证备份文件
   - 检查磁盘空间
   - 确认数据库连接

2. **分批恢复**
   - 大数据库分批导入
   - 避免内存溢出

---

## 🔐 安全建议

1. **备份加密**（推荐）
   ```bash
   # 加密备份文件
   gpg -c backup.sql.gz
   
   # 解密
   gpg backup.sql.gz.gpg
   ```

2. **访问控制**
   - 仅管理员可访问备份功能
   - 限制备份文件访问权限

3. **审计日志**
   - 所有备份/恢复操作记录日志
   - 定期审查操作记录

---

## 📞 技术支持

如果遇到问题：

1. **查看日志**
   ```python
   # 在app.py中启用详细日志
   app.config['SQLALCHEMY_ECHO'] = True
   ```

2. **运行测试脚本**
   ```bash
   python test_postgresql_backup.py
   ```

3. **查看错误追踪**
   - 备份/恢复失败时会返回完整错误信息
   - 检查`trace`字段获取详细堆栈

---

## 📝 更新日志

### v2.0 (2025-12-05)

**新增**:
- ✅ PostgreSQL完整备份支持
- ✅ PostgreSQL恢复功能
- ✅ 压缩备份支持
- ✅ 多格式文件验证
- ✅ 前端界面优化
- ✅ 自动备份功能

**改进**:
- ✅ 备份列表显示数据库类型
- ✅ 显示压缩状态
- ✅ 优化错误提示信息
- ✅ 增强文件验证

**修复**:
- ✅ 修复SQLite备份兼容性
- ✅ 修复时间戳处理
- ✅ 修复文件路径问题

### v1.0

**初始功能**:
- SQLite数据库备份
- SQLite数据库恢复
- 基础备份管理

---

**文档维护**: IT部门  
**最后更新**: 2025-12-05
