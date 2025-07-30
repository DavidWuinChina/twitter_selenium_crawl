#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter个人简介爬虫 - 主入口文件
使用Selenium自动化浏览器爬取Twitter用户信息
"""

import time
import json
import sys
from datetime import datetime
from services.twitter_service import TwitterScraperService
from utils.file_utils import save_to_json, save_to_csv, save_all_users_data

def main():
    """
    主函数 - 批量爬取Twitter用户信息
    """
    print("🚀 启动Twitter爬虫程序...")
    
    # 目标用户列表
    target_usernames = [
        "sunyuchentron",
        "elonmusk", 
        "twitter",
        "github",
        "microsoft"
    ]
    
    print(f"开始批量爬取 {len(target_usernames)} 个用户的信息...")
    print("=" * 60)
    
    # 创建Twitter爬取服务实例
    scraper_service = TwitterScraperService()
    
    successful_users = []
    failed_users = []
    
    try:
        for index, username in enumerate(target_usernames, 1):
            print(f"\n[{index}/{len(target_usernames)}] 正在爬取用户 @{username}...")
            print("-" * 40)
            
            # 获取用户信息
            user_data = scraper_service.get_user_profile(username)
            
            if user_data:
                successful_users.append(user_data)
                
                # 输出用户信息
                print(f"用户名: @{user_data['username']}")
                print(f"显示名称: {user_data['display_name']}")
                print(f"个人简介: {user_data['description']}")
                print(f"位置: {user_data['location']}")
                print(f"爬取时间: {user_data['scraped_at']}")
                print(f"页面URL: {user_data['url']}")
                print(f"页面标题: {user_data['page_title']}")
                
                # 显示最近推文
                if user_data['recent_tweets']:
                    print(f"\n最近 {len(user_data['recent_tweets'])} 条推文:")
                    for i, tweet in enumerate(user_data['recent_tweets'], 1):
                        print(f"\n推文 {i}:")
                        print(f"内容: {tweet['text']}")
                else:
                    print("\n未获取到推文内容")
                    
            else:
                failed_users.append(username)
                print(f"❌ 爬取用户 @{username} 失败")
            
            # 添加延迟，避免请求过于频繁
            if index < len(target_usernames):
                print(f"\n等待3秒后继续下一个用户... ({index}/{len(target_usernames)})")
                time.sleep(3)
        
        # 总结报告
        print(f"\n{'='*60}")
        print("✅ 批量爬取完成！")
        print(f"成功爬取: {len(successful_users)} 个用户")
        print(f"失败爬取: {len(failed_users)} 个用户")
        
        if successful_users:
            print(f"\n✅ 成功的用户:")
            for user in successful_users:
                print(f"- @{user['username']}: {user['display_name']}")
        
        if failed_users:
            print(f"\n❌ 失败的用户:")
            for user in failed_users:
                print(f"- @{user}")
        
        # 保存所有成功用户的数据
        if successful_users:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            all_users_filename = f"all_users_data_{timestamp}.json"
            
            save_all_users_data(successful_users, all_users_filename)
        
        print(f"\n🎉 程序执行完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行过程中发生错误: {str(e)}")
        sys.exit(1)
    finally:
        print("🔚 程序即将退出...")

def single_user_scrape(username):
    """
    爬取单个用户信息
    
    Args:
        username (str): Twitter用户名
    """
    print(f"🚀 开始爬取用户 @{username} 的信息...")
    print("=" * 50)
    
    try:
        # 创建Twitter爬取服务实例
        scraper_service = TwitterScraperService()
        
        # 获取用户信息
        user_data = scraper_service.get_user_profile(username)
        
        if user_data:
            print("\n获取到的用户信息:")
            print(f"用户名: @{user_data['username']}")
            print(f"显示名称: {user_data['display_name']}")
            print(f"个人简介: {user_data['description']}")
            print(f"位置: {user_data['location']}")
            print(f"粉丝数: {user_data['followers_count']}")
            print(f"关注数: {user_data['following_count']}")
            print(f"推文数: {user_data['tweets_count']}")
            print(f"认证状态: {'是' if user_data['verified'] else '否'}")
            print(f"爬取时间: {user_data['scraped_at']}")
            print(f"页面URL: {user_data['url']}")
            
            # 保存数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"twitter_profile_selenium_{username}_{timestamp}.json"
            csv_filename = f"twitter_profile_selenium_{username}_{timestamp}.csv"
            
            save_to_json(user_data, json_filename)
            save_to_csv(user_data, csv_filename)
            
            print("\n" + "=" * 50)
            print("✅ 爬取完成！")
            
            # 特别显示个人简介
            print(f"\n🎯 @{username} 的个人简介:")
            print(f"「{user_data['description']}」")
            
        else:
            print("❌ 爬取失败，请检查用户名是否正确或网络连接是否正常。")
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行过程中发生错误: {str(e)}")
        sys.exit(1)
    finally:
        print("🔚 程序即将退出...")

if __name__ == "__main__":
    # 可以选择批量爬取或单个用户爬取
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，爬取指定用户
        username = sys.argv[1]
        single_user_scrape(username)
    else:
        # 否则进行批量爬取
        main() 