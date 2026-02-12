@echo off
chcp 65001
setlocal

echo 正在创建虚拟环境...
python -m venv .venv

if not exist .venv (
    echo 虚拟环境创建失败
    pause
    exit /b
)

echo 正在升级 pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

if exist requirements.txt (
    echo 正在安装依赖...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo 虚拟环境创建完成
pause
endlocal
