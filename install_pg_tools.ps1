# PostgreSQL 客户端工具 - 简易安装脚本
# 下载官方便携版工具包（仅命令行工具，约 10 MB）

param(
    [switch]$Auto
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL 客户端工具快速安装" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# 配置
$toolsDir = "$PSScriptRoot\pg_tools"
$downloadUrl = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1258649"  # PostgreSQL 16 命令行工具
$zipFile = "$toolsDir\pg_commandline.zip"

# 创建目录
Write-Host "[1/4] 准备安装目录..." -ForegroundColor Yellow
if (-not (Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    Write-Host "  ✓ 创建目录: $toolsDir" -ForegroundColor Green
} else {
    Write-Host "  ✓ 目录已存在" -ForegroundColor Green
}

# 检查是否已安装
$binPath = "$toolsDir\bin"
if ((Test-Path "$binPath\pg_dump.exe") -and (Test-Path "$binPath\pg_restore.exe")) {
    Write-Host "`n已检测到 PostgreSQL 工具已安装!" -ForegroundColor Green
    Write-Host "位置: $binPath" -ForegroundColor Cyan
    
    # 添加到 PATH
    if ($env:Path -notlike "*$binPath*") {
        $env:Path = "$binPath;$env:Path"
        Write-Host "✓ 已添加到当前会话 PATH" -ForegroundColor Green
    }
    
    # 验证
    $version = & "$binPath\pg_dump.exe" --version
    Write-Host "`n版本: $version" -ForegroundColor Cyan
    Write-Host "`n可以直接使用！运行: python test_postgresql_backup.py" -ForegroundColor Green
    exit 0
}

Write-Host "`n【方案选择】" -ForegroundColor Cyan
Write-Host "1. 手动下载安装（推荐，最稳定）" -ForegroundColor Yellow
Write-Host "2. 使用 Scoop 安装（需要管理员权限）" -ForegroundColor Yellow
Write-Host "3. 继续使用 Python 备份脚本（无需安装）" -ForegroundColor Yellow

if (-not $Auto) {
    Write-Host "`n请选择 [1-3]: " -ForegroundColor Green -NoNewline
    $choice = Read-Host
} else {
    $choice = "1"
}

switch ($choice) {
    "1" {
        Write-Host "`n【手动下载安装步骤】" -ForegroundColor Cyan
        Write-Host "================================" -ForegroundColor Gray
        Write-Host "1. 访问以下链接下载 PostgreSQL:" -ForegroundColor Yellow
        Write-Host "   https://www.enterprisedb.com/downloads/postgres-postgresql-downloads`n" -ForegroundColor Green
        
        Write-Host "2. 选择版本:" -ForegroundColor Yellow
        Write-Host "   - PostgreSQL 16.x" -ForegroundColor Gray
        Write-Host "   - Windows x86-64`n" -ForegroundColor Gray
        
        Write-Host "3. 安装时勾选:" -ForegroundColor Yellow
        Write-Host "   - Command Line Tools (必须)`n" -ForegroundColor Gray
        
        Write-Host "4. 安装后配置 PATH:" -ForegroundColor Yellow
        Write-Host '   $env:Path = "C:\Program Files\PostgreSQL\16\bin;$env:Path"' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "5. 验证安装:" -ForegroundColor Yellow
        Write-Host "   pg_dump --version" -ForegroundColor Cyan
        Write-Host ""
        
        # 打开下载页面
        Start-Process "https://www.enterprisedb.com/downloads/postgres-postgresql-downloads"
    }
    
    "2" {
        Write-Host "`n尝试使用 Scoop 安装..." -ForegroundColor Yellow
        
        # 检查 Scoop
        $scoopInstalled = Get-Command scoop -ErrorAction SilentlyContinue
        if (-not $scoopInstalled) {
            Write-Host "  → Scoop 未安装，正在安装..." -ForegroundColor Gray
            try {
                Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                irm get.scoop.sh | iex
            } catch {
                Write-Host "  ✗ Scoop 安装失败" -ForegroundColor Red
                Write-Host "  请选择方案 1 手动安装" -ForegroundColor Yellow
                exit 1
            }
        }
        
        Write-Host "  → 安装 PostgreSQL..." -ForegroundColor Gray
        scoop install postgresql
        
        Write-Host "`n  ✓ 安装完成!" -ForegroundColor Green
        Write-Host "  验证: pg_dump --version" -ForegroundColor Cyan
    }
    
    "3" {
        Write-Host "`n使用 Python 备份脚本（无需安装）" -ForegroundColor Green
        Write-Host "================================" -ForegroundColor Gray
        Write-Host "运行命令:" -ForegroundColor Yellow
        Write-Host "  python python_postgresql_backup.py`n" -ForegroundColor Cyan
        
        Write-Host "优点:" -ForegroundColor Yellow
        Write-Host "  ✓ 无需安装额外软件" -ForegroundColor Gray
        Write-Host "  ✓ 立即可用`n" -ForegroundColor Gray
        
        Write-Host "限制:" -ForegroundColor Yellow
        Write-Host "  - 不包含索引和约束" -ForegroundColor Gray
        Write-Host "  - 需要手动重建数据库结构`n" -ForegroundColor Gray
    }
    
    default {
        Write-Host "`n无效选择，请重新运行脚本" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  安装指南已显示" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
