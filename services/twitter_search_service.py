#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter搜索服务模块
专门用于在现有浏览器会话中搜索用户并获取推文
"""

import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from utils.browser_utils import connect_to_existing_chrome

class TwitterSearchService:
    """
    Twitter搜索服务类
    在现有浏览器会话中搜索用户并获取推文
    """
    
    def __init__(self, debug_port=9222):
        """
        初始化Twitter搜索服务
        
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
    
    def search_user_and_get_tweets(self, username, max_tweets=50):
        """
        搜索用户并获取推文
        
        Args:
            username (str): 要搜索的用户名
            max_tweets (int): 最大推文数量
        
        Returns:
            dict: 包含用户信息和推文的字典
        """
        if not self.driver:
            if not self.connect_to_browser():
                return None
        
        try:
            print(f"🔍 开始搜索用户 @{username}")
            
            # 直接访问用户页面
            if not self._direct_access_user_page(username):
                print(f"❌ 无法访问用户 @{username} 的页面")
                return None
            
            # 等待用户页面加载
            time.sleep(5)
            
            # 验证是否导航到正确的用户页面
            if not self._verify_user_page(username):
                print(f"❌ 未能导航到用户 @{username} 的正确页面")
                return None
            
            # 获取用户信息
            user_info = self._extract_user_info(username)
            
            # 如果用户信息获取失败，尝试重新获取
            if user_info['display_name'] == '未知':
                print("重新尝试获取用户信息...")
                time.sleep(2)
                user_info = self._extract_user_info(username)
            
            # 获取推文
            tweets = self._get_user_tweets(max_tweets)
            
            # 合并数据
            result = {
                'username': username,
                'user_info': user_info,
                'tweets': tweets,
                'scraped_at': datetime.now().isoformat(),
                'tweets_count': len(tweets)
            }
            
            print(f"✅ 成功获取用户 @{username} 的信息和 {len(tweets)} 条推文")
            return result
            
        except Exception as e:
            print(f"❌ 搜索用户时出错: {str(e)}")
            return None
    
    def _ensure_on_twitter_home(self):
        """确保在Twitter主页"""
        try:
            current_url = self.driver.current_url
            
            # 如果不在Twitter主页，导航到主页
            if "x.com/home" not in current_url and "twitter.com/home" not in current_url:
                print("导航到Twitter主页...")
                self.driver.get("https://x.com/home")
                time.sleep(3)
            
            print("✅ 已在Twitter主页")
            
        except Exception as e:
            print(f"确保在Twitter主页时出错: {str(e)}")
    
    def _direct_access_user_page(self, username):
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
            time.sleep(3)
            
            print(f"✅ 已访问用户页面: {user_url}")
            return True
            
        except Exception as e:
            print(f"直接访问用户页面时出错: {str(e)}")
            return False
    
    def _search_user(self, username):
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
    
    def _click_user_profile(self, username):
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
                    time.sleep(3)
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
    
    def _verify_user_page(self, username):
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
            
            print(f"❌ 当前页面不是用户 @{username} 的页面")
            return False
            
        except Exception as e:
            print(f"验证用户页面时出错: {str(e)}")
            return False
    
    def _extract_user_info(self, username):
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
            except:
                pass
            
            # 获取个人简介
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
            except:
                pass
            
            # 获取位置信息
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
            except:
                pass
            
            # 检查认证状态
            try:
                verified_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserVerifiedBadge"]')
                if verified_elements:
                    user_info['verified'] = True
            except:
                pass
            
            # 获取粉丝数
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
                pass
            
            print(f"✅ 已提取用户信息: {user_info['display_name']}")
            print(f"📊 粉丝数: {user_info['followers_count']}")
            print(f"📍 位置: {user_info['location']}")
            print(f"✅ 认证状态: {user_info['verified']}")
            return user_info
            
        except Exception as e:
            print(f"提取用户信息时出错: {str(e)}")
            return {'username': username, 'display_name': '未知', 'description': '无法获取', 'location': '未知', 'verified': False}
    
    def _get_user_tweets(self, max_tweets=50):
        """
        获取用户推文
        
        Args:
            max_tweets (int): 最大推文数量
        
        Returns:
            list: 推文列表
        """
        tweets = []
        seen_tweets = set()  # 用于去重
        try:
            print(f"获取用户推文（目标: {max_tweets}条）...")
            
            # 等待推文加载
            time.sleep(5)
            
            # 无限滚动页面以加载更多推文
            print("开始无限滚动加载推文...")
            scroll_count = 0
            max_scrolls = 500  # 增加最大滚动次数到500次
            
            while len(tweets) < max_tweets and scroll_count < max_scrolls:
                scroll_count += 1
                
                # 滚动600像素（平衡效率和精确性）
                self.driver.execute_script("window.scrollBy(0, 600);")  # 每次滚动600像素
                time.sleep(2)  # 等待2秒
                
                # 使用更简单有效的选择器
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                # 如果找不到推文，尝试其他选择器
                if not tweet_elements:
                    tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                
                # 如果还是找不到，尝试更通用的选择器
                if not tweet_elements:
                    tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article')
                
                # 调试信息
                if scroll_count == 1:
                    print(f"调试：找到 {len(tweet_elements)} 个推文元素")
                    if tweet_elements:
                        print(f"第一个元素的文本长度: {len(tweet_elements[0].text)}")
                        print(f"第一个元素的前100字符: {tweet_elements[0].text[:100]}")
                
                current_tweet_count = len(tweet_elements)
                
                print(f"滚动 {scroll_count}: 找到 {current_tweet_count} 个推文元素")
                
                # 每次滚动都尝试提取推文
                if tweet_elements:
                    print(f"尝试提取推文... (已滚动 {scroll_count} 次)")
                    current_tweets = self._extract_tweets_from_elements_with_dedup(tweet_elements, seen_tweets, max_tweets)
                    
                    if current_tweets:
                        # 添加新推文到结果中
                        for tweet in current_tweets:
                            if len(tweets) < max_tweets:
                                tweets.append(tweet)
                                seen_tweets.add(tweet['text'][:50])  # 使用前50字符作为唯一标识
                        
                        print(f"已提取 {len(tweets)} 条推文")
                
                # 如果已经达到目标数量，停止滚动
                if len(tweets) >= max_tweets:
                    print(f"已达到目标推文数量: {max_tweets}")
                    break
            
            print(f"✅ 成功获取 {len(tweets)} 条推文")
            return tweets
            
        except Exception as e:
            print(f"获取推文时出错: {str(e)}")
            return []
    
    def _extract_tweets_from_elements(self, tweet_elements, max_tweets):
        """
        从推文元素中提取推文数据
        
        Args:
            tweet_elements: 推文元素列表
            max_tweets (int): 最大推文数量
        
        Returns:
            list: 推文列表
        """
        tweets = []
        seen_tweets = set()
        
        for i, element in enumerate(tweet_elements):
            try:
                tweet_data = self._extract_tweet_data(element)
                
                if tweet_data and tweet_data['text'] and len(tweet_data['text']) > 5:
                    # 创建推文唯一标识
                    tweet_id = tweet_data['text'][:50]
                    
                    if tweet_id not in seen_tweets:
                        seen_tweets.add(tweet_id)
                        tweet_data['index'] = len(tweets) + 1
                        tweets.append(tweet_data)
                        
                        if len(tweets) >= max_tweets:
                            break
            
            except Exception as e:
                print(f"处理推文元素时出错: {str(e)}")
                continue
        
        return tweets
    
    def _extract_tweets_from_elements_with_dedup(self, tweet_elements, seen_tweets, max_tweets):
        """
        从推文元素中提取推文数据（带去重）
        
        Args:
            tweet_elements: 推文元素列表
            seen_tweets (set): 已见过的推文集合
            max_tweets (int): 最大推文数量
        
        Returns:
            list: 新推文列表
        """
        new_tweets = []
        
        for i, element in enumerate(tweet_elements):
            try:
                tweet_data = self._extract_tweet_data(element)
                
                if tweet_data and tweet_data['text'] and len(tweet_data['text']) > 5:
                    # 创建推文唯一标识
                    tweet_id = tweet_data['text'][:50]
                    
                    if tweet_id not in seen_tweets:
                        # 不在这里设置index，等最终排序后再设置
                        new_tweets.append(tweet_data)
            
            except Exception as e:
                print(f"处理推文元素时出错: {str(e)}")
                continue
        
        return new_tweets
    
    def _extract_tweet_data(self, tweet_element):
        """
        从推文元素中提取数据
        
        Args:
            tweet_element: 推文元素
        
        Returns:
            dict: 推文数据
        """
        try:
            # 获取完整文本
            full_text = tweet_element.text.strip()
            
            # 获取推文文本 - 使用多种方法
            tweet_text = ""
            
            # 方法1：查找tweetText元素
            try:
                text_elements = tweet_element.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                if text_elements:
                    tweet_text = text_elements[0].text.strip()
            except:
                pass
            
            # 方法2：查找带有lang属性的div
            if not tweet_text:
                try:
                    text_elements = tweet_element.find_elements(By.CSS_SELECTOR, 'div[lang]')
                    if text_elements:
                        tweet_text = text_elements[0].text.strip()
                except:
                    pass
            
            # 方法3：查找所有span元素
            if not tweet_text:
                try:
                    text_elements = tweet_element.find_elements(By.CSS_SELECTOR, 'span')
                    for span in text_elements:
                        span_text = span.text.strip()
                        if len(span_text) > 10 and not any(keyword in span_text.lower() for keyword in ['follow', 'like', 'retweet', 'reply', 'view', 'share', 'more']):
                            tweet_text = span_text
                            break
                except:
                    pass
            
            # 方法4：从完整文本中提取
            if not tweet_text and full_text:
                lines = full_text.split('\n')
                for line in lines:
                    if len(line) > 10 and not any(keyword in line.lower() for keyword in ['follow', 'like', 'retweet', 'reply', 'view', 'share', 'more']):
                        tweet_text = line.strip()
                        break
            
            # 方法5：如果还是没有找到，使用完整文本的前100个字符
            if not tweet_text and full_text:
                tweet_text = full_text[:100].strip()
            
            # 如果推文文本太短，跳过
            if not tweet_text or len(tweet_text) < 5:
                return None
            
            # 提取日期
            date = self._extract_tweet_date(full_text)
            
            # 提取互动数据
            interactions = self._extract_interactions(full_text)
            
            return {
                'text': tweet_text,
                'full_text': full_text,
                'date': date,
                'interactions': interactions,
                'length': len(tweet_text)
            }
            
        except Exception as e:
            # 不打印错误，静默处理
            return None
    
    def _extract_tweet_date(self, full_text):
        """提取推文日期"""
        try:
            date_patterns = [
                r'·\s*(\d{1,2}月\d{1,2}日)',
                r'·\s*(\d{4}年\d{1,2}月\d{1,2}日)',
                r'·\s*([A-Za-z]{3}\s+\d+)',
                r'·\s*([A-Za-z]{3}\s+\d+,\s+\d{4})',
                r'·\s*(\d{1,2}/\d{1,2})',
                r'·\s*(\d{1,2}/\d{1,2}/\d{4})',
                r'·\s*(\d{1,2}-\d{1,2})',
                r'·\s*(\d{1,2}-\d{1,2}-\d{4})',
                r'·\s*(\d{1,2}\.\d{1,2})',
                r'·\s*(\d{1,2}\.\d{1,2}\.\d{4})',
                # 不带点的格式
                r'(\d{1,2}月\d{1,2}日)',
                r'(\d{4}年\d{1,2}月\d{1,2}日)',
                r'([A-Za-z]{3}\s+\d+)',
                r'([A-Za-z]{3}\s+\d+,\s+\d{4})',
                r'(\d{1,2}/\d{1,2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
                r'(\d{1,2}\.\d{1,2})',
                r'(\d{1,2}\.\d{1,2}\.\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, full_text)
                if match:
                    return match.group(1)
            
            return "未知日期"
        except:
            return "未知日期"
    
    def _extract_interactions(self, full_text):
        """提取互动数据"""
        try:
            # 移除日期部分
            date_removed = re.sub(r'·\s*(\d{1,2}月\d{1,2}日)', '', full_text)
            date_removed = re.sub(r'·\s*(\d{4}年\d{1,2}月\d{1,2}日)', '', date_removed)
            date_removed = re.sub(r'·\s*([A-Za-z]{3}\s+\d+)', '', date_removed)
            date_removed = re.sub(r'·\s*([A-Za-z]{3}\s+\d+,\s+\d{4})', '', date_removed)
            
            # 提取数字
            numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', date_removed)
            
            # 过滤数字
            filtered_numbers = []
            for num in numbers:
                if not (len(num) == 4 and num.startswith('20')):  # 排除年份
                    if not (len(num) <= 2 and int(num) <= 31):  # 排除日期
                        filtered_numbers.append(num)
            
            if len(filtered_numbers) >= 4:
                return {
                    'likes': filtered_numbers[0],
                    'retweets': filtered_numbers[1],
                    'replies': filtered_numbers[2],
                    'views': filtered_numbers[3]
                }
            elif len(filtered_numbers) >= 3:
                return {
                    'likes': filtered_numbers[0],
                    'retweets': filtered_numbers[1],
                    'replies': filtered_numbers[2],
                    'views': ''
                }
            else:
                return {'likes': '', 'retweets': '', 'replies': '', 'views': ''}
        except:
            return {'likes': '', 'retweets': '', 'replies': '', 'views': ''}
    
    def close_browser(self):
        """关闭浏览器连接"""
        if self.driver:
            try:
                # 不关闭浏览器，只断开连接
                self.driver = None
                print("✅ 已断开浏览器连接")
            except Exception as e:
                print(f"断开浏览器连接时出错: {str(e)}") 