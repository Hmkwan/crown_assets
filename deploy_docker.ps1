#!/usr/bin/env pwsh
# Docker部署脚本 - PowerShell版本

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Docker 容器部署脚本" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 检查Docker是否运行
Write-Host "[检查] Docker运行状态..." -ForegroundColor Yellow
try {
    docker info 2>$null | Out-Null
    Write-Host "[✓] Docker正在运行`n" -ForegroundColor Green
} catch {
    Write-Host "[✗] Docker未运行！" -ForegroundColor Red
    Write-Host "请先启动Docker Desktop" -ForegroundColor Yellow
    Read-Host "按Enter退出"
    exit 1
}

# 停止旧容器
Write-Host "[1/4] 停止旧容器..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host ""

# 构建镜像
Write-Host "[2/4] 构建Docker镜像..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] 镜像构建失败！" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}
Write-Host ""

# 启动容器
Write-Host "[3/4] 启动容器..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] 容器启动失败！" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}
Write-Host ""

# 等待服务启动
Write-Host "[4/4] 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 检查容器状态
Write-Host "`n容器状态:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "服务地址: " -NoNewline
Write-Host "http://localhost:5020" -ForegroundColor Cyan

Write-Host "`n管理命令:" -ForegroundColor Yellow
Write-Host "  查看日志: " -NoNewline -ForegroundColor White
Write-Host "docker-compose logs -f" -ForegroundColor Cyan
Write-Host "  停止服务: " -NoNewline -ForegroundColor White
Write-Host "docker-compose stop" -ForegroundColor Cyan
Write-Host "  重启服务: " -NoNewline -ForegroundColor White
Write-Host "docker-compose restart" -ForegroundColor Cyan

Write-Host "`n按Enter打开浏览器..." -ForegroundColor Gray
Read-Host
Start-Process "http://localhost:5020"
