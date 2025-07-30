#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter爬取服务模块
包含用户信息获取和推文获取功能
"""

import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.browser_utils import setup_driver

class TwitterScraperService:
    """
    Twitter爬取服务类
    负责获取Twitter用户信息和推文
    """
    
    def __init__(self):
        """初始化Twitter爬取服务"""
        self.driver = None
    
    def get_user_profile(self, username):
        """
        获取Twitter用户信息
        
        Args:
            username (str): Twitter用户名（不包含@符号）
        
        Returns:
            dict: 包含用户信息的字典
        """
        self.driver = None
        try:
            # 设置浏览器驱动
            self.driver = setup_driver()
            if not self.driver:
                return None
            
            # 构建Twitter用户页面URL
            url = f"https://twitter.com/{username}"
            
            print(f"正在使用Selenium访问: {url}")
            
            # 访问页面
            self.driver.get(url)
            
            # 等待页面加载
            print("等待页面加载...")
            time.sleep(5)
            
            # 尝试等待页面元素加载
            wait = WebDriverWait(self.driver, 10)
            print("页面加载完成")
            
            profile_data = {
                'username': username,
                'display_name': '未知',
                'description': '无法获取',
                'location': '未知',
                'followers_count': 0,
                'following_count': 0,
                'tweets_count': 0,
                'verified': False,
                'created_at': None,
                'profile_image_url': None,
                'banner_url': None,
                'url': url,
                'protected': False,
                'scraped_at': datetime.now().isoformat(),
                'page_title': self.driver.title,
                'recent_tweets': []  # 添加最近推文列表
            }
            
            try:
                # 尝试获取页面标题
                profile_data['display_name'] = self.driver.title.strip()
                
                # 获取用户基本信息
                self._extract_user_info(profile_data)
                
                # 获取页面截图（用于调试）
                import os
                # 获取当前脚本文件所在的目录
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # 获取项目根目录（services的父目录）
                project_dir = os.path.dirname(script_dir)
                # 在项目根目录下创建results目录
                results_dir = os.path.join(project_dir, 'results')
                if not os.path.exists(results_dir):
                    os.makedirs(results_dir)
                screenshot_path = os.path.join(results_dir, f"twitter_profile_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"页面截图已保存: {screenshot_path}")
                
                # 获取最近十条推文
                try:
                    print("正在获取最近十条推文...")
                    tweets = self._get_recent_tweets(10)
                    profile_data['recent_tweets'] = tweets
                    print(f"成功获取 {len(tweets)} 条推文")
                except Exception as e:
                    print(f"获取推文时出错: {str(e)}")
                
            except Exception as e:
                print(f"解析页面内容时出错: {str(e)}")
            
            return profile_data
            
        except Exception as e:
            print(f"使用Selenium爬取时发生错误: {str(e)}")
            return None
        finally:
            try:
                if self.driver:
                    print("正在关闭浏览器...")
                    self.driver.quit()
                    print("浏览器已关闭")
            except Exception as e:
                print(f"关闭浏览器时出错: {str(e)}")
    
    def _extract_user_info(self, profile_data):
        """
        提取用户基本信息
        
        Args:
            profile_data (dict): 用户信息字典
        """
        try:
            # 尝试获取个人简介
            try:
                # 查找个人简介元素（可能需要根据实际页面结构调整）
                bio_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserDescription"]')
                if bio_elements:
                    profile_data['description'] = bio_elements[0].text.strip()
                
                # 尝试其他可能的选择器
                if profile_data['description'] == '无法获取':
                    bio_elements = self.driver.find_elements(By.CSS_SELECTOR, '.css-1rynq56')
                    if bio_elements:
                        profile_data['description'] = bio_elements[0].text.strip()
                        
            except Exception as e:
                print(f"获取个人简介时出错: {str(e)}")
            
            # 尝试获取位置信息
            try:
                location_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserLocation"]')
                if location_elements:
                    profile_data['location'] = location_elements[0].text.strip()
            except Exception as e:
                print(f"获取位置信息时出错: {str(e)}")
            
            # 尝试获取粉丝数
            try:
                followers_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserFollowersCount"]')
                if followers_elements:
                    followers_text = followers_elements[0].text.strip()
                    # 提取数字
                    numbers = re.findall(r'\d+', followers_text)
                    if numbers:
                        profile_data['followers_count'] = int(''.join(numbers))
            except Exception as e:
                print(f"获取粉丝数时出错: {str(e)}")
            
            # 尝试获取关注数
            try:
                following_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserFollowingCount"]')
                if following_elements:
                    following_text = following_elements[0].text.strip()
                    numbers = re.findall(r'\d+', following_text)
                    if numbers:
                        profile_data['following_count'] = int(''.join(numbers))
            except Exception as e:
                print(f"获取关注数时出错: {str(e)}")
            
            # 尝试获取推文数
            try:
                tweets_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserTweetsCount"]')
                if tweets_elements:
                    tweets_text = tweets_elements[0].text.strip()
                    numbers = re.findall(r'\d+', tweets_text)
                    if numbers:
                        profile_data['tweets_count'] = int(''.join(numbers))
            except Exception as e:
                print(f"获取推文数时出错: {str(e)}")
            
            # 检查是否认证
            try:
                verified_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserVerifiedBadge"]')
                profile_data['verified'] = len(verified_elements) > 0
            except Exception as e:
                print(f"检查认证状态时出错: {str(e)}")
                
        except Exception as e:
            print(f"提取用户信息时出错: {str(e)}")
    
    def _get_recent_tweets(self, max_tweets=10):
        """
        获取用户最近推文
        
        Args:
            max_tweets (int): 最大推文数量
        
        Returns:
            list: 推文列表
        """
        tweets = []
        try:
            # 等待推文加载
            time.sleep(3)
            
            # 尝试多种推文选择器
            tweet_selectors = [
                '[data-testid="tweet"]',
                '[data-testid="tweetText"]',
                'article[data-testid="tweet"]',
                '.css-1rynq56[data-testid="tweetText"]',
                '[data-testid="cellInnerDiv"]'
            ]
            
            for selector in tweet_selectors:
                try:
                    tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if tweet_elements:
                        print(f"找到 {len(tweet_elements)} 个推文元素 (选择器: {selector})")
                        
                        for i, tweet_element in enumerate(tweet_elements[:max_tweets]):
                            try:
                                # 尝试获取推文文本
                                tweet_text = ""
                                
                                # 方法1: 直接获取文本
                                tweet_text = tweet_element.text.strip()
                                
                                # 方法2: 查找特定的推文文本元素
                                if not tweet_text or len(tweet_text) < 10:
                                    text_elements = tweet_element.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                                    if text_elements:
                                        tweet_text = text_elements[0].text.strip()
                                
                                # 方法3: 查找其他可能的文本元素
                                if not tweet_text or len(tweet_text) < 10:
                                    text_elements = tweet_element.find_elements(By.CSS_SELECTOR, '.css-1rynq56')
                                    if text_elements:
                                        tweet_text = text_elements[0].text.strip()
                                
                                # 清理推文文本
                                if tweet_text and len(tweet_text) > 10:
                                    # 移除多余的空白字符
                                    tweet_text = re.sub(r'\s+', ' ', tweet_text).strip()
                                    
                                    # 检查是否是有效的推文（不是导航、按钮等）
                                    if not any(keyword in tweet_text.lower() for keyword in ['follow', 'following', 'followers', 'tweets', 'likes', 'retweets']):
                                        tweet_data = {
                                            'index': i + 1,
                                            'text': tweet_text,
                                            'length': len(tweet_text)
                                        }
                                        tweets.append(tweet_data)
                                        print(f"推文 {i+1}: {tweet_text[:50]}...")
                                        
                                        if len(tweets) >= max_tweets:
                                            break
                                            
                            except Exception as e:
                                print(f"处理推文 {i+1} 时出错: {str(e)}")
                                continue
                        
                        if tweets:
                            break  # 如果找到推文，跳出选择器循环
                            
                except Exception as e:
                    print(f"使用选择器 {selector} 时出错: {str(e)}")
                    continue
            
            # 如果没有找到推文，尝试滚动页面
            if not tweets:
                print("尝试滚动页面获取更多推文...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # 重新尝试获取推文
                for selector in tweet_selectors:
                    try:
                        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if tweet_elements:
                            for i, tweet_element in enumerate(tweet_elements[:max_tweets]):
                                tweet_text = tweet_element.text.strip()
                                if tweet_text and len(tweet_text) > 10:
                                    tweet_text = re.sub(r'\s+', ' ', tweet_text).strip()
                                    if not any(keyword in tweet_text.lower() for keyword in ['follow', 'following', 'followers', 'tweets', 'likes', 'retweets']):
                                        tweet_data = {
                                            'index': i + 1,
                                            'text': tweet_text,
                                            'length': len(tweet_text)
                                        }
                                        tweets.append(tweet_data)
                                        if len(tweets) >= max_tweets:
                                            break
                    except:
                        continue
                        
        except Exception as e:
            print(f"获取推文时发生错误: {str(e)}")
        
        return tweets 