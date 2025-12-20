# 系统迁移部署指南

## 📦 备份文件信息

**备份文件**: `project_backup_20251130_001405.zip`
**备份时间**: 2025-11-30 00:14:05
**文件大小**: 606.97 KB (压缩后)
**原始大小**: 3.30 MB
**压缩率**: 82.0%
**总文件数**: 223个

### 备份内容清单

✓ **应用代码** (116个文件, 2.39 MB)
  - app/ 目录下所有Python代码
  - 包含所有模块、路由、服务、工具类
  - 完整的HTML模板和静态资源

✓ **数据库文件** (336 KB)
  - app.db (包含所有用户、设备、工单数据)

✓ **配置文件**
  - app.py (应用入口)
  - config.py (配置)
  - requirements.txt (依赖列表)
  - alembic.ini (数据库迁移配置)

✓ **脚本工具** (62个文件)
  - 初始化脚本
  - 测试脚本
  - 工具脚本

✓ **文档资料** (12个Markdown文档)
  - 开发报告
  - 快速启动指南
  - 系统改进计划
  - 等等...

---

## 🚀 快速迁移步骤

### 第一步：解压备份文件

```powershell
# Windows PowerShell
Expand-Archive -Path "project_backup_20251130_001405.zip" -DestinationPath "C:\YourPath\ProjectName"
cd C:\YourPath\ProjectName
```

```bash
# Linux/Mac
unzip project_backup_20251130_001405.zip -d ~/YourPath/ProjectName
cd ~/YourPath/ProjectName
```

### 第二步：检查Python环境

**要求**: Python 3.7 或更高版本

```powershell
# 检查Python版本
python --version

# 应显示 Python 3.7.x 或更高
```

### 第三步：创建虚拟环境

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 第四步：安装依赖

```powershell
# 升级pip
python -m pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt
```

**依赖列表**:
- Flask 2.x
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Migrate
- 其他（见requirements.txt）

### 第五步：验证数据库

```powershell
# 检查数据库文件
ls app.db

# 如果数据库文件存在，跳过此步骤
# 如果不存在，需要初始化:
python init_db.py
python create_admin.py
```

### 第六步：启动服务

```powershell
# 开发模式（默认，调试已禁用）
python app.py

# 如果需要启用调试模式
$env:FLASK_DEBUG="True"
python app.py

# 生产模式（推荐使用Gunicorn或Waitress）
# Windows:
pip install waitress
waitress-serve --host=0.0.0.0 --port=5020 app:app

# Linux:
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5020 app:app
```

### 第七步：访问系统

打开浏览器访问:
- 本地: http://localhost:5020
- 局域网: http://your-ip:5020

**默认管理员账户**（如果使用备份的数据库）:
- 用户名: admin
- 密码: (原系统的密码)

---

## ⚙️ 环境配置调整

### 修改端口号

编辑 `app.py`:
```python
app.run(host='0.0.0.0', port=5020, debug=DEBUG_MODE)
# 改为你需要的端口，例如 port=8000
```

### 修改数据库路径

编辑 `config.py`:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
# 可以改为其他路径或数据库类型
```

### 配置密钥（重要！）

编辑 `config.py`:
```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
# 生产环境建议设置环境变量
```

生成新的密钥:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
# 将输出设置为 SECRET_KEY
```

---

## 🔧 性能优化（新设备）

### 1. CDN资源本地化（推荐）

如果网络较慢，建议下载CDN资源到本地:

```powershell
# 下载所有CDN资源
python download_cdn_resources.py

# 更新模板使用本地资源
python update_base_template.py

# 重启服务
```

**效果**: 页面加载速度提升60-80%

### 2. 启用生产模式

确保不设置 `FLASK_DEBUG` 环境变量，或设置为 False:

```powershell
# 不设置（默认禁用调试）
python app.py

# 或明确设置
$env:FLASK_DEBUG="False"
python app.py
```

### 3. 使用生产服务器

不要在生产环境使用内置开发服务器:

**Windows推荐 - Waitress**:
```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=5020 --threads=4 app:app
```

**Linux推荐 - Gunicorn**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5020 --timeout 120 app:app
```

### 4. 配置开机自启（Windows）

创建快捷方式或使用任务计划程序:

1. 创建启动脚本 `start_service.bat`:
```batch
@echo off
cd /d C:\YourPath\ProjectName
call .venv\Scripts\activate
waitress-serve --host=0.0.0.0 --port=5020 app:app
```

2. 将快捷方式放入启动文件夹:
   - Win+R 输入 `shell:startup`
   - 将 `start_service.bat` 快捷方式复制到该文件夹

---

## 🔍 故障排查

### 问题1: 无法启动服务

**错误**: `ModuleNotFoundError: No module named 'flask'`

**解决**:
```powershell
# 确认虚拟环境已激活
.\.venv\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题2: 数据库错误

**错误**: `sqlalchemy.exc.OperationalError`

**解决**:
```powershell
# 检查数据库文件权限
# 如果数据库损坏，使用备份或重新初始化
python init_db.py
python create_admin.py
```

### 问题3: 端口被占用

**错误**: `Address already in use`

**解决**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5020

# 终止进程
taskkill /PID <进程ID> /F

# 或修改端口号（见上文"修改端口号"）
```

### 问题4: 页面加载缓慢

**解决方案**:
1. 执行CDN资源本地化（见"性能优化"）
2. 确保调试模式已禁用
3. 使用生产服务器（Waitress/Gunicorn）
4. 检查网络连接

### 问题5: 静态文件404错误

**检查**:
```powershell
# 确认static目录存在
ls app\static

# 确认vendor目录存在（如果已执行CDN本地化）
ls app\static\vendor
```

---

## 📋 迁移检查清单

**部署前**:
- [ ] 备份文件已安全传输到新设备
- [ ] Python 3.7+ 已安装
- [ ] 网络连接正常

**部署中**:
- [ ] 解压备份文件成功
- [ ] 虚拟环境创建成功
- [ ] 依赖安装无错误
- [ ] 数据库文件存在且完整

**部署后**:
- [ ] 服务成功启动
- [ ] 可以访问登录页面
- [ ] 管理员账户可以登录
- [ ] 主要功能测试通过

**优化**:
- [ ] CDN资源本地化（可选但推荐）
- [ ] 调试模式已禁用
- [ ] 使用生产服务器
- [ ] 配置开机自启（如需要）

---

## 📞 技术支持

如遇到问题，请检查以下文档:
- `README_RESTORE.md` - 恢复说明
- `QUICK_START_GUIDE.md` - 快速启动指南
- `DEPLOYMENT_OPTIMIZATION_GUIDE.md` - 优化指南
- `DEVELOPMENT_REPORT.md` - 开发报告

---

## 🔄 后续维护

### 备份策略

建议定期备份:
```powershell
# 每周/每月运行一次
python create_backup.py
```

### 更新依赖

定期更新依赖包:
```powershell
pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt
```

### 数据库备份

除了完整备份，也可以单独备份数据库:
```powershell
# 备份
copy app.db app.db.backup

# 恢复
copy app.db.backup app.db
```

---

**迁移完成后，您的系统应该可以在新设备上正常运行！**

如有任何问题，请参考相关文档或联系技术支持。
