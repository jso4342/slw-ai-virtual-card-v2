#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================="
echo " 🚀 Virtual Card Generator Local Server"
echo "=========================================="
echo "Port: http://localhost:8090"
echo "Passcode: SLW2026"
echo "=========================================="
echo ""

export DYLD_LIBRARY_PATH="/Users/syjjang/Library/Frameworks/Python.framework/Versions/3.12/lib"
/Users/syjjang/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 run.py

echo ""
echo "Press enter to exit..."
read
