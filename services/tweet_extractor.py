#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推文提取模块 - 修复版
专门处理Twitter推文数据的提取和去重，基于实际DOM结构观察
"""

import time
import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from services.base_service import BaseService
from services.data_processor import DataProcessor


class TweetExtractor(BaseService):
    """推文提取器，负责提取和处理Twitter推文数据"""
    
    def __init__(self, debug_port=9222, debug_retweet_detection=False):
        """初始化推文提取器"""
        super().__init__(debug_port)
        self.data_processor = DataProcessor()
        self.debug_retweet_detection = debug_retweet_detection
    
    def get_user_tweets(self, max_tweets=50):
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
            print(f"开始获取用户推文，目标数量: {max_tweets}")
            
            # 多次滚动获取推文
            scroll_attempts = 0
            max_scroll_attempts = 50  # 增加最大滚动次数
            no_new_tweets_count = 0  # 连续无新推文计数器
            max_no_new_tweets = 50  # 连续50次无新推文才停止
            
            while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
                # 查找推文元素
                tweet_elements = self._find_tweet_elements()
                
                if not tweet_elements:
                    print("未找到推文元素，等待页面加载...")
                    time.sleep(3)  # 优化等待时间到3秒
                    scroll_attempts += 1
                    continue
                
                # 提取新推文
                new_tweets = self._extract_tweets_from_elements_with_dedup(
                    tweet_elements, seen_tweets, max_tweets - len(tweets)
                )
                
                if new_tweets:
                    tweets.extend(new_tweets)
                    print(f"当前已获取 {len(tweets)} 条有效推文（目标: {max_tweets}）")
                    no_new_tweets_count = 0  # 重置计数器
                else:
                    no_new_tweets_count += 1
                    print(f"未发现新推文，继续滚动... (连续{no_new_tweets_count}次)")
                
                # 滚动页面 - 使用600像素逐步滚动
                self.scroll_page(600)  # 每次滚动600像素
                time.sleep(2)  # 调整滚动后等待时间到2秒
                scroll_attempts += 1
                
                # 如果连续多次没有新推文，停止
                if no_new_tweets_count >= max_no_new_tweets:
                    print(f"连续{max_no_new_tweets}次未获取到新推文，停止滚动")
                    break
            
            print(f"推文获取完成，总计: {len(tweets)} 条")
            return tweets
            
        except Exception as e:
            print(f"获取用户推文时出错: {str(e)}")
            return tweets

    def _find_tweet_elements(self):
        """查找推文元素"""
        try:
            # 使用最可靠的选择器
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            if not tweet_elements:
                # 备用选择器
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
            return tweet_elements
        except Exception as e:
            print(f"查找推文元素时出错: {str(e)}")
            return []
    
    def _extract_tweets_from_elements_with_dedup(self, tweet_elements, seen_tweets, max_new_tweets):
        """从推文元素中提取数据并去重"""
        new_tweets = []
        filtered_count = 0  # 被过滤的推文数量
        duplicate_count = 0  # 重复推文数量
        
        for tweet_element in tweet_elements:
            if len(new_tweets) >= max_new_tweets:
                break
            
            tweet_data = self._extract_tweet_data(tweet_element)
            if not tweet_data:
                filtered_count += 1  # 因为24小时内或其他原因被过滤
                continue
            
            # 使用推文文本进行去重
            tweet_text = tweet_data.get('text', '')
            if tweet_text and tweet_text not in seen_tweets:
                seen_tweets.add(tweet_text)
                tweet_data['index'] = len(seen_tweets)
                new_tweets.append(tweet_data)
                
                # 显示转发类型
                tweet_type = "🔄转发" if tweet_data.get('is_retweet', False) else "✏️原创"
                print(f"  ✅ 新推文 [{tweet_type}]: {tweet_text[:50]}...")
            else:
                duplicate_count += 1
                if self.debug_retweet_detection:
                    print(f"  🔄 跳过重复: {tweet_text[:50]}...")
        
        if self.debug_retweet_detection and (filtered_count > 0 or duplicate_count > 0):
            print(f"    📊 本轮统计: 新增{len(new_tweets)}条, 过滤{filtered_count}条(24h内), 重复{duplicate_count}条")
        
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
            
            # 获取推文文本
            tweet_text = self._extract_tweet_text(tweet_element)
            if not tweet_text:
                return None
            
            # 获取时间
            date = self._extract_date(tweet_element)
            
            # 过滤24小时内的推文
            if self._is_today_tweet(date):
                if self.debug_retweet_detection:
                    print(f"🚫 跳过24小时内推文: {tweet_text[:50]}... (日期: {date})")
                return None
            elif self.debug_retweet_detection:
                print(f"✅ 保留推文: {tweet_text[:50]}... (日期: {date})")
            
            # 获取互动数据
            interactions = self._extract_interactions(tweet_element)
            
            # 检测是否为转发 - 使用新的方法
            is_retweet = self._detect_retweet(tweet_element, full_text, tweet_text)
            
            return {
                'text': tweet_text,
                'full_text': full_text,
                'date': date,
                'interactions': interactions,
                'length': len(tweet_text),
                'is_retweet': is_retweet
            }
            
        except Exception as e:
            # 不打印错误，静默处理
            return None
    
    def _extract_tweet_text(self, tweet_element):
        """提取推文文本 - 使用多种方法"""
        tweet_text = ""
        
        try:
            # 方法1：查找tweetText元素
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
        if not tweet_text:
            try:
                full_text = tweet_element.text.strip()
                if full_text:
                    lines = full_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if len(line) > 10 and not any(keyword in line.lower() for keyword in ['follow', 'like', 'retweet', 'reply', 'view', 'share', 'more', '·', '@']):
                            tweet_text = line
                            break
            except:
                pass
        
        # 如果推文文本太短，返回None
        if not tweet_text or len(tweet_text) < 5:
            return None
            
        return tweet_text
    
    def _extract_date(self, tweet_element):
        """提取推文日期"""
        try:
            # 使用原来的方法：从完整文本中提取日期
            full_text = tweet_element.text.strip()
            return self.data_processor.extract_tweet_date(full_text)
        except:
            return "未知"
    
    def _is_today_tweet(self, date_str):
        """
        判断推文是否是今天发布的
        
        Args:
            date_str (str): 日期字符串
            
        Returns:
            bool: True表示是今天的推文，False表示不是今天或未知日期
        """
        if not date_str or date_str == "未知" or date_str == "未知日期":
            return False
            
        try:
            today = datetime.now()
            
            # 检查相对时间格式 (如: 1h, 2m, 23h等)
            if re.search(r'\d+[hm]$', date_str):
                return True  # 小时/分钟级别认为是今天
                     
            # 检查"今天"或类似表述
            if any(keyword in date_str.lower() for keyword in ['今天', 'today', '刚刚', 'now']):
                return True
                
            # 检查是否是今天的日期格式
            if '月' in date_str and '日' in date_str:
                # 中文日期格式：如 "12月25日" 或 "2024年12月25日"
                month_match = re.search(r'(\d{1,2})月', date_str)
                day_match = re.search(r'(\d{1,2})日', date_str)
                
                if month_match and day_match:
                    month = int(month_match.group(1))
                    day = int(day_match.group(1))
                    
                    # 如果是今天的月日，认为是今天
                    if month == today.month and day == today.day:
                        return True
                        
            # 检查英文日期格式
            elif re.match(r'[A-Za-z]{3}\s+\d+', date_str):
                # 英文格式：如 "Dec 25"
                try:
                    month_str = re.search(r'([A-Za-z]{3})', date_str).group(1)
                    day = int(re.search(r'(\d+)', date_str).group(1))
                    
                    month_map = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }
                    
                    if month_str in month_map:
                        month = month_map[month_str]
                        if month == today.month and day == today.day:
                            return True
                except:
                    pass
                    
            return False
            
        except:
            return False
    
    def _extract_interactions(self, tweet_element):
        """提取互动数据"""
        try:
            # 使用原来的改进方法提取互动数据
            return self.data_processor.extract_interactions_from_element_improved(tweet_element)
        except:
            return {"likes": "0", "retweets": "0", "replies": "0", "views": "0"}
    
    def _detect_retweet(self, tweet_element, full_text, tweet_text):
        """
        检测推文是否为转发
        基于实际的Twitter DOM结构进行检测
        
        Args:
            tweet_element: 推文元素
            full_text (str): 完整文本
            tweet_text (str): 推文内容
        
        Returns:
            bool: 是否为转发
        """
        try:
            debug_info = []
            
            # 主要检测方法：查找socialContext元素
            # 基于实际观察：转发推文会有socialContext元素包含"reposted"
            social_context_elements = tweet_element.find_elements(By.CSS_SELECTOR, '[data-testid="socialContext"]')
            
            if social_context_elements:
                for element in social_context_elements:
                    element_text = element.text.strip()
                    debug_info.append(f"socialContext: {element_text}")
                    
                    # 检查是否包含"reposted"关键词
                    if 'reposted' in element_text.lower():
                        debug_info.append("✓ 检测到转发 - socialContext包含reposted")
                        if self.debug_retweet_detection:
                            print(f"    🔍 转发检测: {' | '.join(debug_info)}")
                        return True
                    
                    # 检查中文转发标识
                    if '转发了' in element_text or '转发' in element_text:
                        debug_info.append("✓ 检测到转发 - socialContext包含转发")
                        if self.debug_retweet_detection:
                            print(f"    🔍 转发检测: {' | '.join(debug_info)}")
                        return True
            else:
                debug_info.append("无socialContext元素")
            
            # 备用检测：传统的RT格式
            if tweet_text.strip().startswith('RT @'):
                debug_info.append("✓ 检测到转发 - RT格式")
                if self.debug_retweet_detection:
                    print(f"    🔍 转发检测: {' | '.join(debug_info)}")
                return True
            
            # 未检测到转发特征
            debug_info.append("✗ 未检测到转发特征")
            if self.debug_retweet_detection:
                print(f"    🔍 转发检测: {' | '.join(debug_info)}")
            return False
            
        except Exception as e:
            if self.debug_retweet_detection:
                print(f"    ❌ 转发检测出错: {str(e)}")
            return False
    
    def _is_today_tweet(self, date):
        """
        判断推文是否为24小时内的推文
        只保留标准日期格式（如 "Aug 9", "May 15"），其他格式都过滤
        
        Args:
            date (str): 推文日期
            
        Returns:
            bool: 是否为24小时内的推文（需要过滤）
        """
        try:
            # 只保留标准的月份+日期格式，如 "Aug 9", "May 15", "Dec 31" 等
            # 匹配模式：英文月份缩写 + 空格 + 1-2位数字
            standard_date_pattern = r'^[A-Za-z]{3}\s+\d{1,2}$'
            
            if re.match(standard_date_pattern, date.strip()):
                # 如果匹配标准日期格式，不过滤（保留）
                return False
            else:
                # 其他所有格式都过滤掉（24小时内）
                return True
            
        except Exception as e:
            # 如果判断出错，默认过滤（安全起见）
            if self.debug_retweet_detection:
                print(f"    ⚠️ 日期判断出错: {str(e)}")
            return True
