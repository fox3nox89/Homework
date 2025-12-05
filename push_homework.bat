@echo off
cd /d "%~dp0"

echo ====================================
echo  Homework: Auto-Git-Push
echo ====================================

rem Commit-Nachricht abfragen (optional)
set /p msg=Commit-Nachricht (Enter = Auto):

if "%msg%"=="" set msg=Auto-Commit %date% %time%

echo.
echo -> Dateien hinzufuegen...
git add .

echo -> Commit ausfuehren...
git commit -m "%msg%"

echo -> Push zu GitHub...
git push

echo.
echo Fertig. Fenster mit einer Taste schliessen.
pause
