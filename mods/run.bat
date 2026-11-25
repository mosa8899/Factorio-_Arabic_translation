@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (
  python apply_ar.py
) else (
  py apply_ar.py
)
echo.
echo Khalas. Aghlaq el fenetre wa a3id chaghghil Factorio.
pause
