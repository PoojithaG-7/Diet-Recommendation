@echo off
echo ========================================
echo   Simplified Diet System
echo   Users + Meals Only
echo ========================================
echo.
echo Checking system status...
echo.

echo 1. Backend Status:
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% == 0 (
    echo    [RUNNING] Simplified Backend on http://localhost:5000
    echo    [DATABASE] SQLite (Users + Meals only)
    echo    [FEATURES] User authentication, Meal logging
) else (
    echo    [STOPPED] Backend not running
    echo    Starting simplified backend...
    cd /d "c:\project4\Diet Recommendation System\backend"
    start /B python simplified_app.py
    timeout /t 3 >nul
    echo    Simplified backend started!
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
