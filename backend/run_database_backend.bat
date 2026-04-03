@echo off
echo ========================================
echo   Database-Enabled Diet System
echo ========================================
echo.
echo Starting Diet Recommendation System with SQLite Database...
echo.
echo Features:
echo - Persistent data storage
echo - User authentication
echo - Diet logging and tracking
echo - Exercise monitoring
echo - Water intake tracking
echo - Admin dashboard
echo.
echo Backend will be available at: http://localhost:5000
echo Database: SQLite (diet_system.db)
echo.
echo Press Ctrl+C to stop the server
echo.

python app_db.py

pause
