@echo off
REM AIDM 后端一键启动（Windows）
REM 用法：deploy\start.bat
setlocal

cd /d "%~dp0\.."

set PYTHONPATH=src
if "%PY%"=="" set PY=python

echo 启动 AIDM 后端 http://0.0.0.0:8080 (reload 模式)...
%PY% -m uvicorn aidm.api.main:combined_app --host 0.0.0.0 --port 8080 --reload

endlocal
