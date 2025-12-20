@echo off
chcp 65001 >nul
echo ========================================
echo Docker 容器部署脚本
echo ========================================
echo.

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker未运行！
    echo 请先启动Docker Desktop
    pause
    exit /b 1
)

echo [✓] Docker正在运行
echo.

REM 停止旧容器
echo [1/4] 停止旧容器...
docker-compose down 2>nul
echo.

REM 构建镜像
echo [2/4] 构建Docker镜像...
docker-compose build
if errorlevel 1 (
    echo [错误] 镜像构建失败！
    pause
    exit /b 1
)
echo.

REM 启动容器
echo [3/4] 启动容器...
docker-compose up -d
if errorlevel 1 (
    echo [错误] 容器启动失败！
    pause
    exit /b 1
)
echo.

REM 等待服务启动
echo [4/4] 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查容器状态
docker-compose ps
echo.

echo ========================================
echo ✅ 部署完成！
echo ========================================
echo.
echo 服务地址: http://localhost:5020
echo.
echo 管理命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose stop
echo   重启服务: docker-compose restart
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:5020
