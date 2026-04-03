@echo off
echo ========================================
echo   Diet Recommendation System Startup
echo ========================================
echo.
echo Checking system status...
echo.

echo 1. Backend Status:
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% == 0 (
    echo    [RUNNING] Backend on http://localhost:5000
) else (
    echo    [STOPPED] Backend not running
    echo    Please start backend first:
    echo    cd "c:\project4\Diet Recommendation System\backend"
    echo    python app.py
    pause
    exit /b
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
