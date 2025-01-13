from flask import Blueprint, render_template, redirect, url_for, request, session
from collector_admin.utils.auth import login_required
from models.database import Database
from collector.collector_config import SERVERS, PRODUCT_TYPES, PRODUCT_GROUPS
import logging

# 配置日志
logger = logging.getLogger('collector')

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 配置管理员账号密码
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            logger.info(f"管理员 {username} 登录成功")
            return redirect(url_for('admin.panel'))
        else:
            logger.warning(f"登录失败，用户名: {username}")
            return render_template('admin/login.html', error='用户名或密码错误')
            
    return render_template('admin/login.html')

@admin_bp.route('/panel')
@login_required
def panel():
    """管理面板"""
    db = Database()
    try:
        # 获取任务列表
        tasks = db.fetch_all("""
            SELECT * FROM collector_tasks 
            ORDER BY id ASC
        """)
        
        # 获取采集器状态
        collector_status = db.fetch_one("""
            SELECT * FROM collector_status 
            WHERE id = 1
        """)
        
        return render_template('admin/dashboard.html',
                             tasks=tasks,
                             servers=SERVERS,
                             products=PRODUCT_TYPES,
                             product_groups=PRODUCT_GROUPS,
                             collector_status=collector_status)
    except Exception as e:
        logger.error(f"获取管理面板数据失败: {str(e)}")
        raise
    finally:
        db.close()

@admin_bp.route('/logout')
def logout():
    """登出"""
    session.pop('logged_in', None)
    logger.info("管理员登出")
    return redirect(url_for('admin.login')) 