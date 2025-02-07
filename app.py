import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, send_from_directory
from collector.collector_routes import collector_bp
from collector_admin.admin_routes import admin_bp
from market.market_routes import market_bp
from collector.init_db import init_database
from collector.collector import DataCollector
from jinja2 import ChoiceLoader, FileSystemLoader

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建日志处理器
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'collector.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)

# 获取环境变量，默认为 development
ENV = os.getenv('FLASK_ENV', 'development')
logging.info(f'Current environment: {ENV}')

# 创建Flask应用（后台管理系统）
app = Flask(__name__)

# 开发环境配置
if ENV == 'development':
    app.config['DEBUG'] = True  # 启用调试模式
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # 模板自动重载
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 静态文件不缓存
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)  # 开发服务器日志级别

# 注册静态文件目录
app.static_folder = 'collector_admin/static'  # 默认静态文件目录

# 注册模板目录
app.template_folder = 'collector_admin/templates'  # 默认模板目录
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('collector_admin/templates'),
    FileSystemLoader('market/templates')
])

# 配置密钥
app.secret_key = 'sc_aiwanba_net_2024'  # 用于session加密

# 确保数据库表存在
try:
    init_database()
    logging.info('数据库初始化完成')
except Exception as e:
    logging.error(f'数据库初始化失败: {str(e)}')

# 初始化采集器
collector = DataCollector.get_instance()

# 注册蓝图
app.register_blueprint(collector_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(market_bp)

# 处理市场静态文件
@app.route('/market/static/<path:filename>')
def market_static(filename):
    return send_from_directory('market/static', filename)

@app.route('/')
def index():
    """首页"""
    return ""

if __name__ == '__main__':
    logging.info('启动 Flask 应用...')
    
    # 根据环境变量决定运行模式
    if ENV == 'development':
        print('Running in development mode')
        app.run(
            host='0.0.0.0', 
            port=5000, 
            use_reloader=True,  # 启用自动重载
            debug=True,  # 启用调试模式
            threaded=True  # 启用多线程
        )
    else:
        print('Running in production mode')
        app.run(host='0.0.0.0', port=5000) 