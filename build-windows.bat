@echo off
cd /d "%~dp0"
py -m pip install -r requirements-desktop.txt || goto error
py -m PyInstaller --noconfirm --clean --windowed --onedir --name ScalareGenetics --add-data "assets;assets" desktop.py || goto error
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" setup.iss
pause
exit /b
:error
pause
exit /b 1
