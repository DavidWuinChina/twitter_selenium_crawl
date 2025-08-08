#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础服务模块
提供浏览器连接和基本功能
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.browser_utils import connect_to_existing_chrome


class BaseService:
    """基础服务类，提供浏览器连接和基本功能"""
    
    def __init__(self, debug_port=9222):
        """
        初始化基础服务
        
        Args:
            debug_port (int): Chrome调试端口
        """
        self.debug_port = debug_port
        self.driver = None
    
    def connect_to_browser(self):
        """
        连接到现有的Chrome浏览器会话
        
        Returns:
            bool: 是否成功连接
        """
        try:
            self.driver = connect_to_existing_chrome(self.debug_port)
            if self.driver:
                print("✅ 成功连接到现有浏览器会话")
                return True
            else:
                print("❌ 无法连接到现有浏览器会话")
                return False
        except Exception as e:
            print(f"❌ 连接浏览器时出错: {str(e)}")
            return False
    
    def ensure_on_twitter_home(self):
        """确保在Twitter主页"""
        try:
            current_url = self.driver.current_url
            if 'twitter.com' not in current_url and 'x.com' not in current_url:
                print("导航到Twitter主页...")
                self.driver.get("https://twitter.com/")
                time.sleep(3)
            return True
        except Exception as e:
            print(f"导航到Twitter主页时出错: {str(e)}")
            return False
    
    def wait_for_element(self, by, value, timeout=10):
        """
        等待元素出现
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超时时间
            
        Returns:
            WebElement or None: 找到的元素
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return None
    
    def wait_for_clickable_element(self, by, value, timeout=10):
        """
        等待元素可点击
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超时时间
            
        Returns:
            WebElement or None: 找到的元素
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable((by, value)))
        except TimeoutException:
            return None
    
    def scroll_page(self, pixels=600):
        """
        滚动页面
        
        Args:
            pixels (int): 滚动像素数
        """
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
    
    def get_page_height(self):
        """获取页面高度"""
        return self.driver.execute_script("return document.body.scrollHeight")
    
    def get_scroll_position(self):
        """获取当前滚动位置"""
        return self.driver.execute_script("return window.pageYOffset")
    
    def is_connected(self):
        """检查是否已连接到浏览器"""
        return self.driver is not None
    
    def close_connection(self):
        """关闭浏览器连接"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("✅ 已关闭浏览器连接")
            except Exception as e:
                print(f"关闭浏览器连接时出错: {str(e)}")
