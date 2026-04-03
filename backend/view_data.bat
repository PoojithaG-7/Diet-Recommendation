@echo off
echo ========================================
echo   Database Data Viewer
echo ========================================
echo.
echo This will show all data stored in the database
echo.
echo Available options:
echo 1. View All Users
echo 2. View User Profiles  
echo 3. View Recent Meals
echo 4. View Recent Exercises
echo 5. View Water Intake
echo 6. View Statistics
echo 7. Search User
echo 0. Exit
echo.
echo Starting database viewer...
echo.

cd /d "c:\project4\Diet Recommendation System\backend"
python simple_db_viewer.py

pause
