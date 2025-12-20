# 🐳 Docker快速部署参考卡

## ⚡ 一键部署（最简单）

```powershell
# 方式1: 使用PowerShell脚本（推荐）
.\deploy_docker.ps1

# 方式2: 使用批处理脚本
.\deploy_docker.bat

# 方式3: 手动命令
docker-compose up -d --build
```

执行后，访问：http://localhost:5020

---

## 📋 常用命令速查

### 启动和停止

```powershell
# 启动容器
docker-compose up -d

# 停止容器
docker-compose stop

# 重启容器
docker-compose restart

# 停止并删除容器
docker-compose down
```

### 查看状态

```powershell
# 查看运行状态
docker-compose ps

# 查看日志（实时）
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100

# 查看特定服务日志
docker-compose logs -f web
```

### 进入容器

```powershell
# 进入容器Shell
docker-compose exec web /bin/bash

# 或使用Docker命令
docker exec -it equipment-management-system /bin/bash

# 在容器中执行Python命令
docker-compose exec web python -c "print('Hello from container')"
```

### 更新部署

```powershell
# 完整更新流程
docker-compose down
docker-compose build
docker-compose up -d

# 或一条命令
docker-compose up -d --build
```

---

## 🔧 Docker Desktop界面操作

在您的Docker Desktop中：

1. **Containers标签**：
   - 查看容器 `equipment-management-system`
   - 点击容器名查看详情
   - 使用▶️停止按钮控制容器

2. **查看日志**：
   - 点击容器
   - 点击"Logs"标签
   - 实时查看应用日志

3. **进入终端**：
   - 点击容器
   - 点击"Terminal"或"CLI"图标
   - 直接在容器内执行命令

4. **查看资源**：
   - "Stats"标签查看CPU/内存使用
   - 监控容器性能

---

## 🔍 故障排查速查

### 容器无法启动

```powershell
# 查看详细错误信息
docker-compose logs

# 查看容器详细信息
docker inspect equipment-management-system

# 查看构建过程
docker-compose build --no-cache
```

### 端口冲突

```powershell
# 检查端口占用
netstat -ano | findstr :5020

# 修改端口（编辑docker-compose.yml）
ports:
  - "8080:5020"  # 改用8080端口
```

### 数据库问题

```powershell
# 进入容器检查数据库
docker-compose exec web ls -lh /app/app.db

# 重新初始化数据库
docker-compose exec web python init_db.py
```

### 性能问题

```powershell
# 查看资源使用
docker stats equipment-management-system

# 增加worker数量（编辑Dockerfile）
CMD ["gunicorn", "-w", "8", ...]  # 默认是4
```

---

## 📦 数据备份（Docker环境）

### 备份数据库

```powershell
# 复制数据库文件到主机
docker cp equipment-management-system:/app/app.db ./app.db.backup

# 或使用挂载的文件直接备份
Copy-Item app.db app.db.backup
```

### 导出容器

```powershell
# 导出整个容器
docker export equipment-management-system > container-backup.tar

# 保存镜像
docker save equipment-management-system:latest > image-backup.tar
```

---

## 🚀 生产环境优化

### 启用自动重启

已在 `docker-compose.yml` 中配置：
```yaml
restart: unless-stopped
```

### 资源限制

编辑 `docker-compose.yml` 添加：
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### 健康检查

已配置自动健康检查，不健康时自动重启

---

## 💡 提示

- ✅ Docker容器会自动在开机时启动（如果Docker Desktop设置为开机启动）
- ✅ 数据库文件通过挂载保存在主机，删除容器不会丢失数据
- ✅ 使用Gunicorn生产服务器，性能优于开发服务器
- ✅ 已配置健康检查，服务异常时自动重启
- ⚠️ 首次构建需要1-3分钟下载依赖
- ⚠️ 确保app.db文件存在，否则需要初始化数据库

---

## 🎯 现在就开始

在 `C:\Users\it03.GD\Desktop\TEST` 目录执行：

```powershell
# 运行一键部署脚本
.\deploy_docker.ps1
```

或在Docker Desktop界面：
1. 点击"Images"标签
2. 点击"Build"按钮
3. 选择项目目录中的Dockerfile
4. 构建完成后点击"Run"

就这么简单！🎉
