# 重启 Flask 应用（使用新的 PostgreSQL PATH）

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  重启 Flask 应用" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. 配置 PATH
Write-Host "[1/4] 配置 PostgreSQL PATH..." -ForegroundColor Yellow
$pgPath = "C:\Program Files\PostgreSQL\18\bin"
$env:Path = "$pgPath;$env:Path"
Write-Host "  ✓ 已添加: $pgPath" -ForegroundColor Green

# 2. 验证 pg_dump
Write-Host "`n[2/4] 验证 pg_dump..." -ForegroundColor Yellow
try {
    $version = & pg_dump --version
    Write-Host "  ✓ $version" -ForegroundColor Green
} catch {
    Write-Host "  ✗ pg_dump 不可用" -ForegroundColor Red
    Write-Host "  请运行: .\configure_pg_after_install.ps1" -ForegroundColor Yellow
    exit 1
}

# 3. 停止旧进程
Write-Host "`n[3/4] 停止旧的 Flask 进程..." -ForegroundColor Yellow
$stopped = 0
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.CommandLine -like "*app.py*" -or 
    $_.CommandLine -like "*flask*" -or
    $_.CommandLine -like "*TEST*"
} | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    $stopped++
}

if ($stopped -gt 0) {
    Write-Host "  ✓ 已停止 $stopped 个进程" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  → 未发现运行中的进程" -ForegroundColor Gray
}

# 4. 启动 Flask
Write-Host "`n[4/4] 启动 Flask 应用..." -ForegroundColor Yellow
Write-Host "  → 使用 boot.bat 启动..." -ForegroundColor Gray

# 在新窗口启动
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; & '.\boot.bat'"

Write-Host "  ✓ 已在新窗口启动 Flask" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✓ 重启完成！" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "【验证】" -ForegroundColor Yellow
Write-Host "1. 等待 Flask 启动（约 5-10 秒）" -ForegroundColor Gray
Write-Host "2. 访问: http://localhost:5020/admin/database" -ForegroundColor Cyan
Write-Host "3. 点击'立即备份'测试功能" -ForegroundColor Gray
Write-Host ""
