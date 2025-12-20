# Docker容器中文字体问题解决方案

## 问题描述
在Docker容器中运行Flask应用时,生成的QR码标签图片只显示二维码,不显示中文文字信息。

**根本原因**: 容器镜像中缺少中文字体文件,导致PIL/Pillow无法渲染中文文字。

## 解决方案

### 方法一: 自动安装脚本 (推荐)

使用提供的PowerShell脚本自动安装字体:

```powershell
# 运行安装脚本
.\install_fonts_docker.ps1

# 或指定容器名称
.\install_fonts_docker.ps1 my-flask-container
```

### 方法二: 手动安装

#### 1. 进入容器
```bash
docker exec -it <容器名称> bash
```

#### 2. 根据系统类型安装字体

**Debian/Ubuntu:**
```bash
apt-get update
apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei fonts-dejavu
```

**Alpine Linux:**
```bash
apk add --no-cache ttf-dejavu fontconfig
mkdir -p /usr/share/fonts/truetype/wqy
cd /tmp
wget https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc -O /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
fc-cache -f -v
```

**CentOS/RHEL:**
```bash
yum install -y wqy-microhei-fonts dejavu-sans-fonts
```

#### 3. 验证字体安装
```bash
fc-list | grep -i wqy
```

#### 4. 重启Flask应用
```bash
# 在容器内
pkill -f "python.*app.py"
# 或重启整个容器
docker restart <容器名称>
```

### 方法三: 修改Dockerfile (永久方案)

在Dockerfile中添加字体安装步骤:

**Debian/Ubuntu基础镜像:**
```dockerfile
FROM python:3.11-slim

# 安装中文字体
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fonts-dejavu \
    fontconfig && \
    rm -rf /var/lib/apt/lists/*

# ... 其他配置
```

**Alpine基础镜像:**
```dockerfile
FROM python:3.11-alpine

# 安装字体和依赖
RUN apk add --no-cache \
    ttf-dejavu \
    fontconfig \
    wget && \
    mkdir -p /usr/share/fonts/truetype/wqy && \
    wget -q https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc \
         -O /usr/share/fonts/truetype/wqy/wqy-microhei.ttc && \
    fc-cache -f -v && \
    apk del wget

# ... 其他配置
```

重新构建镜像:
```bash
docker build -t my-flask-app:latest .
docker stop <旧容器>
docker run -d --name my-flask-app my-flask-app:latest
```

## 代码改进

已更新 `app/utils/qrcode_generator.py` 支持以下字体:

### Windows系统
- 微软雅黑 (msyh.ttc)
- 黑体 (simhei.ttf)
- 宋体 (simsun.ttc)

### Linux系统 (容器环境)
- 文泉驿微米黑 (wqy-microhei.ttc)
- 文泉驿正黑 (wqy-zenhei.ttc)
- DejaVu Sans
- Liberation Sans

代码会自动尝试所有字体路径,找到第一个可用字体后使用。

## 测试验证

安装字体后,在资产中心点击"查看标签"按钮:
- ✅ 应该能看到完整的标签,包括:
  - 顶部标题 (设备标签/配件标签)
  - 左侧二维码
  - 右侧信息: 设备名称、编码、部门、采购日期、位置
  - 底部资产类型和ID

## 故障排查

### 1. 检查容器中的字体
```bash
docker exec <容器名> fc-list | grep -i "wqy\|dejavu"
```

### 2. 查看应用日志
```bash
docker logs <容器名> | grep "字体"
```
应该看到类似: `成功加载字体: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc`

### 3. 检查PIL版本
```bash
docker exec <容器名> pip show pillow
```
确保Pillow >= 9.0

## 相关文件

- `install_fonts_docker.ps1` - Windows PowerShell自动安装脚本
- `install_fonts_docker.sh` - Linux Bash自动安装脚本  
- `app/utils/qrcode_generator.py` - 标签生成代码
- `app/main/asset_routes.py` - 标签路由 (已设置DPI=150用于预览)
