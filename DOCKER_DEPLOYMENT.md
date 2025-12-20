# Docker部署指南

## 📋 前提条件

- Docker Desktop已安装并运行（您的截图显示Docker Desktop正在运行）
- 确保端口5020未被占用

## 🚀 快速部署步骤

### 方法一：使用 Docker Compose（推荐）

#### 1. 构建并启动容器

```powershell
# 在项目根目录执行
docker-compose up -d --build
```

这将：
- 自动构建Docker镜像
- 创建并启动容器
- 在后台运行（-d参数）
- 映射端口5020到主机

#### 2. 查看运行状态

```powershell
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看实时日志（按Ctrl+C退出）
docker-compose logs -f web
```

#### 3. 访问系统

打开浏览器访问：
- http://localhost:5020

#### 4. 停止服务

```powershell
# 停止容器
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器及数据卷（谨慎！）
docker-compose down -v
```

---

### 方法二：使用 Docker 命令

#### 1. 构建镜像

```powershell
docker build -t equipment-management-system:latest .
```

#### 2. 运行容器

```powershell
docker run -d `
  --name equipment-management `
  -p 5020:5020 `
  -v ${PWD}/app.db:/app/app.db `
  -v ${PWD}/app/static:/app/app/static `
  -e FLASK_DEBUG=False `
  --restart unless-stopped `
  equipment-management-system:latest
```

#### 3. 查看容器

```powershell
# 查看运行中的容器
docker ps

# 查看日志
docker logs -f equipment-management

# 进入容器shell
docker exec -it equipment-management /bin/bash
```

#### 4. 停止和删除

```powershell
# 停止容器
docker stop equipment-management

# 删除容器
docker rm equipment-management

# 删除镜像
docker rmi equipment-management-system:latest
```

---

## 🔧 配置说明

### 环境变量

在 `docker-compose.yml` 或运行命令中可以设置：

```yaml
environment:
  - FLASK_DEBUG=False          # 禁用调试模式
  - SECRET_KEY=your-secret-key # 设置密钥
  - TZ=Asia/Shanghai           # 时区设置
```

### 端口映射

默认映射：`5020:5020`（主机端口:容器端口）

如需更改主机端口：
```yaml
ports:
  - "8080:5020"  # 使用主机8080端口
```

### 数据持久化

重要的数据卷挂载：

```yaml
volumes:
  - ./app.db:/app/app.db                # 数据库文件
  - ./app/static:/app/app/static        # 静态文件
```

**注意**：删除容器不会删除挂载的数据文件

---

## 📊 在Docker Desktop中管理

您的Docker Desktop界面可以：

1. **查看容器**：在Containers标签页查看运行状态
2. **查看日志**：点击容器查看实时日志
3. **进入终端**：点击容器的CLI图标进入容器shell
4. **停止/启动**：使用界面按钮控制容器
5. **查看资源**：监控CPU和内存使用情况

---

## 🔍 故障排查

### 问题1：容器无法启动

**检查日志**：
```powershell
docker-compose logs web
```

**常见原因**：
- 端口被占用：更改端口映射
- 数据库文件损坏：删除app.db重新初始化
- 依赖安装失败：检查requirements.txt

### 问题2：无法访问服务

**检查容器状态**：
```powershell
docker-compose ps
```

**检查端口**：
```powershell
netstat -ano | findstr :5020
```

**检查防火墙**：确保5020端口未被防火墙阻止

### 问题3：数据库未持久化

**确认挂载**：
```powershell
docker inspect equipment-management-system | Select-String -Pattern "Mounts" -Context 10
```

### 问题4：性能问题

**调整Worker数量**：
编辑Dockerfile中的CMD：
```dockerfile
CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:5020", ...]
# 增加worker数量（默认4）
```

---

## 🔐 生产环境建议

### 1. 使用环境变量文件

创建 `.env` 文件：
```env
SECRET_KEY=your-very-secure-secret-key-here
FLASK_DEBUG=False
DATABASE_URL=sqlite:///data/app.db
```

在 `docker-compose.yml` 中引用：
```yaml
env_file:
  - .env
```

### 2. 设置资源限制

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

### 3. 使用外部数据库

如果数据量大，建议使用PostgreSQL或MySQL：

```yaml
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: equipment
    volumes:
      - db-data:/var/lib/postgresql/data
  
  web:
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/equipment

volumes:
  db-data:
```

### 4. 启用HTTPS

使用Nginx反向代理：

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
```

---

## 📦 导出和分享镜像

### 保存镜像到文件

```powershell
# 导出镜像
docker save -o equipment-management-system.tar equipment-management-system:latest

# 压缩镜像
Compress-Archive -Path equipment-management-system.tar -DestinationPath equipment-management-system.tar.gz
```

### 在其他机器加载镜像

```powershell
# 加载镜像
docker load -i equipment-management-system.tar

# 或从压缩文件
Expand-Archive equipment-management-system.tar.gz
docker load -i equipment-management-system.tar
```

---

## 🔄 更新部署

### 更新代码后重新部署

```powershell
# 1. 停止当前容器
docker-compose down

# 2. 重新构建镜像
docker-compose build

# 3. 启动新容器
docker-compose up -d

# 或一条命令完成
docker-compose up -d --build
```

### 零停机更新（生产环境）

```powershell
# 1. 构建新镜像
docker-compose build

# 2. 使用滚动更新
docker-compose up -d --no-deps --build web
```

---

## 📝 完整部署清单

部署前检查：
- [ ] Docker Desktop已安装并运行
- [ ] 项目文件完整
- [ ] app.db数据库文件存在
- [ ] 端口5020未被占用

执行部署：
- [ ] 运行 `docker-compose up -d --build`
- [ ] 检查容器状态 `docker-compose ps`
- [ ] 访问 http://localhost:5020
- [ ] 测试登录功能
- [ ] 检查日志无错误

部署后：
- [ ] 设置开机自启（Docker Desktop设置）
- [ ] 配置自动备份
- [ ] 监控容器状态

---

## 🎯 推荐部署命令（开始使用）

最简单的部署方式：

```powershell
# 在项目根目录（C:\Users\it03.GD\Desktop\TEST）执行
docker-compose up -d --build
```

等待1-2分钟后，访问 http://localhost:5020

就这么简单！🎉
