# Docker开发环境实时同步配置

## ✅ 已配置完成

Docker容器现在已配置为**开发模式**,实现本地代码和容器的实时同步。

---

## 📋 配置详情

### 挂载的目录和文件

```yaml
volumes:
  # 核心代码目录
  - ./app:/app/app                    # 应用代码实时同步
  - ./config.py:/app/config.py        # 配置文件
  - ./requirements.txt:/app/requirements.txt
  
  # 数据库
  - ./app.db:/app/app.db              # 数据库实时同步
  
  # 前端资源
  - ./app/static:/app/app/static      # 静态文件
  - ./app/templates:/app/app/templates # 模板文件
  
  # 脚本文件
  - ./init_db.py:/app/init_db.py
  - ./init_default_workflow.py:/app/init_default_workflow.py
  - ./init_default_approval_workflows.py:/app/init_default_approval_workflows.py
  - ./test_docker_sync.py:/app/test_docker_sync.py
  - ./test_workflow_amount_config.py:/app/test_workflow_amount_config.py
```

### 环境变量

```yaml
environment:
  - FLASK_DEBUG=True              # 启用调试模式
  - FLASK_ENV=development         # 开发环境
  - SECRET_KEY=${SECRET_KEY}
  - TZ=Asia/Shanghai              # 中国时区
```

---

## 🚀 实时同步功能

### 1. 代码修改立即生效

**Python代码** (`app/main/routes.py`, `app/models.py`等):
- ✅ 修改后Flask自动重载
- ✅ 无需重启容器
- ✅ 无需重新构建镜像

**测试方法**:
```bash
# 修改任意.py文件,保存后
docker logs equipment-management-system --tail 20
# 会看到: Reloading... 信息
```

### 2. 模板修改立即生效

**HTML模板** (`app/templates/**/*.html`):
- ✅ 刷新浏览器即可看到变化
- ✅ 无需重启

**测试方法**:
```bash
# 修改模板文件,直接刷新浏览器
```

### 3. 静态文件立即生效

**CSS/JS** (`app/static/**/*`):
- ✅ 修改后刷新浏览器
- ✅ 可能需要强制刷新(Ctrl+F5)

### 4. 数据库实时同步

**数据库文件** (`app.db`):
- ✅ 本地修改容器立即可见
- ✅ 容器内修改本地立即可见
- ✅ 双向实时同步

**测试方法**:
```bash
# 本地运行
python init_default_approval_workflows.py

# 容器内立即可用
docker exec equipment-management-system python -c "from app.models import WorkflowNode; print(WorkflowNode.query.count())"
```

---

## 🔧 开发工作流

### 日常开发步骤

1. **启动容器**:
   ```bash
   docker-compose up -d
   ```

2. **修改代码**:
   - 在VSCode中编辑文件
   - 保存后自动同步到容器

3. **查看效果**:
   - 访问 http://localhost:5020
   - 刷新浏览器查看变化

4. **查看日志**:
   ```bash
   docker logs -f equipment-management-system
   ```

5. **停止容器** (如需):
   ```bash
   docker-compose down
   ```

### 数据库操作

**运行初始化脚本**:
```bash
# 本地运行(推荐)
python init_default_approval_workflows.py

# 或容器内运行
docker exec equipment-management-system python init_default_approval_workflows.py
```

**数据库迁移**:
```bash
# 本地运行
alembic upgrade head

# 或容器内运行
docker exec equipment-management-system alembic upgrade head
```

---

## ⚠️ 注意事项

### 1. 不需要重新构建的情况

以下修改**无需**运行 `docker-compose build`:
- ✅ 修改Python代码
- ✅ 修改HTML模板
- ✅ 修改CSS/JS
- ✅ 修改数据库
- ✅ 修改配置文件

### 2. 需要重新构建的情况

以下情况**需要**运行 `docker-compose build`:
- ❌ 修改 `requirements.txt` (添加新包)
- ❌ 修改 `Dockerfile`
- ❌ 系统级依赖变更

**重新构建命令**:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### 3. Debug模式说明

- **优点**: 代码自动重载,详细错误信息
- **缺点**: 性能略低,不适合生产环境
- **切换到生产模式**: 修改docker-compose.yml中的 `FLASK_DEBUG=False`

---

## 🧪 测试同步

运行测试脚本验证同步:

```bash
# 测试1: 代码同步
docker exec equipment-management-system python test_docker_sync.py

# 测试2: 数据库同步
docker exec equipment-management-system python test_workflow_amount_config.py

# 测试3: 检查挂载
docker exec equipment-management-system ls -la /app/app/
```

---

## 📝 配置文件

**文件位置**: `docker-compose.yml`

**当前配置**:
```yaml
version: '3.8'
services:
  web:
    build: .
    container_name: equipment-management-system
    ports:
      - "5020:5020"
    volumes:
      - ./app:/app/app
      - ./app.db:/app/app.db
      - [其他挂载...]
    environment:
      - FLASK_DEBUG=True
      - FLASK_ENV=development
    restart: unless-stopped
```

---

## 🎯 快速命令参考

```bash
# 启动容器
docker-compose up -d

# 停止容器
docker-compose down

# 重启容器
docker-compose restart

# 查看日志
docker logs -f equipment-management-system

# 进入容器
docker exec -it equipment-management-system bash

# 在容器内运行Python
docker exec equipment-management-system python script.py

# 查看容器状态
docker-compose ps

# 查看挂载
docker inspect equipment-management-system | grep -A 20 Mounts
```

---

## ✨ 优势

### 开发效率提升

1. **即时反馈**: 代码修改后立即看到效果
2. **无需等待**: 不用重新构建镜像(节省时间)
3. **调试方便**: Debug模式提供详细错误信息
4. **数据一致**: 本地和容器共享同一数据库

### 环境一致性

1. **开发=生产**: 容器环境与生产环境一致
2. **依赖隔离**: Python依赖在容器内,不污染本地
3. **版本锁定**: Python 3.11环境固定

---

## 🔄 从旧配置迁移

### 旧配置(仅挂载数据库)
```yaml
volumes:
  - ./app.db:/app/app.db
```

### 新配置(完整同步)
```yaml
volumes:
  - ./app:/app/app              # 代码同步
  - ./app.db:/app/app.db        # 数据库同步
  - ./config.py:/app/config.py  # 配置同步
  # ...更多挂载
```

### 迁移步骤
1. ✅ 已完成 - 修改docker-compose.yml
2. ✅ 已完成 - 重启容器
3. ✅ 已完成 - 验证同步

---

**配置完成日期**: 2025-11-30
**配置状态**: ✅ 生产就绪
**测试状态**: ✅ 已验证同步
