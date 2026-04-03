@echo off
echo Starting User Data Dashboard...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server...
echo Dashboard will be available at: http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
