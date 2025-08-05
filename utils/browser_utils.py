#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器工具模块
包含Chrome浏览器设置和配置功能
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import time

def setup_driver():
    """
    设置Chrome浏览器驱动
    
    Returns:
        webdriver.Chrome: 配置好的浏览器驱动
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"无法启动Chrome浏览器: {str(e)}")
        print("请确保已安装Chrome浏览器和ChromeDriver")
        return None 

        
def connect_to_existing_chrome(debug_port=9222):
    """
    连接到现有的Chrome浏览器会话
    
    Args:
        debug_port (int): Chrome调试端口，默认为9222
    
    Returns:
        webdriver.Chrome: 连接到现有会话的浏览器驱动
    """
    try:
        # 设置Chrome选项以连接到现有会话
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        
        # 尝试连接到现有Chrome会话
        driver = webdriver.Chrome(options=chrome_options)
        
        # 检查是否成功连接
        current_url = driver.current_url
        print(f"✅ 成功连接到现有Chrome会话")
        print(f"当前页面URL: {current_url}")
        
        return driver
        
    except Exception as e:
        print(f"❌ 无法连接到现有Chrome会话: {str(e)}")
        print("请确保Chrome浏览器已启动并开启了调试模式")
        return None

def start_chrome_with_debug(debug_port=9222):
    """
    启动Chrome浏览器并开启调试模式
    
    Args:
        debug_port (int): 调试端口号
    
    Returns:
        bool: 是否成功启动
    """
    try:
        # 尝试不同的Chrome路径
        chrome_paths = [
            "chrome.exe",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
        ]
        
        chrome_cmd = None
        for path in chrome_paths:
            try:
                # 测试路径是否存在
                if path == "chrome.exe":
                    # 尝试在PATH中查找
                    result = subprocess.run(["where", "chrome.exe"], capture_output=True, text=True)
                    if result.returncode == 0:
                        chrome_cmd = path
                        break
                else:
                    # 测试完整路径
                    expanded_path = os.path.expandvars(path)
                    if os.path.exists(expanded_path):
                        chrome_cmd = expanded_path
                        break
            except:
                continue
        
        if not chrome_cmd:
            print("❌ 无法找到Chrome浏览器")
            print("请手动启动Chrome浏览器，使用以下命令：")
            print(f"chrome.exe --remote-debugging-port={debug_port} --user-data-dir=chrome_debug_profile")
            return False
        
        # Windows系统启动Chrome的命令
        chrome_args = [
            chrome_cmd,
            f"--remote-debugging-port={debug_port}",
            "--user-data-dir=chrome_debug_profile",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        
        # 启动Chrome
        subprocess.Popen(chrome_args, shell=True)
        print(f"🚀 正在启动Chrome浏览器（调试端口: {debug_port}）...")
        
        # 等待浏览器启动
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ 启动Chrome浏览器失败: {str(e)}")
        return False

def setup_existing_browser_session(debug_port=9222):
    """
    设置现有浏览器会话（如果Chrome未启动则先启动）
    
    Args:
        debug_port (int): 调试端口号
    
    Returns:
        webdriver.Chrome: 浏览器驱动
    """
    # 首先尝试连接到现有会话
    driver = connect_to_existing_chrome(debug_port)
    
    if driver:
        return driver
    
    # 如果连接失败，尝试启动新的Chrome会话
    print("尝试启动新的Chrome调试会话...")
    if start_chrome_with_debug(debug_port):
        time.sleep(5)  # 等待浏览器完全启动
        return connect_to_existing_chrome(debug_port)
    
    return None 