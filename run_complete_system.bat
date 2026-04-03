@echo off
echo ========================================
echo   Diet Recommendation System
echo   Database-Enabled Version
echo ========================================
echo.
echo Checking system status...
echo.

echo 1. Backend Status:
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% == 0 (
    echo    [RUNNING] Database Backend on http://localhost:5000
    echo    [DATABASE] SQLite (Persistent Storage)
    echo    [FEATURES] All data persists between restarts
) else (
    echo    [STOPPED] Backend not running
    echo    Starting database backend...
    cd /d "c:\project4\Diet Recommendation System\backend"
    start /B python app_db.py
    timeout /t 3 >nul
    echo    Database backend started!
)

echo.
echo 2. Starting Frontend...
cd /d "c:\project4\Diet Recommendation System"
echo    Starting React development server...
echo    Frontend will be available at: http://localhost:3000
echo.
echo    Press Ctrl+C to stop the frontend
echo.

npm start

pause
