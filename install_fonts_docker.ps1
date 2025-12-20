# Docker容器中文字体安装脚本 (PowerShell版本)
# 使用方法: .\install_fonts_docker.ps1 <容器名称或ID>

param(
    [Parameter(Mandatory=$false)]
    [string]$ContainerName
)

# 如果没有提供容器名,尝试自动查找
if (-not $ContainerName) {
    Write-Host "正在查找运行中的容器..." -ForegroundColor Yellow
    $containers = docker ps --format "{{.Names}}"
    if ($containers) {
        Write-Host "找到以下容器:" -ForegroundColor Green
        $containers | ForEach-Object { Write-Host "  - $_" }
        $ContainerName = Read-Host "请输入容器名称"
    } else {
        Write-Host "错误: 没有找到运行中的容器" -ForegroundColor Red
        exit 1
    }
}

Write-Host "目标容器: $ContainerName" -ForegroundColor Cyan
Write-Host ""

# 检测容器的操作系统类型
Write-Host "检测容器操作系统..." -ForegroundColor Yellow
$osType = docker exec $ContainerName cat /etc/os-release 2>$null

if ($osType -match "debian|ubuntu") {
    Write-Host "检测到 Debian/Ubuntu 系统" -ForegroundColor Green
    
    # 更新包列表
    Write-Host "更新包列表..." -ForegroundColor Yellow
    docker exec $ContainerName apt-get update
    
    # 安装中文字体
    Write-Host "安装中文字体..." -ForegroundColor Yellow
    docker exec $ContainerName apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei fonts-dejavu fonts-liberation
    
} elseif ($osType -match "alpine") {
    Write-Host "检测到 Alpine 系统" -ForegroundColor Green
    
    # 安装基础字体
    Write-Host "安装字体包..." -ForegroundColor Yellow
    docker exec $ContainerName apk add --no-cache ttf-dejavu fontconfig wget
    
    # 创建字体目录
    docker exec $ContainerName mkdir -p /usr/share/fonts/truetype/wqy
    
    # 下载文泉驿字体
    Write-Host "下载中文字体..." -ForegroundColor Yellow
    docker exec $ContainerName wget -q https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc -O /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
    
    # 刷新字体缓存
    Write-Host "刷新字体缓存..." -ForegroundColor Yellow
    docker exec $ContainerName fc-cache -f -v
    
} elseif ($osType -match "centos|rhel|fedora") {
    Write-Host "检测到 RedHat/CentOS 系统" -ForegroundColor Green
    
    # 安装中文字体
    Write-Host "安装中文字体..." -ForegroundColor Yellow
    docker exec $ContainerName yum install -y wqy-microhei-fonts wqy-zenhei-fonts dejavu-sans-fonts liberation-sans-fonts
    
} else {
    Write-Host "警告: 无法识别操作系统类型" -ForegroundColor Red
    Write-Host "请手动在容器中执行字体安装命令" -ForegroundColor Yellow
    exit 1
}

# 验证字体安装
Write-Host ""
Write-Host "验证已安装的字体:" -ForegroundColor Cyan
docker exec $ContainerName fc-list 2>$null | Select-String -Pattern "wqy|dejavu|liberation" | Select-Object -First 10

Write-Host ""
Write-Host "字体安装完成!" -ForegroundColor Green
Write-Host "请重启容器中的Flask应用以使更改生效" -ForegroundColor Yellow
Write-Host ""
Write-Host "重启方法:" -ForegroundColor Cyan
Write-Host "  docker restart $ContainerName" -ForegroundColor White
