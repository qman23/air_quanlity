#!/usr/bin/env python3
"""
分析WAQI API返回的数据结构
"""

import requests
import json
from datetime import datetime

def analyze_waqi_api():
    """分析WAQI API的返回数据"""
    # 使用测试城市和token（demo token有使用限制）
    city = "beijing"
    token = "demo"  # 演示token，限制较多
    
    url = f"https://api.waqi.info/feed/{city}/"
    params = {"token": token}
    
    try:
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        print("-" * 50)
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        api_response = response.json()
        print("API完整返回数据:")
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
        # 查找time相关的字段
        print("\n" + "=" * 50)
        print("查找time字段:")
        
        def find_time_fields(obj, path=""):
            """递归查找包含time的字段"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if "time" in key.lower():
                        print(f"找到time字段: {current_path} = {value}")
                    if isinstance(value, (dict, list)):
                        find_time_fields(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_time_fields(item, f"{path}[{i}]")
        
        find_time_fields(api_response)
        
        # 特别查找time.s
        print("\n" + "=" * 30)
        print("查找time.s字段:")
        
        def find_time_s_field(obj, path=""):
            """递归查找time.s字段"""
            if isinstance(obj, dict):
                if "time" in obj and isinstance(obj["time"], dict) and "s" in obj["time"]:
                    time_s = obj["time"]["s"]
                    print(f"找到time.s: {path}.time.s = {time_s} (类型: {type(time_s)})")
                    return time_s
                
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    result = find_time_s_field(value, current_path)
                    if result is not None:
                        return result
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = find_time_s_field(item, f"{path}[{i}]")
                    if result is not None:
                        return result
            return None
        
        time_s_value = find_time_s_field(api_response)
        if time_s_value:
            print(f"\n成功找到time.s字段，值为: {time_s_value}")
        else:
            print("\n未找到time.s字段")
            
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_waqi_api()
