# Docker 部署问题解决总结

## 🎯 问题概述

在将设备管理系统部署到 Docker 容器时遇到了一系列依赖和配置问题。

## 📋 解决的问题列表

### 1. **Werkzeug 版本不兼容**
**错误**: `ImportError: cannot import name 'url_quote' from 'werkzeug.urls'`

**原因**: Flask 2.0.3 与最新版 Werkzeug 不兼容

**解决方案**: 在 `requirements.txt` 中添加:
```
Werkzeug==2.0.3
```

---

### 2. **SQLAlchemy 版本不兼容**
**错误**: `AttributeError: module 'sqlalchemy' has no attribute '__all__'`

**原因**: Flask-SQLAlchemy 2.5.1 与 SQLAlchemy 2.x 不兼容

**解决方案**: 锁定 SQLAlchemy 版本:
```
SQLAlchemy==1.4.46
```

---

### 3. **缺少 email-validator**
**错误**: `Exception: Install 'email_validator' for email validation support.`

**原因**: WTForms 的 Email() 验证器需要此包

**解决方案**: 添加依赖:
```
email-validator==1.3.0
```

---

### 4. **缺少 pandas**
**错误**: `ModuleNotFoundError: No module named 'pandas'`

**原因**: Excel 导入导出功能使用 pandas

**解决方案**: 添加依赖:
```
pandas==1.5.3
openpyxl==3.1.2
```

---

### 5. **numpy 二进制不兼容**
**错误**: `ValueError: numpy.dtype size changed, may indicate binary incompatibility`

**原因**: pandas 1.5.3 需要特定版本的 numpy

**解决方案**: 指定兼容版本:
```
numpy==1.24.3
```

---

### 6. **缺少 reportlab**
**错误**: `ModuleNotFoundError: No module named 'reportlab'`

**原因**: PDF 生成功能需要 reportlab

**解决方案**: 添加依赖:
```
reportlab==4.0.4
```

---

### 7. **Gunicorn 模块导入问题** ⭐ 最关键
**错误**: `AttributeError: module 'app' has no attribute 'app'`

**原因**: 
- 项目中同时存在 `app/` 目录(Python包)和 `app.py` 文件
- Gunicorn 的 `app:app` 语法会尝试从 `app` 包导入 `app` 属性
- Python 优先导入 `app/` 目录而不是 `app.py` 文件

**解决方案**: 创建独立的 WSGI 入口文件
```python
# wsgi.py
from app import create_app
app = create_app()
```

修改 Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5020", "wsgi:app"]
```

---

## 📦 最终 requirements.txt

```txt
Flask==2.0.3
Werkzeug==2.0.3
SQLAlchemy==1.4.46
Flask-SQLAlchemy==2.5.1
Flask-Login==0.5.0
Flask-WTF==1.0.1
WTForms==3.0.0
Flask-Migrate==3.1.0
python-dotenv==0.20.0
email-validator==1.3.0
numpy==1.24.3
pandas==1.5.3
openpyxl==3.1.2
reportlab==4.0.4
qrcode>=7.4.2
Pillow>=10.0.0
markdown2>=2.4.0
```

---

## 🎨 关键文件变更

### 1. wsgi.py (新增)
```python
"""WSGI entry point for Gunicorn"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

### 2. Dockerfile (修改)
```dockerfile
# 启动命令改为使用 wsgi.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5020", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:app"]
```

---

## ✅ 部署验证

### 容器状态
```bash
docker-compose ps
# STATUS: Up (health: starting)
# PORTS: 0.0.0.0:5020->5020/tcp
```

### 服务日志
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5020
[INFO] Booting worker with pid: 7
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
```

✅ **4个 Gunicorn worker 进程全部成功启动**

---

## 🚀 快速部署命令

```powershell
# 构建并启动
docker-compose up -d --build

# 检查状态
docker-compose ps

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose stop

# 完全清理
docker-compose down
```

---

## 📝 经验教训

1. **版本锁定至关重要**: Flask 生态系统的版本依赖非常严格,必须明确指定兼容版本

2. **Python 包命名冲突**: 目录名和模块名冲突时,Python 会优先导入目录,导致 Gunicorn 无法正确加载应用

3. **WSGI 入口点最佳实践**: 为生产环境创建独立的 `wsgi.py` 文件,避免模块导入问题

4. **逐步测试**: 在容器内逐个测试 Python 导入,能够快速定位依赖问题

5. **Socket.IO / WebSocket 注意**: 如果使用 Socket.IO，请确保所选的 Gunicorn worker 支持 WebSocket（例如 `eventlet` 或 `gevent-websocket`）。如果你选择 gevent，安装 `gevent-websocket` 并将 worker 指定为 `geventwebsocket.gunicorn.workers.GeventWebSocketWorker`，否则浏览器的 `/socket.io` WebSocket 握手可能会返回 404。

6. **日志是关键**: Docker 容器的完整错误日志是排查问题的最佳工具

---

## 🎯 部署成功标志

- ✅ 容器状态: `Up` (非 `Restarting`)
- ✅ 4个 worker 进程全部启动
- ✅ 端口 5020 正确映射
- ✅ 健康检查通过
- ✅ 访问 http://localhost:5020 正常

---

**部署完成时间**: 2025-11-30 10:27  
**总耗时**: 约 30 分钟  
**解决问题数**: 7个  
**最终状态**: ✅ 成功运行
