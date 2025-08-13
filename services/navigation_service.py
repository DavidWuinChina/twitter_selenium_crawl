#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航服务模块
处理Twitter页面导航和用户搜索
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from services.base_service import BaseService


class NavigationService(BaseService):
    """导航服务类，处理页面导航和用户搜索"""
    
    def direct_access_user_page(self, username):
        """
        直接访问用户页面
        
        Args:
            username (str): 用户名
        
        Returns:
            bool: 是否成功访问
        """
        try:
            print(f"直接访问用户 @{username} 的页面...")
            
            # 构建用户页面URL
            user_url = f"https://x.com/{username}"
            
            # 访问用户页面
            self.driver.get(user_url)
            time.sleep(3)  # 进一步优化页面加载等待时间到3秒
            
            print(f"✅ 已访问用户页面: {user_url}")
            return True
            
        except Exception as e:
            print(f"直接访问用户页面时出错: {str(e)}")
            return False
    
    def search_user(self, username):
        """
        搜索用户
        
        Args:
            username (str): 用户名
        
        Returns:
            bool: 是否成功搜索
        """
        try:
            print(f"搜索用户 @{username}...")
            
            # 查找搜索框
            search_selectors = [
                '[data-testid="SearchBox_Search_Input"]',
                'input[placeholder*="Search"]',
                'input[aria-label*="Search"]',
                '[data-testid="SearchBox"] input',
                'input[type="text"]',
                'input[placeholder*="搜索"]',
                'input[aria-label*="搜索"]',
                '[data-testid="SearchBox"]',
                'input[placeholder*="What"]',
                'input[placeholder*="Search Twitter"]',
                'input[placeholder*="Search X"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        search_input = elements[0]
                        break
                except:
                    continue
            
            if not search_input:
                print("❌ 无法找到搜索框")
                return False
            
            # 清空搜索框并输入用户名
            search_input.clear()
            time.sleep(1)
            search_input.send_keys(f"@{username}")
            time.sleep(1)
            search_input.send_keys(Keys.ENTER)
            
            print(f"✅ 已搜索用户 @{username}")
            return True
            
        except Exception as e:
            print(f"搜索用户时出错: {str(e)}")
            return False
    
    def click_user_profile(self, username):
        """
        点击用户资料链接
        
        Args:
            username (str): 用户名
        
        Returns:
            bool: 是否成功点击
        """
        try:
            print(f"点击用户 @{username} 的资料链接...")
            
            # 等待搜索结果加载
            time.sleep(3)
            
            # 查找用户链接 - 更全面的选择器
            user_link_selectors = [
                f'a[href="/{username}"]',
                f'a[href*="/{username}"]',
                f'[data-testid="UserCell"] a[href*="/{username}"]',
                f'[data-testid="User-{username}"]',
                f'a[href*="{username}"]',
                f'[data-testid="UserCell"] a',
                f'[data-testid="UserCell"]',
                f'a[href*="twitter.com/{username}"]',
                f'a[href*="x.com/{username}"]',
                f'[data-testid="UserCell"] div[role="link"]',
                f'[data-testid="UserCell"] span[role="link"]',
                f'[data-testid="UserCell"] a[href*="/{username.lower()}"]',
                f'a[href*="/{username.lower()}"]'
            ]
            
            user_link = None
            for selector in user_link_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # 检查元素是否包含目标用户名
                        for element in elements:
                            element_text = element.text.lower()
                            element_href = element.get_attribute('href') or ''
                            if username.lower() in element_text or username.lower() in element_href:
                                user_link = element
                                break
                        if user_link:
                            break
                except:
                    continue
            
            # 如果还是找不到，尝试更通用的方法
            if not user_link:
                print("尝试更通用的用户链接查找方法...")
                try:
                    # 查找所有可能的用户链接
                    all_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/"]')
                    for link in all_links:
                        href = link.get_attribute('href') or ''
                        if f'/{username}' in href or f'/{username.lower()}' in href:
                            user_link = link
                            break
                except:
                    pass
            
            if not user_link:
                print("❌ 无法找到用户链接")
                print("尝试直接访问用户页面...")
                try:
                    # 直接访问用户页面
                    user_url = f"https://x.com/{username}"
                    self.driver.get(user_url)
                    time.sleep(3)  # 进一步优化页面加载等待时间到3秒
                    print(f"✅ 已直接访问用户页面: {user_url}")
                    return True
                except Exception as e:
                    print(f"直接访问用户页面失败: {str(e)}")
                    return False
            
            # 点击用户链接
            user_link.click()
            print(f"✅ 已点击用户 @{username} 的链接")
            return True
            
        except Exception as e:
            print(f"点击用户链接时出错: {str(e)}")
            return False
    
    def verify_user_page(self, username):
        """
        验证是否在正确的用户页面
        
        Args:
            username (str): 用户名
        
        Returns:
            bool: 是否在正确的用户页面
        """
        try:
            # 检查当前URL
            current_url = self.driver.current_url
            print(f"当前页面URL: {current_url}")
            
            # 检查URL是否包含用户名
            if f"/{username}" in current_url or f"/{username.lower()}" in current_url:
                print(f"✅ 已导航到用户 @{username} 的页面")
                return True
            
            # 检查页面标题或内容是否包含用户名
            page_title = self.driver.title
            if username.lower() in page_title.lower():
                print(f"✅ 页面标题包含用户 @{username}")
                return True
            
            # 检查页面内容是否包含用户名
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if username.lower() in page_text:
                print(f"✅ 页面内容包含用户 @{username}")
                return True
            
            print(f"❌ 未导航到用户 @{username} 的正确页面")
            return False
            
        except Exception as e:
            print(f"验证用户页面时出错: {str(e)}")
            return False
