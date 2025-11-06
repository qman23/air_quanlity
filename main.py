#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空气质量自动化监控程序（增强版）
作者: AI助手
功能: 定时获取空气质量数据并存储到SQLite数据库
增强错误处理和调试功能
修复：添加完整的环境变量配置支持
"""

import requests
import sqlite3
import json
import schedule
import time
import logging
from datetime import datetime
import sys
from typing import Dict, Optional, List
import argparse
from dotenv import load_dotenv
import os
import traceback
from contextlib import contextmanager


class DatabaseError(Exception):
    """数据库相关异常"""
    pass


class DataValidationError(Exception):
    """数据验证异常"""
    pass


class AirQualityMonitorEnhanced:
    """空气质量监控器（增强版）"""
    
    def __init__(self, db_path: str = "air_quality.db", api_key: str = None, city: str = "北京"):
        """
        初始化空气质量监控器
        
        Args:
            db_path: SQLite数据库文件路径
            api_key: 空气质量API密钥
            city: 监控的城市名称
        """
        self.db_path = db_path
        self.api_key = api_key
        self.city = city
        self.setup_logging()

        # 数据库操作统计
        self.db_stats = {
            'total_attempts': 0,
            'successful_inserts': 0,
            'failed_inserts': 0,
            'validation_errors': 0,
            'last_error': None,
            'last_error_time': None
        }

        """如果数据库文件不存在，则创建数据库表"""
        if not os.path.exists(self.db_path):
            self.logger.info(f"数据库文件不存在，将创建: {self.db_path}")
            self.setup_database()
        else:
            self.logger.info(f"数据库文件已存在: {self.db_path}")
            
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('air_quality_enhanced.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """创建数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS air_quality (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        city TEXT NOT NULL,
                        aqi INTEGER,
                        pm25 REAL,
                        pm10 REAL,
                        co REAL,
                        no2 REAL,
                        o3 REAL,
                        so2 REAL,
                        level TEXT,
                        source TEXT DEFAULT 'waqi',
                        raw_data TEXT
                    )
                ''')
                conn.commit()
                self.logger.info("数据库表创建成功")
        except Exception as e:
            self.logger.error(f"数据库设置失败: {e}")
            raise DatabaseError(f"数据库设置失败: {e}")
            
    @contextmanager
    def get_db_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            self.logger.error(f"数据库连接错误: {e}")
            if conn:
                conn.rollback()
            raise DatabaseError(f"数据库连接错误: {e}")
        finally:
            if conn:
                conn.close()
    
    def validate_data(self, data: Dict) -> bool:
        """
        验证数据完整性和类型
        
        Args:
            data: 要验证的数据
            
        Returns:
            验证通过返回True，失败返回False
        """
        try:
            # 检查必填字段
            required_fields = ['city', 'aqi', 'pm25', 'pm10', 'co', 'no2', 'o3', 'so2', 'level', 'raw_data']
            for field in required_fields:
                if field not in data:
                    self.logger.error(f"缺少必填字段: {field}")
                    raise DataValidationError(f"缺少必填字段: {field}")
            
            # 验证数据类型
            if not isinstance(data['city'], str) or not data['city'].strip():
                self.logger.error(f"城市名称无效: {data['city']}")
                raise DataValidationError(f"城市名称无效: {data['city']}")
            
            # 验证数值字段
            numeric_fields = ['aqi', 'pm25', 'pm10', 'co', 'no2', 'o3', 'so2']
            for field in numeric_fields:
                try:
                    value = float(data[field]) if data[field] is not None else 0.0
                    if field == 'aqi' and not isinstance(data[field], int) and not float(data[field]).is_integer():
                        # AQI应该是整数
                        pass  # SQLite会自动转换
                except (ValueError, TypeError) as e:
                    self.logger.error(f"字段 {field} 数值类型错误: {data[field]}, 错误: {e}")
                    raise DataValidationError(f"字段 {field} 数值类型错误: {e}")
            
            # 验证等级字段
            valid_levels = ["优", "良", "轻度污染", "中度污染", "重度污染", "严重污染"]
            if data['level'] not in valid_levels:
                self.logger.error(f"空气质量等级无效: {data['level']}")
                raise DataValidationError(f"空气质量等级无效: {data['level']}")
            
            # 检查字符串长度（避免SQLite TEXT限制问题）
            if len(data['raw_data']) > 1000000:  # 1MB限制
                self.logger.error(f"原始数据过长: {len(data['raw_data'])} 字符")
                raise DataValidationError(f"原始数据过长: {len(data['raw_data'])} 字符")
            
            return True
            
        except DataValidationError:
            raise
        except Exception as e:
            self.logger.error(f"数据验证过程中发生未知错误: {e}")
            raise DataValidationError(f"数据验证过程中发生未知错误: {e}")
            
    def save_to_database(self, data: Dict, retry_count: int = 3) -> bool:
        """
        将空气质量数据保存到数据库（增强版）
        
        Args:
            data: 空气质量数据
            retry_count: 重试次数
            
        Returns:
            保存成功返回True，失败返回False
        """
        self.db_stats['total_attempts'] += 1
        
        for attempt in range(retry_count):
            try:
                # 验证数据
                self.logger.debug(f"开始验证数据，尝试 {attempt + 1}/{retry_count}")
                self.validate_data(data)
                
                # 准备插入数据
                insert_data = (
                    data["city"], 
                    int(data["aqi"]),  # 确保aqi是整数
                    float(data["pm25"]) if data["pm25"] else 0.0,
                    float(data["pm10"]) if data["pm10"] else 0.0,
                    float(data["co"]) if data["co"] else 0.0,
                    float(data["no2"]) if data["no2"] else 0.0,
                    float(data["o3"]) if data["o3"] else 0.0,
                    float(data["so2"]) if data["so2"] else 0.0,
                    data["level"], 
                    data["raw_data"][:990000]  # 确保不超过SQLite限制
                )
                
                # 执行插入
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 插入数据
                    cursor.execute('''
                        INSERT INTO air_quality 
                        (city, aqi, pm25, pm10, co, no2, o3, so2, level, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', insert_data)
                    
                    # 验证插入是否成功
                    rows_affected = cursor.rowcount
                    if rows_affected == 0:
                        raise DatabaseError("插入操作未影响任何行")
                    
                    conn.commit()
                    
                    # 验证数据确实已插入
                    cursor.execute("SELECT COUNT(*) FROM air_quality WHERE city = ? AND aqi = ? AND timestamp > datetime('now', '-5 minutes')", 
                                 (data["city"], int(data["aqi"])))
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        raise DatabaseError("数据插入后验证失败，数据未找到")
                    
                    self.logger.info(f"数据保存成功 - {data['city']}: AQI {data['aqi']} ({data['level']}) [尝试 {attempt + 1}]")
                    self.db_stats['successful_inserts'] += 1
                    return True
                    
            except DataValidationError as e:
                self.db_stats['validation_errors'] += 1
                self.logger.error(f"数据验证失败: {e}")
                return False
                
            except DatabaseError as e:
                self.logger.warning(f"数据库操作失败 [尝试 {attempt + 1}/{retry_count}]: {e}")
                if attempt == retry_count - 1:  # 最后一次尝试
                    self.db_stats['failed_inserts'] += 1
                    self.db_stats['last_error'] = str(e)
                    self.db_stats['last_error_time'] = datetime.now().isoformat()
                    self.logger.error(f"数据库保存最终失败: {e}")
                    return False
                time.sleep(1)  # 等待1秒后重试
                
            except sqlite3.Error as e:
                self.logger.error(f"SQLite错误 [尝试 {attempt + 1}/{retry_count}]: {e}")
                if attempt == retry_count - 1:
                    self.db_stats['failed_inserts'] += 1
                    self.db_stats['last_error'] = f"SQLite错误: {e}"
                    self.db_stats['last_error_time'] = datetime.now().isoformat()
                    return False
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"未知错误 [尝试 {attempt + 1}/{retry_count}]: {e}")
                self.logger.error(f"错误详情: {traceback.format_exc()}")
                if attempt == retry_count - 1:
                    self.db_stats['failed_inserts'] += 1
                    self.db_stats['last_error'] = f"未知错误: {e}"
                    self.db_stats['last_error_time'] = datetime.now().isoformat()
                    return False
                time.sleep(1)
        
        return False
            
    def collect_once(self) -> bool:
        """
        执行一次数据收集（增强版）
        
        Returns:
            收集成功返回True，失败返回False
        """
        self.logger.info(f"开始收集 {self.city} 的空气质量数据...")
        
        try:
            # 获取API数据
            data = self.fetch_data_from_api()
            if not data:
                self.logger.error("数据获取失败")
                return False
            
            # 记录要保存的数据摘要
            self.logger.debug(f"准备保存数据: 城市={data['city']}, AQI={data['aqi']}, 等级={data['level']}")
            
            # 保存到数据库
            success = self.save_to_database(data)
            
            if success:
                self.logger.info(f"数据收集和保存完成 - {data['city']}: AQI {data['aqi']} ({data['level']})")
                return True
            else:
                self.logger.error(f"数据保存失败 - {data['city']}: AQI {data['aqi']} ({data['level']})")
                return False
                
        except Exception as e:
            self.logger.error(f"数据收集过程中发生异常: {e}")
            self.logger.error(f"异常详情: {traceback.format_exc()}")
            return False
            
    def fetch_data_from_api(self, city: str = None) -> Optional[Dict]:
        """
        从WAQI空气质量API获取数据（增强版）
        
        Args:
            city: 城市名称，默认为初始化时设置的城市
            
        Returns:
            包含空气质量数据的字典，失败返回None
        """
        city = city or self.city
        
        # 使用WAQI API: https://api.waqi.info/feed/{city}/?token={api_key}
        try:
            if self.api_key:
                # 构建API URL
                url = f"https://api.waqi.info/feed/{city}/"
                params = {"token": self.api_key}
                headers = {
                    "User-Agent": "AirQualityMonitorEnhanced/1.0"
                }
                
                self.logger.info(f"正在请求WAQI API: {url}")
                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                
                api_response = response.json()
                
                # 检查API返回状态
                if api_response.get("status") != "ok":
                    error_msg = api_response.get("data", "Unknown error")
                    self.logger.error(f"API返回错误: {error_msg}")
                    return None
                
                # 解析API返回的数据
                parsed_data = self.parse_waqi_response(api_response, city)
                return parsed_data
                
            else:
                # 模拟数据（用于测试和演示）
                self.logger.warning("未设置API密钥，使用模拟数据")
                return self.generate_mock_data(city)
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"数据获取异常: {e}")
            return None
            
    def parse_waqi_response(self, api_response: Dict, city: str) -> Optional[Dict]:
        """
        解析WAQI API返回的数据（增强版）
        
        Args:
            api_response: WAQI API返回的原始数据
            city: 城市名称
            
        Returns:
            解析后的数据字典
        """
        try:
            data = api_response.get("data", {})
            
            # 提取主要数据
            aqi = data.get("aqi", 0)
            city_name = data.get("city", {}).get("name", city)
            
            # 提取iaqi数据（各污染物的值）
            iaqi = data.get("iaqi", {})
            
            # 从iaqi中提取各污染物的值
            pm25 = self._extract_iaqi_value(iaqi, "pm25")
            pm10 = self._extract_iaqi_value(iaqi, "pm10")
            co = self._extract_iaqi_value(iaqi, "co")
            no2 = self._extract_iaqi_value(iaqi, "no2")
            o3 = self._extract_iaqi_value(iaqi, "o3")
            so2 = self._extract_iaqi_value(iaqi, "so2")
            
            # 构建解析后的数据
            parsed_data = {
                "city": city_name,
                "aqi": aqi,
                "pm25": pm25,
                "pm10": pm10,
                "co": co,
                "no2": no2,
                "o3": o3,
                "so2": so2,
                "level": self.get_air_quality_level(aqi),
                "raw_data": json.dumps(api_response, ensure_ascii=False, indent=2)
            }
            
            self.logger.info(f"数据解析成功 - {city_name}: AQI {aqi} ({parsed_data['level']})")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"WAQI API数据解析失败: {e}")
            return None
    
    def _extract_iaqi_value(self, iaqi: Dict, pollutant: str) -> float:
        """
        从iaqi字典中提取污染物值（增强版）
        
        Args:
            iaqi: 包含所有污染物值的字典
            pollutant: 污染物名称 (pm25, pm10, co, no2, o3, so2)
            
        Returns:
            污染物值，如果不存在则返回0.0
        """
        try:
            value = iaqi.get(pollutant, {}).get("v", 0.0)
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError) as e:
            self.logger.warning(f"无法提取污染物 {pollutant} 的值，使用默认值: {e}")
            return 0.0
        
    def generate_mock_data(self, city: str) -> Dict:
        """
        生成模拟空气质量数据（增强版）
        
        Args:
            city: 城市名称
            
        Returns:
            模拟的空气质量数据
        """
        import random
        
        aqi = random.randint(50, 200)
        return {
            "city": city,
            "aqi": aqi,
            "pm25": round(random.uniform(10, 150), 2),
            "pm10": round(random.uniform(20, 200), 2),
            "co": round(random.uniform(0.5, 3.0), 2),
            "no2": round(random.uniform(10, 100), 2),
            "o3": round(random.uniform(20, 200), 2),
            "so2": round(random.uniform(5, 50), 2),
            "level": self.get_air_quality_level(aqi),
            "raw_data": json.dumps({"mock": True, "generated_at": datetime.now().isoformat()})
        }
        
    def get_air_quality_level(self, aqi: int) -> str:
        """
        根据AQI值获取空气质量等级
        
        Args:
            aqi: 空气质量指数
            
        Returns:
            空气质量等级字符串
        """
        try:
            aqi_val = int(aqi)
        except (ValueError, TypeError):
            aqi_val = 0
            
        if aqi_val <= 50:
            return "优"
        elif aqi_val <= 100:
            return "良"
        elif aqi_val <= 150:
            return "轻度污染"
        elif aqi_val <= 200:
            return "中度污染"
        elif aqi_val <= 300:
            return "重度污染"
        else:
            return "严重污染"
            
    def get_database_statistics(self) -> Dict:
        """
        获取数据库操作统计信息
        
        Returns:
            包含统计信息的字典
        """
        return self.db_stats.copy()
        
    def print_database_statistics(self):
        """打印数据库操作统计信息"""
        stats = self.get_database_statistics()
        print("\n=== 数据库操作统计 ===")
        print(f"总尝试次数: {stats['total_attempts']}")
        print(f"成功插入: {stats['successful_inserts']}")
        print(f"失败插入: {stats['failed_inserts']}")
        print(f"验证错误: {stats['validation_errors']}")
        print(f"成功率: {stats['successful_inserts']}/{stats['total_attempts']} ({stats['successful_inserts']/max(stats['total_attempts'], 1)*100:.1f}%)")
        if stats['last_error']:
            print(f"最后错误: {stats['last_error']}")
            print(f"错误时间: {stats['last_error_time']}")
        print("========================\n")
            
    def start_monitoring(self, interval_hours: int = 1):
        """
        开始定时监控（增强版）
        
        Args:
            interval_hours: 监控间隔（小时）
        """
        self.logger.info(f"开始定时监控，每 {interval_hours} 小时收集一次数据")
        
        # 设置定时任务
        schedule.every(interval_hours).hours.do(self.collect_once)
        
        # 立即执行一次
        self.collect_once()
        
        # 开始调度循环
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次


