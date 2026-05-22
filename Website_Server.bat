@echo off
title Portfolio Website Server
cd /d "E:\Introduction to GeoPandas-20220620T100205Z-001\ProtfolioWebsite"
start http://localhost:8000

echo ================================
echo    Portfolio Website Server
echo ================================
echo.
echo Serving from: docs/
echo URL: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================

python -m http.server 8000 --directory docs/

echo.
echo Server has been stopped.
echo You can close this window.
pause