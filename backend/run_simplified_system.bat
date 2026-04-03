@echo off
echo ========================================
echo   Simplified Diet System
echo   Users + Meals Only
echo ========================================
echo.
echo Features:
echo - User authentication and profiles
echo - Meal logging with nutrition tracking
echo - Food database with auto-calculation
echo - Search and delete meal functionality
echo - Admin dashboard
echo.
echo Database: SQLite (Simplified)
echo Tables: users, user_profiles, diet_logs
echo.
echo Starting simplified backend...
echo Backend will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python simplified_app.py

pause
