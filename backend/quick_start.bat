@echo off
echo Starting Diet Backend with Debug Admin Setup...
python create_debug_admin.py
echo.
echo Starting Flask server...
cd /d "c:\project4\Diet Recommendation System\backend"
set PYTHONIOENCODING=utf-8 && python -c "import app; print('Backend ready!')" && python app.py
