#!/bin/bash
# Cross-platform build script for ftpdispatch Windows installer
# This script can be run on Linux/macOS to build Windows executable

set -e

echo "Building ftpdispatch Windows installer..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Install build dependencies
echo "Installing build dependencies..."
pip install pyinstaller

# Clean previous builds
rm -rf build/ dist/

# Install the package in development mode
echo "Installing ftpdispatch in development mode..."
pip install -e .

# Build the executable
echo "Building standalone executable..."
pyinstaller --clean ftpdispatch.spec

# Check if build was successful
if [ -f "dist/ftpdispatch.exe" ] || [ -f "dist/ftpdispatch" ]; then
    echo
    echo "SUCCESS: Standalone executable created!"
    echo "Location: dist/"
    echo
    echo "You can now copy the executable to any Windows machine"
    echo "No Python installation required on target machine."
    echo
    echo "Usage: ./ftpdispatch --base-dir \"/path/to/your/directory\""
    echo
else
    echo
    echo "ERROR: Build failed. Check the output above for errors."
    echo
fi