from flask import Blueprint, render_template, jsonify, request
from .models import ProductPrice
from datetime import datetime, timedelta

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

@market_bp.route('/api/prices/today/<int:server_type>/<int:product_id>')
def get_today_prices(server_type, product_id):
    """获取当天价格数据"""
    try:
        price_model = ProductPrice()
        result = price_model.get_today_prices(server_type, product_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_bp.route('/api/prices/history/<int:server_type>/<int:product_id>')
def get_price_history(server_type, product_id):
    """获取历史价格数据
    
    时间范围参数：
    - today: 今日数据
    - week: 最近一周数据
    - all: 所有历史数据
    """
    try:
        time_range = request.args.get('range', 'today')
        price_model = ProductPrice()
        result = price_model.get_price_history_by_range(server_type, product_id, time_range)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 