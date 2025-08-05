@echo off
chcp 65001 >nul
echo ========================================
echo Chrome Debug Mode Launcher
echo ========================================
echo.

set CHROME_PATH="C:\Users\David Wu\AppData\Local\Google\Chrome\Application\chrome.exe"
set DEBUG_PORT=9222
set USER_DATA_DIR=chrome_debug_profile

echo Chrome Path: %CHROME_PATH%
echo Debug Port: %DEBUG_PORT%
echo User Data Dir: %USER_DATA_DIR%
echo.

if not exist %CHROME_PATH% (
    echo ❌ Error: Chrome browser not found
    echo Please check if Chrome is installed
    pause
    exit /b 1
)

echo 🚀 Starting Chrome Debug Mode...
echo.

%CHROME_PATH% --remote-debugging-port=%DEBUG_PORT% --user-data-dir=%USER_DATA_DIR% --no-first-run --no-default-browser-check

echo.
echo ✅ Chrome Started!
echo.
echo 📋 Next Steps:
echo 1. Visit https://x.com/home in the new Chrome window
echo 2. Login to your Twitter account
echo 3. Wait for page to fully load
echo 4. Then run twitter_search_with_existing_browser.py
echo.
pause 