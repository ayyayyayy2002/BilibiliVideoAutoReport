@echo off
chcp 65001
setlocal

echo ===== 第一步：检查虚拟环境 =====
if exist .venv (
    echo 虚拟环境已存在，跳过创建步骤
) else (
    echo 未检测到虚拟环境，正在创建...
    python -m venv .venv
    if not exist .venv (
        echo 虚拟环境创建失败
        pause
        exit /b
    )
    echo 虚拟环境创建完成
)

echo.
echo ===== 第二步：升级 pip =====
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo pip 升级失败，可重新运行此脚本继续
    pause
    exit /b
)

echo.
echo ===== 第三步：安装依赖 =====
if exist requirements.txt (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖安装失败，可重新运行此脚本继续
        pause
        exit /b
    )
    echo 依赖安装完成
) else (
    echo 未找到 requirements.txt，跳过依赖安装
)

echo.
echo ===== 所有步骤执行完成 =====
pause
endlocal
