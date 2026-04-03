@echo off
echo ========================================
echo   Database Access Tools
echo ========================================
echo.
echo SQLite Database: diet_system.db
echo Location: c:\project4\Diet Recommendation System\backend\
echo.

echo 1. Opening SQLite Command Line...
echo.
echo Available Commands:
echo   .tables                    - Show all tables
echo   .schema                    - Show table structure
echo   SELECT * FROM users;        - View all users
echo   SELECT * FROM user_profiles; - View user profiles
echo   SELECT * FROM diet_logs;    - View meal logs
echo   SELECT * FROM exercise_logs; - View exercise logs
echo   SELECT * FROM water_logs;   - View water logs
echo   .quit                      - Exit SQLite
echo.

cd /d "c:\project4\Diet Recommendation System\backend"
sqlite3 diet_system.db

pause
