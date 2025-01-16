from flask import Blueprint, render_template, jsonify, current_app, request
from flask_cors import CORS
from models.database import Database
import traceback
from datetime import datetime, timedelta

# 创建市场蓝图
market_bp = Blueprint('market', __name__, url_prefix='/market')
# 启用CORS
CORS(market_bp)  # 简化CORS配置，允许所有来源

@market_bp.route('/')
def index():
    """市场首页"""
    return render_template('market/index.html')

@market_bp.route('/<int:server_type>/<int:product_id>')
def product_detail(server_type, product_id):
    """商品详情页"""
    return render_template('market/index.html')

@market_bp.route('/api/v1/market/quality/<int:server_type>/<int:product_type>')
def get_quality_data(server_type, product_type):
    """获取商品品质数据"""
    try:
        db = Database()
        table_name = f"market_{server_type}_{product_type}"
        
        # 获取最近24小时的数据
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=24)
        
        sql = f"""
            SELECT 
                quality,
                MAX(price) as highest_price,
                MIN(price) as lowest_price,
                AVG(price) as average_price,
                MAX(CASE 
                    WHEN posted_time = (
                        SELECT MAX(posted_time) 
                        FROM {table_name} t2 
                        WHERE t2.quality = t1.quality
                    ) 
                    THEN price 
                    ELSE NULL 
                END) as latest_price,
                MAX(posted_time) as update_time
            FROM {table_name} t1
            WHERE posted_time >= %s
            GROUP BY quality
            ORDER BY quality
        """
        
        result = db.fetch_all(sql, (start_time,))
        
        # 格式化数据
        quality_data = []
        for row in result:
            quality_data.append({
                'quality': row['quality'],
                'latestPrice': float(row['latest_price']) if row['latest_price'] else None,
                'lowestPrice': float(row['lowest_price']) if row['lowest_price'] else None,
                'highestPrice': float(row['highest_price']) if row['highest_price'] else None,
                'averagePrice': float(row['average_price']) if row['average_price'] else None,
                'updateTime': row['update_time'].strftime('%Y-%m-%d %H:%M:%S') if row['update_time'] else None
            })
            
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': quality_data
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'Error: {str(e)}',
            'data': None
        }), 500
    finally:
        if 'db' in locals():
            db.close()

@market_bp.route('/api/v1/market/history/<int:server_type>/<int:product_id>/<int:quality>')
def get_history_data(server_type, product_id, quality):
    """获取指定品质等级的历史价格和成交量数据"""
    try:
        current_app.logger.info(f"接收历史数据请求 - server_type: {server_type}, product_id: {product_id}, quality: {quality}")
        
        period = request.args.get('period', '1d')  # 默认1天
        
        # 根据时间周期确定查询范围
        if period == '1h':
            time_range = "INTERVAL 1 HOUR"
        elif period == '1d':
            time_range = "INTERVAL 24 HOUR"
        else:  # 1m
            time_range = "INTERVAL 30 DAY"
            
        db = Database()
        with db.conn.cursor() as cursor:
            # 构建查询SQL，使用 CONVERT_TZ 函数进行时区转换
            sql = """
            SELECT 
                UNIX_TIMESTAMP(CONVERT_TZ(posted_time, '+00:00', '+08:00')) * 1000 as time,
                price,
                quantity
            FROM market_{0}_{1}
            WHERE quality = %s
            AND CONVERT_TZ(posted_time, '+00:00', '+08:00') >= DATE_SUB(NOW(), {2})
            ORDER BY posted_time
            """.format(server_type, product_id, time_range)

            current_app.logger.info(f"执行SQL查询: {sql}")
            cursor.execute(sql, (quality,))
            results = cursor.fetchall()

            # 添加日志输出
            current_app.logger.info(f"查询结果数量: {len(results)}")
            if len(results) > 0:
                current_app.logger.info(f"第一条记录: {results[0]}")

            # 处理查询结果
            history_data = []
            for row in results:
                history_data.append({
                    'time': row['time'],
                    'price': float(row['price']),
                    'volume': int(row['quantity'])
                })

            response = jsonify({
                'code': 0,
                'message': 'success',
                'data': history_data
            })
            response.headers['Content-Type'] = 'application/json'
            return response

    except Exception as e:
        current_app.logger.error(f"处理历史数据请求出错: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        response = jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        })
        response.headers['Content-Type'] = 'application/json'
        return response, 500 