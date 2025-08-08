#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户信息提取模块
专门处理Twitter用户信息的提取
"""

import re
from selenium.webdriver.common.by import By
from services.base_service import BaseService


class UserInfoExtractor(BaseService):
    """用户信息提取器，提取Twitter用户的详细信息"""
    
    def extract_user_info(self, username):
        """
        提取用户信息
        
        Args:
            username (str): 用户名
        
        Returns:
            dict: 用户信息
        """
        try:
            user_info = {
                'username': username,
                'display_name': '未知',
                'description': '无法获取',
                'location': '未知',
                'verified': False,
                'followers_count': 0,
                'following_count': 0,
                'tweets_count': 0
            }
            
            # 获取显示名称
            self._extract_display_name(user_info)
            
            # 获取个人简介
            self._extract_description(user_info)
            
            # 获取位置信息
            self._extract_location(user_info)
            
            # 检查认证状态
            self._extract_verified_status(user_info)
            
            # 获取粉丝数
            self._extract_followers_count(user_info)
            
            # 获取关注数
            self._extract_following_count(user_info)
            
            # 获取推文数
            self._extract_tweets_count(user_info)
            
            print(f"✅ 已提取用户信息: {user_info['display_name']}")
            print(f"📊 粉丝数: {user_info['followers_count']}")
            print(f"📍 位置: {user_info['location']}")
            print(f"✅ 认证状态: {user_info['verified']}")
            return user_info
            
        except Exception as e:
            print(f"提取用户信息时出错: {str(e)}")
            return {
                'username': username, 
                'display_name': '未知', 
                'description': '无法获取', 
                'location': '未知', 
                'verified': False,
                'followers_count': 0,
                'following_count': 0,
                'tweets_count': 0
            }
    
    def _extract_display_name(self, user_info):
        """提取显示名称"""
        try:
            name_selectors = [
                '[data-testid="UserName"]',
                '[data-testid="UserName"] span',
                'h1[data-testid="UserName"]',
                '[data-testid="UserName"] div'
            ]
            
            for selector in name_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    user_info['display_name'] = elements[0].text.strip()
                    break
        except Exception as e:
            print(f"提取显示名称时出错: {str(e)}")
    
    def _extract_description(self, user_info):
        """提取个人简介"""
        try:
            bio_selectors = [
                '[data-testid="UserDescription"]',
                '[data-testid="UserBio"]',
                '.css-1rynq56'
            ]
            
            for selector in bio_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    user_info['description'] = elements[0].text.strip()
                    break
        except Exception as e:
            print(f"提取个人简介时出错: {str(e)}")
    
    def _extract_location(self, user_info):
        """提取位置信息"""
        try:
            location_selectors = [
                '[data-testid="UserLocation"]',
                '[data-testid="UserProfileHeader_Items"] span'
            ]
            
            for selector in location_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    user_info['location'] = elements[0].text.strip()
                    break
        except Exception as e:
            print(f"提取位置信息时出错: {str(e)}")
    
    def _extract_verified_status(self, user_info):
        """检查认证状态"""
        try:
            verified_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserVerifiedBadge"]')
            if verified_elements:
                user_info['verified'] = True
        except Exception as e:
            print(f"检查认证状态时出错: {str(e)}")
    
    def _extract_followers_count(self, user_info):
        """获取粉丝数"""
        try:
            # 调试：打印页面上所有包含"followers"的元素
            print("🔍 调试：搜索粉丝数元素...")
            all_followers_elements = self.driver.find_elements(By.CSS_SELECTOR, '*[href*="/followers"]')
            print(f"找到 {len(all_followers_elements)} 个包含followers链接的元素")
            for i, elem in enumerate(all_followers_elements[:5]):  # 只打印前5个
                print(f"  元素 {i+1}: {elem.text.strip()}")
            
            # 调试：打印所有verified_followers链接
            verified_followers_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/verified_followers"]')
            print(f"找到 {len(verified_followers_elements)} 个verified_followers链接")
            for i, elem in enumerate(verified_followers_elements):
                print(f"  verified_followers {i+1}: {elem.text.strip()}")
            
            # 调试：打印所有UserProfileStats元素
            profile_stats_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserProfileStats"]')
            print(f"找到 {len(profile_stats_elements)} 个UserProfileStats元素")
            for i, elem in enumerate(profile_stats_elements):
                print(f"  UserProfileStats {i+1}: {elem.text.strip()}")
            
            followers_selectors = [
                'a[href*="/verified_followers"] span',
                'a[href*="/followers"] span',
                '[data-testid="UserFollowersCount"]',
                '[data-testid="UserProfileStats"] a[href*="/followers"] span',
                'a[href*="/followers"]',
                '[data-testid="UserProfileStats"] span',
                '[data-testid="UserProfileStats"] a[href*="/followers"]',
                'a[href*="/followers"] div',
                '[data-testid="UserProfileStats"] div a[href*="/followers"]',
                '[data-testid="UserProfileStats"] a[href*="/followers"] div',
                'div[data-testid="UserProfileStats"] a[href*="/followers"]',
                'div[data-testid="UserProfileStats"] a[href*="/followers"] span',
                'div[data-testid="UserProfileStats"] a[href*="/followers"] div',
                'a[href*="/followers"] strong',
                'a[href*="/followers"] b',
                'a[href*="/followers"] span strong',
                'a[href*="/followers"] span b',
                '[data-testid="UserProfileStats"] a[href*="/followers"] strong',
                '[data-testid="UserProfileStats"] a[href*="/followers"] b',
                'div[data-testid="UserProfileStats"] a[href*="/followers"] strong',
                'div[data-testid="UserProfileStats"] a[href*="/followers"] b'
            ]
            
            for selector in followers_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        followers_text = element.text.strip()
                        # 提取数字，处理K、M等单位
                        if followers_text:
                            # 移除逗号和其他非数字字符，保留K、M等
                            followers_clean = re.sub(r'[^\d.KMB万]', '', followers_text)
                            if followers_clean and followers_clean != '0':
                                user_info['followers_count'] = followers_clean
                                print(f"找到粉丝数: {followers_clean}")
                                break
                    if user_info['followers_count'] != 0:
                        break
        except Exception as e:
            print(f"获取粉丝数时出错: {str(e)}")
    
    def _extract_following_count(self, user_info):
        """获取关注数"""
        try:
            following_selectors = [
                'a[href*="/following"] span',
                '[data-testid="UserFollowingCount"]',
                '[data-testid="UserProfileStats"] a[href*="/following"] span',
                'a[href*="/following"]',
                'a[href*="/following"] div',
                'a[href*="/following"] strong',
                'a[href*="/following"] b'
            ]
            
            for selector in following_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        following_text = element.text.strip()
                        if following_text:
                            # 移除逗号和其他非数字字符，保留K、M等
                            following_clean = re.sub(r'[^\d.KMB万]', '', following_text)
                            if following_clean and following_clean != '0':
                                user_info['following_count'] = following_clean
                                print(f"找到关注数: {following_clean}")
                                break
                    if user_info['following_count'] != 0:
                        break
        except Exception as e:
            print(f"获取关注数时出错: {str(e)}")
    
    def _extract_tweets_count(self, user_info):
        """获取推文数"""
        try:
            # Twitter的推文数通常显示在用户资料的统计信息中
            tweets_selectors = [
                '[data-testid="UserTweetsCount"]',
                '[data-testid="UserProfileStats"] span',
                '[data-testid="UserProfileStats"] div'
            ]
            
            for selector in tweets_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        tweets_text = element.text.strip()
                        # 查找包含"tweet"或"推文"的文本
                        if any(keyword in tweets_text.lower() for keyword in ['tweet', 'post', '推文', '条']):
                            # 提取数字
                            tweets_clean = re.sub(r'[^\d.KMB万]', '', tweets_text)
                            if tweets_clean and tweets_clean != '0':
                                user_info['tweets_count'] = tweets_clean
                                print(f"找到推文数: {tweets_clean}")
                                break
                    if user_info['tweets_count'] != 0:
                        break
        except Exception as e:
            print(f"获取推文数时出错: {str(e)}")
