# 使用Python 3.11官方镜像作为基础镜像 (支持 scrypt 密码哈希)
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_DEBUG=False \
    TZ=Asia/Shanghai

# 安装系统依赖、中文字体和 PostgreSQL 客户端工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn \
    && pip install --no-cache-dir gevent --force-reinstall \
    && pip install --no-cache-dir gevent-websocket

# 复制应用代码
COPY . .

# 创建数据目录（用于挂载数据库）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 5020

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5020/auth/login')" || exit 1

# 启动命令 - 使用 gevent worker 提供异步支持（在当前镜像中 eventlet 行为异常）
CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "-b", "0.0.0.0:5020", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
