#!/bin/bash
# Docker容器中安装中文字体
# 使用方法: 
# 1. 复制到容器: docker cp install_fonts_docker.sh <容器名>:/tmp/
# 2. 进入容器执行: docker exec -it <容器名> bash /tmp/install_fonts_docker.sh

echo "开始安装中文字体..."

# 检测系统类型
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu系统
    echo "检测到Debian/Ubuntu系统"
    apt-get update
    apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei fonts-dejavu fonts-liberation
    
elif [ -f /etc/redhat-release ]; then
    # RedHat/CentOS系统
    echo "检测到RedHat/CentOS系统"
    yum install -y wqy-microhei-fonts wqy-zenhei-fonts dejavu-sans-fonts liberation-sans-fonts
    
elif [ -f /etc/alpine-release ]; then
    # Alpine系统
    echo "检测到Alpine系统"
    apk add --no-cache ttf-dejavu fontconfig
    
    # 下载并安装文泉驿字体
    mkdir -p /usr/share/fonts/truetype/wqy
    cd /tmp
    wget -q https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc -O /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
    
    # 刷新字体缓存
    fc-cache -f -v
else
    echo "未知系统类型,请手动安装字体"
    exit 1
fi

echo "字体安装完成!"
echo "已安装字体列表:"
fc-list | grep -i "wqy\|dejavu\|liberation" | head -10

echo ""
echo "请重启Flask应用以使更改生效"
