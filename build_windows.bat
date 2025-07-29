@echo off
REM Windows build script for ftpdispatch standalone installer
REM This script creates a standalone Windows executable using PyInstaller

echo Building ftpdispatch Windows installer...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install build dependencies
echo Installing build dependencies...
pip install pyinstaller

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Install the package in development mode
echo Installing ftpdispatch in development mode...
pip install -e .

REM Build the executable
echo Building standalone executable...
pyinstaller --clean ftpdispatch.spec

REM Check if build was successful
if exist "dist\ftpdispatch.exe" (
    echo.
    echo SUCCESS: Standalone executable created!
    echo Location: dist\ftpdispatch.exe
    echo.
    echo You can now copy dist\ftpdispatch.exe to any Windows machine
    echo No Python installation required on target machine.
    echo.
    echo Usage: ftpdispatch.exe --base-dir "C:\path\to\your\directory"
    echo.
) else (
    echo.
    echo ERROR: Build failed. Check the output above for errors.
    echo.
)

pause