def load_config():
    """从环境变量加载配置（增强版）"""
    # 加载.env文件
    load_dotenv()
    
    # 从环境变量获取配置，优先级从高到低：
    # 命令行参数 > 环境变量 > 默认值
    
    # API密钥 - 从环境变量AQ_API_KEY获取
    api_key = os.getenv('AQ_API_KEY')
    
    # 数据库路径 - 从环境变量AQ_DB_PATH获取，默认为air_quality.db
    db_path = os.getenv('AQ_DB_PATH', 'air_quality.db')
    
    # 城市名称 - 从环境变量AQ_CITY获取，默认为北京
    city = os.getenv('AQ_CITY', '北京')
    
    # 监控间隔 - 从环境变量AQ_INTERVAL获取，默认为1小时
    interval = int(os.getenv('AQ_INTERVAL', '1'))
    
    # 日志级别 - 从环境变量AQ_LOG_LEVEL获取，默认为INFO
    log_level = os.getenv('AQ_LOG_LEVEL', 'INFO')
    
    return {
        'api_key': api_key,
        'db_path': db_path,
        'city': city,
        'interval': interval,
        'log_level': log_level
    }


def main():
    """主函数（增强版）"""
    # 首先加载环境变量配置
    config = load_config()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, config['log_level']))
    
    parser = argparse.ArgumentParser(description='空气质量自动化监控程序（增强版）')
    parser.add_argument('--city', default=config['city'], help='监控的城市名称')
    parser.add_argument('--api-key', default=config['api_key'], help='WAQI API密钥')
    parser.add_argument('--db-path', default=config['db_path'], help='数据库文件路径')
    parser.add_argument('--interval', type=int, default=config['interval'], help='监控间隔（小时）')
    parser.add_argument('--mode', choices=['monitor', 'once', 'test'], 
                       default='test', help='运行模式')
    
    args = parser.parse_args()
    
    try:
        # 创建监控器实例
        monitor = AirQualityMonitorEnhanced(
            db_path=args.db_path,
            api_key=args.api_key,
            city=args.city
        )
        
        if args.mode == 'test':
            # 测试模式：运行3次收集操作来验证错误处理
            print("=== 测试模式：验证改进的错误处理机制 ===")
            print(f"使用配置: 城市={args.city}, 数据库={args.db_path}")
            for i in range(3):
                print(f"\n--- 测试轮次 {i+1} ---")
                success = monitor.collect_once()
                print(f"收集结果: {'成功' if success else '失败'}")
                monitor.print_database_statistics()
                time.sleep(2)  # 间隔2秒
                
        elif args.mode == 'monitor':
            # 定时监控模式
            monitor.start_monitoring(args.interval)
            
        elif args.mode == 'once':
            # 单次收集模式
            success = monitor.collect_once()
            print("数据收集" + ("成功" if success else "失败"))
            monitor.print_database_statistics()
                
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常: {e}")
        logging.error(f"程序异常: {e}")


if __name__ == "__main__":
    main()
