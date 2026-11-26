@echo off
setlocal
cd /d "%~dp0"

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo Installera Inno Setup 6 innan du bygger installationsfilen.
    goto error
)

py -m pip install -r requirements-desktop.txt || goto error
py -m PyInstaller --noconfirm --clean --windowed --onedir --name ScalareGenetics --add-data "assets;assets" desktop.py || goto error
"%ISCC%" setup.iss || goto error
echo Installationsfil: Output\ScalareGeneticsSetup.exe
pause
exit /b 0

:error
pause
exit /b 1
