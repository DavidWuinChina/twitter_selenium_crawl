#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析转发检测结果
帮助识别哪些推文可能被误判
"""

import json
import re

def analyze_tweet_classification(json_file):
    """分析推文分类结果"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔍 转发检测结果分析")
    print("=" * 60)
    
    for user_data in data:
        username = user_data['username']
        tweets = user_data['recent_tweets']
        
        print(f"\n👤 用户: @{username}")
        print(f"📊 总推文: {len(tweets)}")
        
        original_count = 0
        retweet_count = 0
        potential_misclassified = []
        
        for tweet in tweets[:10]:  # 分析前10条推文
            is_retweet = tweet.get('is_retweet', False)
            full_text = tweet.get('full_text', '')
            tweet_text = tweet.get('text', '')
            
            # 简单的误判检测逻辑
            has_reposted = 'reposted' in full_text.lower()
            has_pinned = 'pinned' in full_text.lower()
            
            if is_retweet:
                retweet_count += 1
                # 检查是否可能是误判
                if has_pinned and not has_reposted:
                    potential_misclassified.append({
                        'index': tweet['index'],
                        'reason': '可能是置顶原创推文被误判为转发',
                        'text': tweet_text[:100] + '...' if len(tweet_text) > 100 else tweet_text
                    })
                elif not has_reposted and not re.search(r'RT @\w+', tweet_text):
                    potential_misclassified.append({
                        'index': tweet['index'],
                        'reason': '原创内容被误判为转发',
                        'text': tweet_text[:100] + '...' if len(tweet_text) > 100 else tweet_text
                    })
            else:
                original_count += 1
        
        print(f"✏️ 原创: {original_count}")
        print(f"🔄 转发: {retweet_count}")
        
        if potential_misclassified:
            print(f"\n⚠️ 可能的误判 ({len(potential_misclassified)}条):")
            for item in potential_misclassified:
                print(f"  推文 {item['index']}: {item['reason']}")
                print(f"    内容: {item['text']}")
        
        # 分析一些样本推文的结构
        print(f"\n🔍 推文结构分析 (前3条):")
        for i, tweet in enumerate(tweets[:3], 1):
            full_text = tweet.get('full_text', '')
            lines = full_text.split('\n')
            classification = "🔄转发" if tweet.get('is_retweet', False) else "✏️原创"
            
            print(f"\n  推文 {i} [{classification}]:")
            print(f"    内容: {tweet.get('text', '')[:80]}...")
            print(f"    结构: {len(lines)}行")
            if len(lines) >= 2:
                print(f"    第1行: {lines[0][:50]}...")
                print(f"    第2行: {lines[1][:50]}..." if len(lines) > 1 else "")
        
        print("-" * 60)

if __name__ == "__main__":
    try:
        analyze_tweet_classification('results/twitter_users_data.json')
    except FileNotFoundError:
        print("❌ 找不到 results/twitter_users_data.json 文件")
        print("请先运行爬虫程序生成数据")
    except Exception as e:
        print(f"❌ 分析过程中出错: {str(e)}")



