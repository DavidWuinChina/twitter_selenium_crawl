#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推文提取模块
专门处理Twitter推文数据的提取和去重
"""

import time
import re
from selenium.webdriver.common.by import By
from services.base_service import BaseService
from services.data_processor import DataProcessor


class TweetExtractor(BaseService):
    """推文提取器，负责提取和处理Twitter推文数据"""
    
    def __init__(self, debug_port=9222):
        """初始化推文提取器"""
        super().__init__(debug_port)
        self.data_processor = DataProcessor()
    
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
                self.scroll_page(600)
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
                        
                        print(f"已提取 {len(tweets)} 条推文")
                
                # 如果已经达到目标数量，停止滚动
                if len(tweets) >= max_tweets:
                    print(f"已达到目标推文数量: {max_tweets}")
                    break
            
            # 为推文添加索引
            for i, tweet in enumerate(tweets):
                tweet['index'] = i
            
            print(f"✅ 成功获取 {len(tweets)} 条推文")
            return tweets
            
        except Exception as e:
            print(f"获取推文时出错: {str(e)}")
            return []
    
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
                    # 创建推文唯一标识 - 使用完整文本内容而不是前50字符
                    tweet_text = tweet_data['text'].strip()
                    
                    if tweet_text not in seen_tweets:
                        # 添加到已见过的集合中
                        seen_tweets.add(tweet_text)
                        # 不在这里设置index，等最终排序后再设置
                        new_tweets.append(tweet_data)
                        print(f"  ✅ 添加新推文: {tweet_text[:50]}...")
                    else:
                        print(f"  🔄 跳过重复推文: {tweet_text[:50]}...")
            
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
                    line = line.strip()
                    if len(line) > 10 and not any(keyword in line.lower() for keyword in ['follow', 'like', 'retweet', 'reply', 'view', 'share', 'more', '·', '@']):
                        tweet_text = line
                        break
            
            # 如果推文文本太短，跳过
            if not tweet_text or len(tweet_text) < 5:
                return None
            
            # 提取日期
            date = self.data_processor.extract_tweet_date(full_text)
            
            # 提取互动数据 - 使用改进的方法
            interactions = self.data_processor.extract_interactions_from_element_improved(tweet_element)
            
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
