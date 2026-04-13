@echo off
cd /d D:\Entwicklung\Python

echo =========================
echo Baue vo_bildtool.exe ...
echo =========================
echo.

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist vo_bildtool.spec del /q vo_bildtool.spec

call .venv\Scripts\activate.bat

python -m PyInstaller --onefile --windowed vo_bildtool.py

echo.
echo Fertig.
pause