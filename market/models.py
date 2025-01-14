from datetime import datetime, timedelta
from decimal import Decimal
from models.database import Database

class ProductPrice:
    """商品价格模型"""
    
    def __init__(self):
        self.db = Database()
        
    def __del__(self):
        """确保关闭数据库连接"""
        if hasattr(self, 'db'):
            self.db.close()
            
    def get_table_name(self, server_type: int, product_id: int) -> str:
        """获取对应的数据表名"""
        return f"market_{server_type}_{product_id}"
        
    def get_today_price_history(self, server_type: int, product_id: int):
        """获取今日价格历史数据
        
        返回格式：
        [
            {
                "quality": 0,
                "price": 123.456,
                "posted_time": "2024-01-14 10:30:00"
            },
            ...
        ]
        """
        try:
            # 获取今天的开始和结束时间
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            table_name = self.get_table_name(server_type, product_id)
            
            # 查询今日所有有效价格数据
            sql = f"""
                SELECT 
                    quality,
                    price,
                    posted_time
                FROM {table_name}
                WHERE posted_time BETWEEN %s AND %s
                AND is_valid = 1
                ORDER BY quality ASC, posted_time ASC
            """
            
            result = self.db.fetch_all(sql, (today_start, today_end))
            
            # 处理数据，确保价格是浮点数
            return [{
                'quality': row['quality'],
                'price': float(row['price']),
                'posted_time': row['posted_time'].strftime('%Y-%m-%d %H:%M:%S')
            } for row in result]
            
        except Exception as e:
            raise Exception(f"获取今日价格历史数据失败: {str(e)}")
            
    def get_today_prices(self, server_type: int, product_id: int):
        """获取当天价格数据"""
        try:
            # 获取今天的开始和结束时间
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            table_name = self.get_table_name(server_type, product_id)
            
            # 先获取今日所有有效数据,按品质分组统计
            stats_sql = f"""
                WITH today_data AS (
                    SELECT *
                    FROM {table_name}
                    WHERE posted_time BETWEEN %s AND %s
                    AND is_valid = 1
                ),
                latest_records AS (
                    SELECT quality, price as latest_price, posted_time as last_update
                    FROM today_data td1
                    WHERE posted_time = (
                        SELECT MAX(posted_time)
                        FROM today_data td2
                        WHERE td2.quality = td1.quality
                    )
                ),
                price_stats AS (
                    SELECT 
                        quality,
                        MAX(price) as highest,
                        MIN(price) as lowest,
                        ROUND(AVG(price), 3) as average,
                        COUNT(*) as count
                    FROM today_data
                    GROUP BY quality
                )
                SELECT 
                    ps.quality,
                    lr.latest_price,
                    lr.last_update,
                    ps.highest,
                    ps.lowest,
                    ps.average,
                    ps.count
                FROM price_stats ps
                JOIN latest_records lr ON lr.quality = ps.quality
                ORDER BY ps.quality ASC
            """
            
            today_stats = self.db.fetch_all(stats_sql, (today_start, today_end))
            
            if not today_stats:
                return []
            
            # 获取昨天最后一个批次的价格（按品质）
            yesterday_start = today_start - timedelta(days=1)
            yesterday_sql = f"""
                WITH yesterday_data AS (
                    SELECT quality, price, posted_time
                    FROM {table_name}
                    WHERE posted_time BETWEEN %s AND %s
                    AND is_valid = 1
                )
                SELECT quality, price
                FROM yesterday_data yd1
                WHERE posted_time = (
                    SELECT MAX(posted_time)
                    FROM yesterday_data yd2
                    WHERE yd2.quality = yd1.quality
                )
            """
            yesterday_prices = {
                row['quality']: row['price'] 
                for row in self.db.fetch_all(yesterday_sql, (yesterday_start, today_start))
            }
            
            # 处理每个品质的数据
            response_data = []
            for stat in today_stats:
                quality = stat['quality']
                yesterday_price = yesterday_prices.get(quality)
                
                # 计算日涨跌
                daily_trend = None
                if yesterday_price:
                    daily_trend = float(stat['latest_price']) - float(yesterday_price)
                
                quality_data = {
                    'quality': quality,
                    'latest_price': float(stat['latest_price']),
                    'highest': float(stat['highest']),
                    'lowest': float(stat['lowest']),
                    'average': float(stat['average']),
                    'daily_trend': round(daily_trend, 3) if daily_trend is not None else None,
                    'last_update': stat['last_update'].strftime('%Y-%m-%d %H:%M:%S'),
                    'count': stat['count']
                }
                response_data.append(quality_data)
            
            return response_data
            
        except Exception as e:
            raise Exception(f"获取价格数据失败: {str(e)}")
            
    def get_price_history(self, server_type: int, product_id: int, days: int = 7):
        """获取历史价格数据"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            table_name = self.get_table_name(server_type, product_id)
            
            sql = f"""
                SELECT 
                    DATE(posted_time) as date,
                    MAX(price) as highest,
                    MIN(price) as lowest,
                    AVG(price) as average,
                    COUNT(*) as count
                FROM {table_name}
                WHERE posted_time >= %s
                AND is_valid = 1
                GROUP BY DATE(posted_time)
                ORDER BY date ASC
            """
            return self.db.fetch_all(sql, (start_date,))
            
        except Exception as e:
            raise Exception(f"获取历史价格数据失败: {str(e)}")
            
    def get_price_history_by_range(self, server_type: int, product_id: int, time_range: str = 'today'):
        """根据时间范围获取价格历史数据
        
        Args:
            server_type: 服务器类型
            product_id: 商品ID
            time_range: 时间范围
                - today: 今日数据
                - week: 最近一周数据
                - all: 所有历史数据
        """
        try:
            now = datetime.now()
            table_name = self.get_table_name(server_type, product_id)
            
            # 根据时间范围确定查询起始时间
            if time_range == 'today':
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == 'week':
                start_time = now - timedelta(days=7)
            else:  # 'all'
                start_time = datetime(2000, 1, 1)  # 使用一个足够早的时间
                
            end_time = now
            
            # 查询指定时间范围内的所有有效价格数据
            sql = f"""
                SELECT 
                    quality,
                    price,
                    posted_time
                FROM {table_name}
                WHERE posted_time BETWEEN %s AND %s
                AND is_valid = 1
                ORDER BY quality ASC, posted_time ASC
            """
            
            result = self.db.fetch_all(sql, (start_time, end_time))
            
            # 处理数据，确保价格是浮点数
            return [{
                'quality': row['quality'],
                'price': float(row['price']),
                'posted_time': row['posted_time'].strftime('%Y-%m-%d %H:%M:%S')
            } for row in result]
            
        except Exception as e:
            raise Exception(f"获取价格历史数据失败: {str(e)}") 