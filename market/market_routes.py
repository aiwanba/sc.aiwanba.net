from flask import Blueprint, render_template, jsonify
from models.database import Database

# 创建市场蓝图
market_bp = Blueprint('market', __name__, url_prefix='/market')

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
        db = Database()
        with db.conn.cursor() as cursor:
            # 构建查询SQL
            sql = """
            WITH today_data AS (
                SELECT *
                FROM market_{0}_{1}
                WHERE DATE(posted_time) = CURDATE()
            )
            SELECT 
                m.quality,
                (
                    SELECT price 
                    FROM today_data t1
                    WHERE t1.quality = m.quality
                    ORDER BY posted_time DESC 
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
                    SELECT posted_time
                    FROM today_data t4
                    WHERE t4.quality = m.quality
                    ORDER BY posted_time DESC
                    LIMIT 1
                ) as update_time
            FROM 
                today_data m
            GROUP BY 
                m.quality
            ORDER BY 
                m.quality ASC;
            """.format(server_type, product_id)

            cursor.execute(sql)
            results = cursor.fetchall()

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

            return jsonify({
                'code': 0,
                'message': 'success',
                'data': quality_data
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500 