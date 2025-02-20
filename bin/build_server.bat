@echo off

cd /d %~dp0..
setlocal

python-embed\python.exe -B lib\server_builder.py

endlocal

pause