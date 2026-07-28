@echo off
cd /d "%~dp0"
start "BACKEND 5000" cmd /k "cd /d %~dp0backend && py -m pip install -r requirements.txt && py app.py"
start "FRONTEND 5173" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"
echo Backend va frontend ishga tushyapti...
echo Brauzerda oching: http://localhost:5173/
pause
