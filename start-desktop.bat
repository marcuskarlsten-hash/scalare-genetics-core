@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv || goto error
)
".venv\Scripts\python.exe" -c "import PIL, tkinter" >nul 2>&1
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m pip install "Pillow>=10,<13" || goto error
)
".venv\Scripts\python.exe" desktop.py || goto error
exit /b 0
:error
 echo Could not start Scalare Genetics. Check Python and installation.
 pause
 exit /b 1
