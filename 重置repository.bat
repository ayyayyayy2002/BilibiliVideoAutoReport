@echo off
REM --- 删除旧仓库 ---
rmdir /s /q .git

REM --- 初始化 Git 仓库 ---
git init

REM --- 配置代理 ---
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

REM --- 配置 Git 用户信息 ---
git config --global user.name "ayyayyayy2002"
git config --global user.email "199196441+ayyayyayy2002@users.noreply.github.com"

REM --- 删除 GitHub 凭据（重新登录用） ---
cmdkey /delete:git:https://github.com

REM --- 创建 main 分支 ---
git branch -M main

REM --- 添加文件并提交 ---
git add .
git commit -m "Initial commit"

REM --- 添加远程仓库 ---
git remote add origin https://github.com/ayyayyayy2002/BilibiliVideoAutoReport.git

REM --- 强制推送到远程 main 分支 ---
git push -f origin main

pause