from functools import wraps
from flask import session, redirect, url_for
import logging

# 配置日志
logger = logging.getLogger('collector')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            logger.warning("未授权的访问尝试")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function 