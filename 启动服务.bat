@echo off
chcp 65001 >nul
cd /d "D:\APP"
title Flask应用 - 运行中

echo ====================================
echo   启动Flask应用
echo   皇冠新材-IT资产管理系统
echo   时间: %date% %time%
echo   开发部门：信息部（广东皇冠新材料科技有限公司）
echo ====================================

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保Python已正确安装
    pause
    exit /b 1
)

:: 检查app.py是否存在
if not exist "C:\Users\it03.GD\Desktop\TEST\app.py" (
    echo [错误] 在 E:\TEST 目录下未找到app.py文件
    pause
    exit /b 1
)

:: 检查Flask是否安装
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [错误] Flask模块未安装
    echo 正在尝试自动安装Flask...
    pip install flask
    if errorlevel 1 (
        echo [错误] Flask安装失败，请手动安装
        echo 运行: pip install flask
        pause
        exit /b 1
    )
    echo [成功] Flask安装完成
)

echo.
echo [信息] 正在启动Flask应用...
echo [信息] 按 Ctrl+C 停止服务
echo ====================================

:: 启动应用，使用绝对路径
python "C:\Users\it03.GD\Desktop\TEST\app.py"

echo.
echo ====================================
echo   应用已停止
echo   停止时间: %date% %time%
echo ====================================
pause