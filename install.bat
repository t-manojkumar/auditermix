@echo off
setlocal enabledelayedexpansion
title auditermix  setup

:: ════════════════════════════════════════════════════════════
::  auditermix — Windows one-time installer
::  Auto-installs: Python 3.11+, ffmpeg, yt-dlp
::  Generates: .venv\, run.bat, Desktop shortcut
:: ════════════════════════════════════════════════════════════

:: Enable ANSI colours on Windows 10+
for /f "tokens=4-5 delims=. " %%i in ('ver') do set WINMAJ=%%i
if defined WINMAJ if %WINMAJ% GEQ 10 ( reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1 )

set "OR=[38;5;214m" & set "GR=[38;5;120m" & set "RE=[38;5;203m"
set "SM=[38;5;245m" & set "GH=[38;5;238m" & set "BO=[1m" & set "RS=[0m"

echo.
echo   %OR%╔══════════════════════════════════════════════╗%RS%
echo   %OR%║%RS%  auditermix  ^|  one-time setup              %OR%║%RS%
echo   %OR%╚══════════════════════════════════════════════╝%RS%
echo.


:: ── 1. PYTHON ─────────────────────────────────────────────────────────────

echo   %GH%checking python...%RS%
set "PYTHON_OK=0"

python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
    for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do set PYMAJ=%%a & set PYMIN=%%b
    if !PYMAJ! GEQ 3 if !PYMIN! GEQ 11 (
        set PYTHON_OK=1
        echo   %GR%✓%RS%  Python !PYVER! found
    ) else (
        echo   %OR%◆%RS%  Python !PYVER! is too old — need 3.11+
    )
)

if "!PYTHON_OK!"=="0" (
    echo   %OR%◆%RS%  Installing Python 3.11 via winget...
    winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo   %RE%✗%RS%  Auto-install failed. Please install manually:
        echo      https://python.org  — tick "Add Python to PATH"
        pause & exit /b 1
    )
    :: Refresh so Python is visible in PATH
    call refreshenv >nul 2>&1
    python --version >nul 2>&1
    if errorlevel 1 (
        echo   %OR%◆%RS%  Python installed — please close and re-run install.bat
        pause & exit /b 1
    )
    echo   %GR%✓%RS%  Python 3.11 installed
)


:: ── 2. FFMPEG ─────────────────────────────────────────────────────────────

echo   %GH%checking ffmpeg...%RS%
where ffmpeg >nul 2>&1
if not errorlevel 1 (
    echo   %GR%✓%RS%  ffmpeg found
    goto :ffmpeg_ok
)

echo   %OR%◆%RS%  ffmpeg not found — trying winget...
winget install --id Gyan.FFmpeg --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
where ffmpeg >nul 2>&1
if not errorlevel 1 ( echo   %GR%✓%RS%  ffmpeg installed via winget & goto :ffmpeg_ok )

echo   %OR%◆%RS%  winget failed — trying chocolatey...
where choco >nul 2>&1
if not errorlevel 1 (
    choco install ffmpeg -y --no-progress >nul 2>&1
    where ffmpeg >nul 2>&1
    if not errorlevel 1 ( echo   %GR%✓%RS%  ffmpeg installed via choco & goto :ffmpeg_ok )
)

echo.
echo   %RE%✗%RS%  Could not auto-install ffmpeg.
echo.
echo      Manual options:
echo        1.  winget install Gyan.FFmpeg
echo        2.  choco install ffmpeg     ^(if Chocolatey is installed^)
echo        3.  https://ffmpeg.org/download.html
echo            Add the bin\ folder to your PATH
echo.
pause & exit /b 1
:ffmpeg_ok


:: ── 3. VIRTUAL ENVIRONMENT ────────────────────────────────────────────────

echo   %GH%setting up virtual environment...%RS%
if exist .venv\ (
    echo   %GR%✓%RS%  .venv exists — skipping
) else (
    python -m venv .venv
    if errorlevel 1 ( echo   %RE%✗%RS%  venv creation failed & pause & exit /b 1 )
    echo   %GR%✓%RS%  .venv created
)


:: ── 4. YT-DLP ─────────────────────────────────────────────────────────────

echo   %GH%installing yt-dlp...%RS%
.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
.venv\Scripts\pip.exe install --quiet --upgrade yt-dlp
if errorlevel 1 ( echo   %RE%✗%RS%  pip install failed & pause & exit /b 1 )
echo   %GR%✓%RS%  yt-dlp ready


:: ── 5. LAUNCHERS ──────────────────────────────────────────────────────────

echo   %GH%writing launchers...%RS%

(
    echo @echo off
    echo title  auditermix
    echo cd /d "%%~dp0"
    echo .venv\Scripts\python.exe auditermix.py %%*
    echo if errorlevel 1 pause
) > run.bat
echo   %GR%✓%RS%  run.bat created

set "DSK=%USERPROFILE%\Desktop\auditermix.bat"
(
    echo @echo off
    echo title  auditermix
    echo cd /d "%~dp0"
    echo .venv\Scripts\python.exe "%~dp0auditermix.py"
    echo if errorlevel 1 pause
) > "%DSK%"
echo   %GR%✓%RS%  Desktop shortcut created


:: ── DONE ──────────────────────────────────────────────────────────────────

echo.
echo   %OR%╔══════════════════════════════════════════════╗%RS%
echo   %OR%║%RS%  %GR%✓%RS%  Setup complete!                        %OR%║%RS%
echo   %OR%╚══════════════════════════════════════════════╝%RS%
echo.
echo   Launch anytime:
echo     %SM%double-click  run.bat%RS%             (this folder)
echo     %SM%double-click  auditermix.bat%RS%      (Desktop)
echo.
pause
