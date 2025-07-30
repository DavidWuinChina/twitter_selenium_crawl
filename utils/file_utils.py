#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件工具模块
包含JSON和CSV文件保存功能
"""

import json
import pandas as pd
import os
from datetime import datetime

def ensure_results_dir():
    """
    确保results目录存在
    
    Returns:
        str: results目录的路径
    """
    # 获取当前脚本文件所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录（utils的父目录）
    project_dir = os.path.dirname(script_dir)
    # 在项目根目录下创建results目录
    results_dir = os.path.join(project_dir, 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    return results_dir

def save_to_json(data, filename):
    """
    将数据保存为JSON文件到results目录
    
    Args:
        data (dict): 要保存的数据
        filename (str): 文件名
    """
    try:
        results_dir = ensure_results_dir()
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filepath}")
    except Exception as e:
        print(f"保存文件时发生错误: {str(e)}")

def save_to_csv(data, filename):
    """
    将数据保存为CSV文件到results目录
    
    Args:
        data (dict): 要保存的数据
        filename (str): 文件名
    """
    try:
        results_dir = ensure_results_dir()
        filepath = os.path.join(results_dir, filename)
        
        df = pd.DataFrame([data])
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"数据已保存到 {filepath}")
    except Exception as e:
        print(f"保存文件时发生错误: {str(e)}")

def save_all_users_data(data, filename):
    """
    保存所有用户数据到results目录
    
    Args:
        data (list): 所有用户数据列表
        filename (str): 文件名
    """
    try:
        results_dir = ensure_results_dir()
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"所有用户数据已保存到 {filepath}")
    except Exception as e:
        print(f"保存文件时发生错误: {str(e)}") 