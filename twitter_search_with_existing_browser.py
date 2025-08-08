#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter搜索程序 - 使用现有浏览器会话
在已经打开的Chrome浏览器中搜索用户并获取推文
"""

import time
import json
import sys
import os
from datetime import datetime
from services.twitter_search_service import TwitterSearchService
import re # Added for date parsing

def main():
    """
    主函数 - 使用现有浏览器会话搜索Twitter用户
    """
    # 记录开始时间
    start_time = datetime.now()
    print("🚀 启动Twitter搜索程序（使用现有浏览器会话）...")
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 目标用户列表
    target_usernames = [
    "Defiqueen01"
]
    # target_usernames = [
    #     "sunyuchentron",
    #     "Defiqueen01",
    #     "ApeCryptos",
    #     "cryptodragon001",
    #     "Grandellaa",
    #     "CryptoAvenuee",
    #     "CryptoAs_TW",
    #     "specialist_005",
    #     "9ali9__",
    #     "CoinLabVerse"
    # ]
    
    print(f"开始搜索 {len(target_usernames)} 个用户...")
    print("请确保Chrome浏览器已打开并访问了 https://x.com/home")
    print("=" * 60)
    
    # 创建Twitter搜索服务实例
    search_service = TwitterSearchService(debug_port=9222)
    
    # 尝试连接到现有浏览器会话
    if not search_service.connect_to_browser():
        print("❌ 无法连接到现有浏览器会话")
        print("请确保：")
        print("1. Chrome浏览器已打开")
        print("2. 已访问 https://x.com/home")
        print("3. 如果需要，请使用以下命令启动Chrome调试模式：")
        print("   chrome.exe --remote-debugging-port=9222 --user-data-dir=chrome_debug_profile")
        return
    
    successful_users = []
    failed_users = []
    
    try:
        for index, username in enumerate(target_usernames, 1):
            print(f"\n[{index}/{len(target_usernames)}] 正在搜索用户 @{username}...")
            print("-" * 40)
            
            # 搜索用户并获取推文
            result = search_service.search_user_and_get_tweets(username, max_tweets=50)
            
            if result:
                successful_users.append(result)
                
                # 输出用户信息
                user_info = result['user_info']
                print(f"用户名: @{result['username']}")
                print(f"显示名称: {user_info['display_name']}")
                print(f"粉丝数: {user_info.get('followers_count', '0')}")
                print(f"个人简介: {user_info['description']}")
                print(f"位置: {user_info['location']}")
                print(f"认证状态: {'是' if user_info['verified'] else '否'}")
                print(f"获取到推文数量: {result['tweets_count']}")
                
                # 显示推文内容
                if result['tweets']:
                    print(f"\n📝 获取到的推文（前5条）:")
                    for i, tweet in enumerate(result['tweets'][:5], 1):
                        print(f"\n推文 {i} (日期: {tweet.get('date', '未知')}):")
                        print(f"内容: {tweet['text']}")
                        if tweet.get('interactions'):
                            print(f"互动: {tweet['interactions']}")
                        print(f"长度: {tweet['length']} 字符")
                    
                    if len(result['tweets']) > 5:
                        print(f"\n... 还有 {len(result['tweets']) - 5} 条推文")
                else:
                    print("\n未获取到推文内容")
                    
            else:
                failed_users.append(username)
                print(f"❌ 搜索用户 @{username} 失败")
            
            # 添加延迟，避免请求过于频繁
            if index < len(target_usernames):
                print(f"\n等待3秒后继续下一个用户... ({index}/{len(target_usernames)})")
                time.sleep(3)
        
        # 总结报告
        print(f"\n{'='*60}")
        print("✅ 批量搜索完成！")
        print(f"成功搜索: {len(successful_users)} 个用户")
        print(f"失败搜索: {len(failed_users)} 个用户")
        
        if successful_users:
            print(f"\n✅ 成功的用户:")
            for user in successful_users:
                print(f"- @{user['username']}: {user['user_info']['display_name']} (推文: {user['tweets_count']}条)")
        
        if failed_users:
            print(f"\n❌ 失败的用户:")
            for user in failed_users:
                print(f"- @{user}")
        
        # 保存所有成功用户的数据
        if successful_users:
            # 创建结果目录
            results_dir = 'results'
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            # 转换为正确的格式
            formatted_results = []
            for result in successful_users:
                user_info = result['user_info']
                
                # 重新排序推文（按时间顺序，最新的在前，未知日期放在最后）
                tweets = result['tweets']
                
                # 自定义排序函数：已知日期按时间排序，未知日期放在最后
                def sort_key(tweet):
                    date = tweet.get('date', '')
                    if date == '未知日期' or date == '':
                        return '9999-12-31'  # 未知日期放在最后
                    else:
                        # 尝试解析日期，如果解析失败，也放在最后
                        try:
                            # 处理中文日期格式
                            if '月' in date and '日' in date:
                                if '年' in date:
                                    # 2024年1月1日格式
                                    year_match = re.search(r'(\d{4})年', date)
                                    month_match = re.search(r'(\d{1,2})月', date)
                                    day_match = re.search(r'(\d{1,2})日', date)
                                    if year_match and month_match and day_match:
                                        year = int(year_match.group(1))
                                        month = int(month_match.group(1))
                                        day = int(day_match.group(1))
                                        return f"{year:04d}-{month:02d}-{day:02d}"
                                else:
                                    # 1月1日格式，假设是今年
                                    current_year = datetime.now().year
                                    month_match = re.search(r'(\d{1,2})月', date)
                                    day_match = re.search(r'(\d{1,2})日', date)
                                    if month_match and day_match:
                                        month = int(month_match.group(1))
                                        day = int(day_match.group(1))
                                        return f"{current_year:04d}-{month:02d}-{day:02d}"
                            elif re.match(r'[A-Za-z]{3}\s+\d+', date):
                                # Jan 1 格式，假设是今年
                                current_year = datetime.now().year
                                month_match = re.search(r'([A-Za-z]{3})', date)
                                day_match = re.search(r'(\d+)', date)
                                if month_match and day_match:
                                    month_str = month_match.group(1)
                                    day = int(day_match.group(1))
                                    # 月份映射
                                    month_map = {
                                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                                        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                                        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                                    }
                                    if month_str in month_map:
                                        month = month_map[month_str]
                                        return f"{current_year:04d}-{month:02d}-{day:02d}"
                        except:
                            pass
                        return '9999-12-31'  # 解析失败也放在最后
                
                # 按自定义排序函数排序
                tweets.sort(key=sort_key, reverse=False)  # 改为reverse=False，这样未知日期会放在最后
                
                # 重新设置index
                for i, tweet in enumerate(tweets, 1):
                    tweet['index'] = i
                
                formatted_user = {
                    "username": result['username'],
                    "display_name": user_info['display_name'],
                    "followers": user_info.get('followers_count', '0'),
                    "description": user_info['description'],
                    "location": user_info['location'],
                    "verified": user_info['verified'],
                    "scraped_at": result['scraped_at'],
                    "url": f"https://twitter.com/{result['username']}",
                    "page_title": f"{user_info['display_name']} (@{result['username']}) / X",
                    "recent_tweets": tweets
                }
                formatted_results.append(formatted_user)
            
            # 保存为JSON格式
            json_filename = os.path.join(results_dir, "twitter_users_data.json")
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(formatted_results, f, ensure_ascii=False, indent=2)
            
            # 保存为TXT格式
            txt_filename = os.path.join(results_dir, "twitter_users_data.txt")
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(f"Twitter搜索结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for result in formatted_results:
                    f.write(f"用户名: @{result['username']}\n")
                    f.write(f"显示名称: {result['display_name']}\n")
                    f.write(f"粉丝数: {result.get('followers', '0')}\n")
                    f.write(f"个人简介: {result['description']}\n")
                    f.write(f"位置: {result['location']}\n")
                    f.write(f"认证状态: {'是' if result['verified'] else '否'}\n")
                    f.write(f"获取到推文数量: {len(result['recent_tweets'])}\n")
                    
                    if result['recent_tweets']:
                        f.write(f"\n推文内容:\n")
                        for tweet in result['recent_tweets']:
                            f.write(f"\n推文 {tweet['index']} (日期: {tweet.get('date', '未知')}):\n")
                            f.write(f"内容: {tweet['text']}\n")
                            if tweet.get('interactions'):
                                f.write(f"互动: {tweet['interactions']}\n")
                            f.write(f"长度: {tweet['length']} 字符\n")
                    
                    f.write("\n" + "-" * 40 + "\n\n")
            
            print(f"\n📁 结果已保存:")
            print(f"JSON文件: {json_filename}")
            print(f"TXT文件: {txt_filename}")
        
        # 计算运行时长
        end_time = datetime.now()
        duration = end_time - start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"\n🎉 程序执行完成！")
        print(f"⏰ 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 总运行时长: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")
        
    except KeyboardInterrupt:
        # 计算运行时长
        end_time = datetime.now()
        duration = end_time - start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print("\n⚠️ 用户中断程序执行")
        print(f"⏰ 中断时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 运行时长: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")
        sys.exit(0)
    except Exception as e:
        # 计算运行时长
        end_time = datetime.now()
        duration = end_time - start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"\n❌ 程序执行过程中发生错误: {str(e)}")
        print(f"⏰ 错误时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 运行时长: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")
        sys.exit(1)
    finally:
        # 断开浏览器连接（不关闭浏览器）
        search_service.close_browser()
        print("🔚 程序即将退出...")
        # 确保程序完全退出
        sys.exit(0)

if __name__ == "__main__":
    main() 