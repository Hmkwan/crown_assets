# PostgreSQL 便携版客户端工具安装脚本
# 无需管理员权限，仅安装命令行工具

Write-Host "`n==============================================`n" -ForegroundColor Cyan
Write-Host "  PostgreSQL 便携版客户端工具安装" -ForegroundColor Green
Write-Host "`n==============================================`n" -ForegroundColor Cyan

# 配置
$installDir = "$PSScriptRoot\postgresql-tools"
$version = "16.1"  # PostgreSQL 版本
$downloadUrl = "https://get.enterprisedb.com/postgresql/postgresql-$version-1-windows-x64-binaries.zip"

Write-Host "[1/5] 检查安装目录..." -ForegroundColor Yellow
if (Test-Path $installDir) {
    Write-Host "  ✓ 目录已存在: $installDir" -ForegroundColor Gray
} else {
    Write-Host "  → 创建目录: $installDir" -ForegroundColor Gray
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

Write-Host "`n[2/5] 下载 PostgreSQL 便携版..." -ForegroundColor Yellow
$zipFile = "$installDir\postgresql-binaries.zip"

# 检查是否已下载
if (Test-Path $zipFile) {
    Write-Host "  ✓ 安装包已存在，跳过下载" -ForegroundColor Green
} else {
    Write-Host "  → 下载地址: $downloadUrl" -ForegroundColor Gray
    Write-Host "  → 文件大小: 约 60 MB" -ForegroundColor Gray
    Write-Host "  → 下载中，请稍候..." -ForegroundColor Gray
    
    try {
        # 使用 .NET 下载（支持进度显示）
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($downloadUrl, $zipFile)
        Write-Host "  ✓ 下载完成" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ 下载失败: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "`n  请手动下载并解压：" -ForegroundColor Yellow
        Write-Host "  1. 访问: https://www.enterprisedb.com/download-postgresql-binaries" -ForegroundColor Cyan
        Write-Host "  2. 下载 Windows x86-64 Binaries" -ForegroundColor Cyan
        Write-Host "  3. 解压到: $installDir" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host "`n[3/5] 解压安装包..." -ForegroundColor Yellow
try {
    if (-not (Test-Path "$installDir\pgsql")) {
        Write-Host "  → 解压中..." -ForegroundColor Gray
        Expand-Archive -Path $zipFile -DestinationPath $installDir -Force
        Write-Host "  ✓ 解压完成" -ForegroundColor Green
    } else {
        Write-Host "  ✓ 文件已解压，跳过" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ 解压失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n[4/5] 配置环境变量..." -ForegroundColor Yellow
$binPath = "$installDir\pgsql\bin"

# 检查 bin 目录是否存在
if (-not (Test-Path $binPath)) {
    Write-Host "  ✗ 未找到 bin 目录: $binPath" -ForegroundColor Red
    Write-Host "  请检查下载的文件是否完整" -ForegroundColor Yellow
    exit 1
}

# 添加到当前会话的 PATH
if ($env:Path -notlike "*$binPath*") {
    $env:Path = "$binPath;$env:Path"
    Write-Host "  ✓ 已添加到当前会话 PATH" -ForegroundColor Green
} else {
    Write-Host "  ✓ 已在 PATH 中" -ForegroundColor Green
}

Write-Host "`n[5/5] 验证安装..." -ForegroundColor Yellow
try {
    $pgDumpVersion = & "$binPath\pg_dump.exe" --version 2>&1
    $pgRestoreVersion = & "$binPath\pg_restore.exe" --version 2>&1
    $psqlVersion = & "$binPath\psql.exe" --version 2>&1
    
    Write-Host "  ✓ pg_dump:    $pgDumpVersion" -ForegroundColor Green
    Write-Host "  ✓ pg_restore: $pgRestoreVersion" -ForegroundColor Green
    Write-Host "  ✓ psql:       $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 验证失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n==============================================`n" -ForegroundColor Cyan
Write-Host "  ✓ 安装成功！" -ForegroundColor Green
Write-Host "`n==============================================`n" -ForegroundColor Cyan

Write-Host "安装目录: $installDir" -ForegroundColor Cyan
Write-Host "可执行文件: $binPath" -ForegroundColor Cyan

Write-Host "`n【重要提示】" -ForegroundColor Yellow
Write-Host "1. 当前会话已可以使用 pg_dump 等命令" -ForegroundColor Gray
Write-Host "2. 新打开的终端需要重新配置 PATH" -ForegroundColor Gray
Write-Host "`n【永久添加到 PATH（可选）】" -ForegroundColor Yellow
Write-Host "运行以下命令（需要管理员权限）：" -ForegroundColor Gray
Write-Host @"
`$env:Path = "$binPath;`$env:Path"
[Environment]::SetEnvironmentVariable("Path", `$env:Path, "User")
"@ -ForegroundColor Cyan

Write-Host "`n【快速测试】" -ForegroundColor Yellow
Write-Host "运行: python test_postgresql_backup.py" -ForegroundColor Green
Write-Host ""
