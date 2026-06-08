@echo off
cd /d "D:\Postgeschichte_PC\IT-Entwicklung\Historische_Suite_Projektordner\Pagina\app\Python"

echo =========================
echo Baue Pagina.exe ...
echo =========================
echo.

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

call .venv\Scripts\activate.bat

python -m PyInstaller Pagina.spec

echo.
echo Fertig.
pause