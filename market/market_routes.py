from flask import Blueprint, render_template, jsonify, current_app, request
from flask_cors import CORS
from models.database import Database
import traceback

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

@market_bp.route('/api/v1/market/quality/<int:server_type>/<int:product_id>')
def get_quality_prices(server_type, product_id):
    """获取商品各品质等级的价格数据"""
    try:
        current_app.logger.info(f"接收请求 - server_type: {server_type}, product_id: {product_id}")
        
        db = Database()
        with db.conn.cursor() as cursor:
            # 构建查询SQL，使用 CONVERT_TZ 函数进行时区转换
            sql = """
            WITH today_data AS (
                SELECT 
                    *,
                    CONVERT_TZ(posted_time, '+00:00', '+08:00') as local_time
                FROM market_{0}_{1}
                WHERE DATE(CONVERT_TZ(posted_time, '+00:00', '+08:00')) = CURDATE()
            )
            SELECT 
                m.quality,
                (
                    SELECT price 
                    FROM today_data t1
                    WHERE t1.quality = m.quality
                    ORDER BY t1.local_time DESC
                    LIMIT 1
                ) as latest_price,
                (
                    SELECT price
                    FROM today_data t2
                    WHERE t2.quality = m.quality
                    ORDER BY price ASC
                    LIMIT 1
                ) as lowest_price,
                (
                    SELECT price
                    FROM today_data t3
                    WHERE t3.quality = m.quality
                    ORDER BY price DESC
                    LIMIT 1
                ) as highest_price,
                AVG(price) as average_price,
                (
                    SELECT local_time
                    FROM today_data t4
                    WHERE t4.quality = m.quality
                    ORDER BY t4.local_time DESC
                    LIMIT 1
                ) as update_time
            FROM 
                today_data m
            GROUP BY 
                m.quality
            ORDER BY 
                m.quality ASC;
            """.format(server_type, product_id)

            current_app.logger.info(f"执行SQL查询")
            cursor.execute(sql)
            results = cursor.fetchall()

            # 添加日志输出
            current_app.logger.info(f"查询结果数量: {len(results)}")
            if len(results) > 0:
                current_app.logger.info(f"第一条记录: {results[0]}")

            # 处理查询结果
            quality_data = []
            for row in results:
                quality_data.append({
                    'quality': row['quality'],
                    'latest_price': float(row['latest_price']) if row['latest_price'] else None,
                    'lowest_price': float(row['lowest_price']) if row['lowest_price'] else None,
                    'highest_price': float(row['highest_price']) if row['highest_price'] else None,
                    'average_price': float(row['average_price']) if row['average_price'] else None,
                    'update_time': row['update_time'].strftime('%Y-%m-%d %H:%M:%S') if row['update_time'] else None
                })

            response = jsonify({
                'code': 0,
                'message': 'success',
                'data': quality_data
            })
            response.headers['Content-Type'] = 'application/json'
            return response

    except Exception as e:
        current_app.logger.error(f"处理请求出错: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        response = jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        })
        response.headers['Content-Type'] = 'application/json'
        return response, 500 

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