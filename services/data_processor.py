#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理模块
专门处理推文数据的解析和格式化
"""

import re
from selenium.webdriver.common.by import By


class DataProcessor:
    """数据处理器，负责解析和格式化推文数据"""
    
    def extract_tweet_date(self, full_text):
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
    
    def extract_interactions(self, full_text):
        """提取互动数据 - 改进版本"""
        try:
            # 移除日期部分
            date_removed = re.sub(r'·\s*(\d{1,2}月\d{1,2}日)', '', full_text)
            date_removed = re.sub(r'·\s*(\d{4}年\d{1,2}月\d{1,2}日)', '', date_removed)
            date_removed = re.sub(r'·\s*([A-Za-z]{3}\s+\d+)', '', date_removed)
            date_removed = re.sub(r'·\s*([A-Za-z]{3}\s+\d+,\s+\d{4})', '', date_removed)
            
            # 提取数字 - 改进的正则表达式
            numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', date_removed)
            
            # 改进的数字过滤逻辑
            filtered_numbers = []
            for num in numbers:
                # 排除年份（2020-2030）
                if len(num) == 4 and num.startswith('20') and num.isdigit() and int(num) >= 2020:
                    continue
                # 排除明显不合理的大数字小时（>= 24的两位数可能是小时，但我们保留，因为也可能是互动数）
                # 只排除明显超出合理范围的数字，如>99的纯数字小时
                if len(num) <= 2 and num.isdigit() and int(num) > 99:
                    continue
                # 保留其他所有数字，包括小的互动数
                filtered_numbers.append(num)
            
            # 智能分配数字
            if len(filtered_numbers) >= 4:
                # 寻找最可能的浏览数（通常最大且包含K、M等单位）
                view_candidates = []
                for num in filtered_numbers:
                    if 'K' in num or 'M' in num or '万' in num:
                        try:
                            numeric_value = self.convert_to_numeric(num)
                            view_candidates.append((num, numeric_value))
                        except:
                            continue
                
                if view_candidates:
                    # 选择最大的作为浏览数
                    view_candidates.sort(key=lambda x: x[1], reverse=True)
                    views_num = view_candidates[0][0]
                    
                    # 分配其他数字
                    remaining = [n for n in filtered_numbers if n != views_num]
                    return {
                        'likes': remaining[0] if len(remaining) >= 1 else '0',
                        'retweets': remaining[1] if len(remaining) >= 2 else '0',
                        'replies': remaining[2] if len(remaining) >= 3 else '0',
                        'views': views_num
                    }
                else:
                    # 没有明显的浏览数，按顺序分配
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
                    'views': '0'
                }
            elif len(filtered_numbers) >= 2:
                return {
                    'likes': filtered_numbers[0],
                    'retweets': filtered_numbers[1],
                    'replies': '0',
                    'views': '0'
                }
            elif len(filtered_numbers) >= 1:
                return {
                    'likes': filtered_numbers[0],
                    'retweets': '0',
                    'replies': '0',
                    'views': '0'
                }
            else:
                return {'likes': '0', 'retweets': '0', 'replies': '0', 'views': '0'}
        except Exception as e:
            print(f"提取互动数据时出错: {str(e)}")
            return {'likes': '0', 'retweets': '0', 'replies': '0', 'views': '0'}
    
    def extract_interactions_from_element_improved(self, tweet_element):
        """
        改进的互动数据提取方法 - 直接从网页元素获取
        
        Args:
            tweet_element: 推文元素
        
        Returns:
            dict: 互动数据
        """
        interactions = {'likes': '0', 'retweets': '0', 'replies': '0', 'views': '0'}
        
        try:
            # 方法1：尝试从具体的互动按钮中提取
            # 查找点赞按钮
            like_buttons = tweet_element.find_elements(By.CSS_SELECTOR, 
                '[data-testid="like"], [aria-label*="Like"], [aria-label*="点赞"], [data-testid="Unlike"]')
            for button in like_buttons:
                aria_label = button.get_attribute('aria-label') or ''
                button_text = button.text.strip()
                # 从aria-label或按钮文本中提取数字
                numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', aria_label + ' ' + button_text)
                if numbers:
                    interactions['likes'] = numbers[0]
                    break
            
            # 查找转发按钮
            retweet_buttons = tweet_element.find_elements(By.CSS_SELECTOR, 
                '[data-testid="retweet"], [aria-label*="Retweet"], [aria-label*="转发"], [data-testid="unretweet"]')
            for button in retweet_buttons:
                aria_label = button.get_attribute('aria-label') or ''
                button_text = button.text.strip()
                numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', aria_label + ' ' + button_text)
                if numbers:
                    interactions['retweets'] = numbers[0]
                    break
            
            # 查找回复按钮
            reply_buttons = tweet_element.find_elements(By.CSS_SELECTOR, 
                '[data-testid="reply"], [aria-label*="Reply"], [aria-label*="回复"]')
            for button in reply_buttons:
                aria_label = button.get_attribute('aria-label') or ''
                button_text = button.text.strip()
                numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', aria_label + ' ' + button_text)
                if numbers:
                    interactions['replies'] = numbers[0]
                    break
            
            # 查找浏览数按钮
            view_buttons = tweet_element.find_elements(By.CSS_SELECTOR, 
                '[data-testid="analytics"], [aria-label*="View"], [aria-label*="浏览"]')
            for button in view_buttons:
                aria_label = button.get_attribute('aria-label') or ''
                button_text = button.text.strip()
                numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', aria_label + ' ' + button_text)
                if numbers:
                    interactions['views'] = numbers[0]
                    break
            
            # 方法2：如果按钮方法失败，尝试查找通用的可点击元素
            if all(v == '0' for v in interactions.values()):
                interactive_elements = tweet_element.find_elements(By.CSS_SELECTOR, 
                    'span[role="button"], div[role="button"], button, [data-testid*="socialContext"]')
                
                found_numbers = []
                for element in interactive_elements:
                    element_text = element.text.strip()
                    aria_label = element.get_attribute('aria-label') or ''
                    combined_text = element_text + ' ' + aria_label
                    numbers = re.findall(r'(\d+(?:\.\d+)?[KMB万]?)', combined_text)
                    for num in numbers:
                        if num not in found_numbers:
                            found_numbers.append(num)
                
                # 智能分配找到的数字
                if found_numbers:
                    self._assign_numbers_intelligently(found_numbers, interactions)
            
            # 方法3：如果还是没有找到，使用fallback方法从全文提取
            if all(v == '0' for v in interactions.values()):
                full_text = tweet_element.text
                fallback_interactions = self.extract_interactions(full_text)
                interactions.update(fallback_interactions)
                
        except Exception as e:
            print(f"从元素提取互动数据时出错: {str(e)}")
            # fallback到文本提取
            try:
                full_text = tweet_element.text
                interactions = self.extract_interactions(full_text)
            except:
                pass
        
        return interactions
    
    def _assign_numbers_intelligently(self, numbers, interactions):
        """智能分配数字到不同的互动类型"""
        try:
            # 按数值大小排序，识别最可能的views（通常最大）
            number_values = []
            for num in numbers:
                try:
                    value = self.convert_to_numeric(num)
                    number_values.append((num, value))
                except:
                    number_values.append((num, 0))
            
            # 按数值大小排序
            number_values.sort(key=lambda x: x[1], reverse=True)
            
            # 优先分配包含K、M单位的大数字作为views
            views_assigned = False
            for num, value in number_values:
                if ('K' in num or 'M' in num or '万' in num) and not views_assigned:
                    interactions['views'] = num
                    views_assigned = True
                    break
            
            # 分配剩余的数字
            remaining_numbers = [num for num, value in number_values if num != interactions['views']]
            
            if len(remaining_numbers) >= 3:
                interactions['likes'] = remaining_numbers[0]
                interactions['retweets'] = remaining_numbers[1] 
                interactions['replies'] = remaining_numbers[2]
            elif len(remaining_numbers) >= 2:
                interactions['likes'] = remaining_numbers[0]
                interactions['retweets'] = remaining_numbers[1]
            elif len(remaining_numbers) >= 1:
                interactions['likes'] = remaining_numbers[0]
                
        except Exception as e:
            print(f"智能分配数字时出错: {str(e)}")
    
    def convert_to_numeric(self, value_str):
        """将带单位的字符串转换为数值用于比较"""
        if not value_str:
            return 0
        
        value_str = value_str.replace(',', '')
        
        if 'M' in value_str:
            return float(value_str.replace('M', '')) * 1000000
        elif 'K' in value_str:
            return float(value_str.replace('K', '')) * 1000
        elif 'B' in value_str:
            return float(value_str.replace('B', '')) * 1000000000
        elif '万' in value_str:
            return float(value_str.replace('万', '')) * 10000
        else:
            try:
                return float(value_str)
            except:
                return 0
