#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Debug Mode Launcher
"""

import subprocess
import time
import os
import sys

def start_chrome_debug():
    """Start Chrome Debug Mode"""
    print("🚀 Chrome Debug Mode Launcher")
    print("=" * 40)
    
    # Chrome paths
    chrome_paths = [
        r"C:\Users\David Wu\AppData\Local\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if not chrome_path:
        print("❌ Error: Chrome browser not found")
        print("Please ensure Chrome is properly installed")
        return False
    
    print(f"✅ Found Chrome: {chrome_path}")
    
    # Launch parameters
    debug_port = 9222
    user_data_dir = "chrome_debug_profile"
    
    # Build launch command
    cmd = [
        chrome_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    print(f"🔧 Launch Parameters:")
    print(f"  Debug Port: {debug_port}")
    print(f"  User Data Dir: {user_data_dir}")
    print()
    
    try:
        print("🚀 Starting Chrome...")
        # Launch Chrome
        process = subprocess.Popen(cmd)
        
        # Wait for startup
        time.sleep(3)
        
        print("✅ Chrome Started!")
        print()
        print("📋 Next Steps:")
        print("1. Visit https://x.com/home in the new Chrome window")
        print("2. Login to your Twitter account")
        print("3. Wait for page to fully load")
        print("4. Then run twitter_search_with_existing_browser.py")
        print()
        
        # Wait for user confirmation
        input("Press Enter to test connection...")
        
        # Test connection
        print("🔍 Testing Chrome connection...")
        from utils.browser_utils import connect_to_existing_chrome
        
        driver = connect_to_existing_chrome(debug_port)
        if driver:
            print("✅ Successfully connected to Chrome browser!")
            print(f"Current page: {driver.current_url}")
            driver = None
            print("Now you can run twitter_search_with_existing_browser.py")
            return True
        else:
            print("❌ Unable to connect to Chrome browser")
            print("Please ensure Chrome is properly started with debug mode")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Chrome: {str(e)}")
        return False

def main():
    """Main function"""
    if start_chrome_debug():
        print("\n✅ Setup completed!")
    else:
        print("\n❌ Setup failed!")
        print("Please manually start Chrome with the following command:")
        print("chrome.exe --remote-debugging-port=9222 --user-data-dir=chrome_debug_profile")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 