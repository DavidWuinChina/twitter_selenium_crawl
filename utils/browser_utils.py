#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器工具模块
包含Chrome浏览器设置和配置功能
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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