#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter搜索服务模块 - 重构版本
专门用于在现有浏览器会话中搜索用户并获取推文
整合所有分离的功能模块
"""

import time
from datetime import datetime
from services.base_service import BaseService
from services.navigation_service import NavigationService
from services.user_info_extractor import UserInfoExtractor
from services.tweet_extractor import TweetExtractor


class TwitterSearchService(BaseService):
    """
    Twitter搜索服务类 - 重构版本
    整合导航、用户信息提取、推文提取等功能
    """
    
    def __init__(self, debug_port=9222, debug_retweet_detection=False):
        """
        初始化Twitter搜索服务
        
        Args:
            debug_port (int): Chrome调试端口
            debug_retweet_detection (bool): 是否启用转发检测调试模式
        """
        super().__init__(debug_port)
        
        # 初始化各个功能模块
        self.navigation = NavigationService(debug_port)
        self.user_extractor = UserInfoExtractor(debug_port)
        self.tweet_extractor = TweetExtractor(debug_port, debug_retweet_detection)
    
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
            
            # 共享浏览器驱动到所有模块
            self._share_driver_to_modules()
            
            # 直接访问用户页面
            if not self.navigation.direct_access_user_page(username):
                print(f"❌ 无法访问用户 @{username} 的页面")
                return None
            
            # 等待用户页面加载
            time.sleep(3)  # 进一步优化页面加载等待时间到3秒
            
            # 验证是否导航到正确的用户页面
            if not self.navigation.verify_user_page(username):
                print(f"❌ 未能导航到用户 @{username} 的正确页面")
                return None
            
            # 获取用户信息
            user_info = self.user_extractor.extract_user_info(username)
            
            # 如果用户信息获取失败，尝试重新获取
            if user_info['display_name'] == '未知':
                print("重新尝试获取用户信息...")
                time.sleep(2)  # 进一步优化重试等待时间到2秒
                user_info = self.user_extractor.extract_user_info(username)
            
            # 检查是否获取到了粉丝信息
            followers_count = user_info.get('followers_count', 0)
            if followers_count == 0:
                print(f"⚠️ 用户 @{username} 未获取到粉丝信息，停止处理该用户")
                return {'error': 'no_followers_info', 'username': username}
            
            # 获取推文
            tweets = self.tweet_extractor.get_user_tweets(max_tweets)
            
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
    
    def _share_driver_to_modules(self):
        """将浏览器驱动共享给所有模块"""
        self.navigation.driver = self.driver
        self.user_extractor.driver = self.driver
        self.tweet_extractor.driver = self.driver
    
    def close_connection(self):
        """关闭所有连接"""
        super().close_connection()
        
        # 清理所有模块的驱动引用
        if hasattr(self.navigation, 'driver'):
            self.navigation.driver = None
        if hasattr(self.user_extractor, 'driver'):
            self.user_extractor.driver = None
        if hasattr(self.tweet_extractor, 'driver'):
            self.tweet_extractor.driver = None
