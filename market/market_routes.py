from flask import Blueprint, render_template

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