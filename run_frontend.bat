@echo off
set "PATH=C:\Program Files\nodejs;%PATH%"
cd /d "C:\Users\nyusk\Desktop\AI Campaign\frontend"
if exist ".next" rmdir /s /q ".next"
call npm run build > "C:\Users\nyusk\Desktop\AI Campaign\run_logs\frontend.log" 2>&1
if errorlevel 1 exit /b 1
call npm run start >> "C:\Users\nyusk\Desktop\AI Campaign\run_logs\frontend.log" 2>&1
