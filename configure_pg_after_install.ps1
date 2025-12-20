# PostgreSQL 安装后配置脚本
# 用于安装完成后配置环境变量和验证

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL 安装后配置" -ForegroundColor Green
Write-Host "=======================================`n" -ForegroundColor Cyan

# 常见安装路径
$possiblePaths = @(
    "C:\Program Files\PostgreSQL\16\bin",
    "C:\Program Files\PostgreSQL\15\bin",
    "C:\Program Files\PostgreSQL\14\bin",
    "C:\Program Files (x86)\PostgreSQL\16\bin",
    "C:\Program Files (x86)\PostgreSQL\15\bin",
    "$env:LOCALAPPDATA\scoop\apps\postgresql\current\bin",
    "$env:USERPROFILE\scoop\apps\postgresql\current\bin"
)

Write-Host "[1/3] 搜索 PostgreSQL 安装位置..." -ForegroundColor Yellow

$foundPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\pg_dump.exe") {
        $foundPath = $path
        Write-Host "  ✓ 找到: $path" -ForegroundColor Green
        break
    }
}

if (-not $foundPath) {
    Write-Host "  ✗ 未找到 PostgreSQL 安装" -ForegroundColor Red
    Write-Host "`n请确认：" -ForegroundColor Yellow
    Write-Host "1. PostgreSQL 是否已安装完成？" -ForegroundColor Gray
    Write-Host "2. 安装时是否勾选了 'Command Line Tools'？" -ForegroundColor Gray
    Write-Host "`n如果已安装，请手动输入 bin 目录路径：" -ForegroundColor Yellow
    Write-Host "示例: C:\Program Files\PostgreSQL\16\bin" -ForegroundColor Gray
    Write-Host "`n路径: " -ForegroundColor Green -NoNewline
    $customPath = Read-Host
    
    if ($customPath -and (Test-Path "$customPath\pg_dump.exe")) {
        $foundPath = $customPath
        Write-Host "  ✓ 路径有效" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 路径无效或未找到 pg_dump.exe" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n[2/3] 配置环境变量..." -ForegroundColor Yellow

# 检查是否已在 PATH 中
if ($env:Path -like "*$foundPath*") {
    Write-Host "  ✓ 已在当前 PATH 中" -ForegroundColor Green
} else {
    # 添加到当前会话
    $env:Path = "$foundPath;$env:Path"
    Write-Host "  ✓ 已添加到当前会话" -ForegroundColor Green
    
    # 询问是否永久添加
    Write-Host "`n  是否永久添加到用户环境变量？(Y/N): " -ForegroundColor Yellow -NoNewline
    $confirm = Read-Host
    
    if ($confirm -eq 'Y' -or $confirm -eq 'y') {
        try {
            $currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($currentUserPath -notlike "*$foundPath*") {
                [Environment]::SetEnvironmentVariable(
                    "Path",
                    "$foundPath;$currentUserPath",
                    "User"
                )
                Write-Host "  ✓ 已永久添加到用户环境变量" -ForegroundColor Green
                Write-Host "  ⚠ 新终端窗口将自动生效" -ForegroundColor Yellow
            } else {
                Write-Host "  ✓ 已存在于用户环境变量中" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ✗ 添加失败: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  可能需要管理员权限" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  → 跳过永久配置" -ForegroundColor Gray
    }
}

Write-Host "`n[3/3] 验证安装..." -ForegroundColor Yellow

try {
    $pgDump = & pg_dump --version 2>&1
    $pgRestore = & pg_restore --version 2>&1
    $psql = & psql --version 2>&1
    
    Write-Host "  ✓ pg_dump:    $pgDump" -ForegroundColor Green
    Write-Host "  ✓ pg_restore: $pgRestore" -ForegroundColor Green
    Write-Host "  ✓ psql:       $psql" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 验证失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n  请尝试：" -ForegroundColor Yellow
    Write-Host "  1. 关闭此窗口" -ForegroundColor Gray
    Write-Host "  2. 重新打开 PowerShell" -ForegroundColor Gray
    Write-Host "  3. 再次运行此脚本" -ForegroundColor Gray
    exit 1
}

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "  ✓ 配置完成！" -ForegroundColor Green
Write-Host "=======================================`n" -ForegroundColor Cyan

Write-Host "PostgreSQL 客户端工具已就绪！" -ForegroundColor Green
Write-Host "`n【下一步】测试备份功能:" -ForegroundColor Yellow
Write-Host "  python test_postgresql_backup.py`n" -ForegroundColor Cyan

# 询问是否立即测试
Write-Host "是否立即运行测试？(Y/N): " -ForegroundColor Green -NoNewline
$runTest = Read-Host

if ($runTest -eq 'Y' -or $runTest -eq 'y') {
    Write-Host "`n正在运行测试...`n" -ForegroundColor Yellow
    python test_postgresql_backup.py
} else {
    Write-Host "`n稍后可手动运行测试。" -ForegroundColor Gray
}

Write-Host ""
