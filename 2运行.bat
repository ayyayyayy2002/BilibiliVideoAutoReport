@echo off
chcp 65001
setlocal
.venv\Scripts\python.exe main.py
popd
pause
endlocal