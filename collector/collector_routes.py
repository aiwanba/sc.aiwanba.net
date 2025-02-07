from flask import Blueprint, render_template, jsonify, request, redirect
from models.database import Database
from collector.collector_config import SERVERS, PRODUCT_TYPES, PRODUCT_GROUPS
from collector_admin.utils.auth import login_required
import json
import logging
import os
from collector.collector import DataCollector
from datetime import datetime, timedelta

# 配置日志
logger = logging.getLogger('collector')

# 修改蓝图前缀为admin
collector_bp = Blueprint('collector', __name__, url_prefix='/admin')

@collector_bp.route('/panel')
@login_required
def task_list():
    """任务列表页面"""
    db = Database()
    try:
        # 获取任务列表（添加更多字段）
        tasks_sql = """
            SELECT 
                ct.*,
                MAX(cs.last_request_time) as last_collection_time,
                COUNT(cs.last_request_time) as total_collections,
                CASE 
                    WHEN cs.error_message IS NULL THEN 1 
                    ELSE 0 
                END as last_collection_success,
                cs.error_message as last_error
            FROM collector_tasks ct
            LEFT JOIN collector_status cs ON ct.id = cs.current_task_id
            GROUP BY ct.id
            ORDER BY ct.id
        """
        tasks = db.fetch_all(tasks_sql)
        
        # 获取各表实际记录数和最新批次的数据量
        table_stats = {}
        for task in tasks:
            table_name = f"market_{task['server_type']}_{task['product_type']}"
            # 先检查表是否存在
            exists = db.fetch_one("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """, (table_name,))
            
            if exists and exists['count'] > 0:
                # 获取总记录数和最新批次的数据量
                stats = db.fetch_one(f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(DISTINCT batch_id) as batch_count,
                        (
                            SELECT COUNT(*) 
                            FROM {table_name} 
                            WHERE batch_id = (
                                SELECT MAX(batch_id) 
                                FROM {table_name}
                            )
                        ) as last_batch_count
                    FROM {table_name}
                """)
                
                table_stats[table_name] = {
                    'total_count': stats['total_count'] if stats else 0,
                    'batch_count': stats['batch_count'] if stats else 0,
                    'last_batch_count': stats['last_batch_count'] if stats else 0
                }
            else:
                table_stats[table_name] = {
                    'total_count': 0,
                    'batch_count': 0,
                    'last_batch_count': 0
                }
        
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
                             collector_status=collector_status,
                             table_stats=table_stats)
    finally:
        db.close()

@collector_bp.route('/collector/status')
@login_required
def get_collector_status():
    """获取采集器状态"""
    db = Database()
    try:
        status = db.fetch_one("""
            SELECT 
                is_running,
                current_task_id,
                request_interval,
                error_message,
                last_request_time,
                next_request_time,
                ct.server_type as task_server_type,
                ct.product_type as task_product_type
            FROM collector_status cs
            LEFT JOIN collector_tasks ct ON cs.current_task_id = ct.id
            WHERE cs.id = 1
        """)
        
        if not status:
            return jsonify({
                'status': 'error',
                'message': '采集器状态记录不存在'
            }), 404
            
        # 直接返回时间字段，不提供默认值
        return jsonify({
            'is_running': bool(status['is_running']),
            'current_task_id': status['current_task_id'],
            'last_request_time': status['last_request_time'].strftime('%Y-%m-%d %H:%M:%S') if status['last_request_time'] else '',
            'next_request_time': status['next_request_time'].strftime('%Y-%m-%d %H:%M:%S') if status['next_request_time'] else '',
            'request_interval': status['request_interval'],
            'error_message': status['error_message']
        })
    except Exception as e:
        logger.error(f"获取采集器状态失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close()

@collector_bp.route('/collector/toggle', methods=['POST'])
@login_required
def toggle_collector():
    """切换采集器状态"""
    data = request.json
    logger.info(f"收到采集器状态切换请求: {data}")
    
    db = Database()
    try:
        # 获取采集器实例
        try:
            collector = DataCollector.get_instance()
            logger.info("成功获取采集器实例")
        except Exception as e:
            logger.error(f"获取采集器实例失败: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': f'获取采集器实例失败: {str(e)}'
            }), 500

        if data['is_running']:
            # 检查采集器当前状态
            status = db.fetch_one("""
                SELECT is_running FROM collector_status 
                WHERE id = 1
            """)
            logger.info(f"当前采集器状态: {status}")
            
            if status and status['is_running']:
                logger.warning("采集器已经在运行中")
                return jsonify({
                    'status': 'error',
                    'message': '采集器已经在运行中'
                }), 400

            # 获取所有任务的配置
            tasks = db.fetch_all("""
                SELECT server_type, product_type 
                FROM collector_tasks 
                ORDER BY server_type, product_type
            """)
            logger.info(f"获取到任务列表: {tasks}")
            
            if not tasks:
                logger.warning("没有可用的采集任务")
                return jsonify({
                    'status': 'error',
                    'message': '没有可用的采集任务，请先创建任务'
                }), 400

            # 生成采集方案
            collection_plan = []
            for task in tasks:
                collection_plan.append({
                    'server_type': task['server_type'],
                    'product_type': task['product_type']
                })
            logger.info(f"生成采集方案: {collection_plan}")

            try:
                # 更新数据库状态
                db.execute("""
                    UPDATE collector_status 
                    SET current_plan = %s,
                        plan_index = 0,
                        error_message = NULL,
                        is_running = 1,
                        updated_at = NOW()
                    WHERE id = 1
                """, (json.dumps(collection_plan),))
                logger.info("数据库状态更新成功")

                # 启动采集器
                collector.start_collection()
                logger.info("采集器启动成功")
                
            except Exception as e:
                error_msg = f"启动采集器失败: {str(e)}"
                logger.error(error_msg, exc_info=True)
                # 回滚状态
                db.execute("""
                    UPDATE collector_status 
                    SET is_running = 0,
                        error_message = %s,
                        updated_at = NOW()
                    WHERE id = 1
                """, (error_msg,))
                return jsonify({
                    'status': 'error',
                    'message': error_msg
                }), 500
            
        else:
            try:
                # 检查当前状态
                status = db.fetch_one("""
                    SELECT is_running FROM collector_status 
                    WHERE id = 1
                """)
                
                if not status or not status['is_running']:
                    logger.warning("采集器已经停止")
                    return jsonify({
                        'status': 'success',
                        'message': '采集器已经停止'
                    })

                # 停止采集器
                collector.stop_collection()
                logger.info("采集器停止成功")
                return jsonify({'status': 'success'})
                
            except Exception as e:
                error_msg = f"停止采集器失败: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': error_msg
                }), 500
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        error_msg = f"采集器操作失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500
    finally:
        db.close()

@collector_bp.route('/task/delete', methods=['POST'])
@login_required
def delete_task():
    """删除任务"""
    data = request.json
    db = Database()
    try:
        # 获取任务信息
        task = db.fetch_one("""
            SELECT server_type, product_type 
            FROM collector_tasks 
            WHERE id = %s
        """, (data['id'],))
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': '任务不存在'
            }), 404

        # 删除任务
        db.execute("""
            DELETE FROM collector_tasks 
            WHERE id = %s
        """, (data['id'],))
        
        return jsonify({'status': 'success'})
    finally:
        db.close()

def create_market_table(db, server_type, product_type):
    """创建市场数据表"""
    table_name = f"market_{server_type}_{product_type}"
    
    try:
        db.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                market_id BIGINT NOT NULL COMMENT '市场订单ID',
                kind TINYINT NOT NULL COMMENT '商品类型标识',
                quantity INT NOT NULL COMMENT '数量',
                quality TINYINT NOT NULL COMMENT '品质',
                price DECIMAL(10,3) NOT NULL COMMENT '价格',
                seller_id BIGINT NOT NULL COMMENT '卖家ID',
                seller_name VARCHAR(100) NOT NULL COMMENT '卖家名称',
                seller_realm_id TINYINT NOT NULL COMMENT '卖家服务器ID',
                seller_certificates INT DEFAULT 0 COMMENT '卖家证书数',
                seller_contest_wins INT DEFAULT 0 COMMENT '卖家比赛获胜次数',
                seller_is_npc TINYINT(1) DEFAULT 0 COMMENT '是否NPC',
                fees INT DEFAULT 0 COMMENT '交易费用',
                posted_time DATETIME NOT NULL COMMENT '发布时间',
                batch_id BIGINT NOT NULL COMMENT '采集批次号',
                data_version INT NOT NULL DEFAULT 1 COMMENT '数据版本号',
                is_valid TINYINT(1) NOT NULL DEFAULT 1 COMMENT '数据是否有效',
                data_source VARCHAR(50) NOT NULL DEFAULT 'api' COMMENT '数据来源',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                KEY idx_seller_id (seller_id),
                KEY idx_posted_time (posted_time),
                KEY idx_batch_id (batch_id),
                UNIQUE KEY uk_market_id (market_id) COMMENT '市场订单ID唯一约束'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 
            COMMENT='市场数据表{server_type}服务器{product_type}商品'
        """)
        return True
    except Exception as e:
        logger.error(f"创建市场数据表失败: {str(e)}")
        return False

@collector_bp.route('/task/create', methods=['POST'])
@login_required
def create_task():
    """创建新任务"""
    data = request.json
    db = Database()
    try:
        # 检查服务器和商品类型组合是否已存在
        existing = db.fetch_one("""
            SELECT id FROM collector_tasks 
            WHERE server_type = %s AND product_type = %s
        """, (data['server_type'], data['product_type']))
        
        if existing:
            return jsonify({
                'status': 'error',
                'message': '该服务器和商品类型的任务已存在'
            }), 400

        # 创建市场数据表
        if not create_market_table(db, data['server_type'], data['product_type']):
            return jsonify({
                'status': 'error',
                'message': '创建市场数据表失败'
            }), 500

        # 创建新任务
        db.execute("""
            INSERT INTO collector_tasks (
                server_type, product_type
            ) VALUES (%s, %s)
        """, (
            data['server_type'],
            data['product_type']
        ))
        
        return jsonify({'status': 'success'})
    finally:
        db.close() 

@collector_bp.route('/task/delete_all', methods=['POST'])
@login_required
def delete_all_tasks():
    """删除所有任务配置"""
    db = Database()
    try:
        # 检查采集器是否正在运行
        status = db.fetch_one("""
            SELECT is_running FROM collector_status 
            WHERE id = 1
        """)
        
        if status and status['is_running']:
            return jsonify({
                'status': 'error',
                'message': '采集器正在运行中，请先停止采集'
            }), 400

        # 删除所有任务
        db.execute("DELETE FROM collector_tasks")
        
        # 清空采集状态
        db.execute("""
            UPDATE collector_status 
            SET current_plan = NULL,
                plan_index = 0,
                current_task_id = NULL,
                current_server_type = NULL,
                current_product_type = NULL,
                error_message = NULL
            WHERE id = 1
        """)
        
        logger.info("所有任务配置已删除")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"删除所有任务失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close() 

@collector_bp.route('/collector/update_interval', methods=['POST'])
@login_required
def update_interval():
    """更新采集间隔时间"""
    data = request.json
    db = Database()
    try:
        # 检查采集器是否正在运行
        status = db.fetch_one("""
            SELECT is_running FROM collector_status 
            WHERE id = 1
        """)
        
        if status and status['is_running']:
            return jsonify({
                'status': 'error',
                'message': '采集器正在运行中，请先停止采集'
            }), 400

        interval = data.get('request_interval')
        if not isinstance(interval, int) or interval < 1 or interval > 3600:
            return jsonify({
                'status': 'error',
                'message': '间隔时间必须在1-3600秒之间'
            }), 400

        # 更新间隔时间
        db.execute("""
            UPDATE collector_status 
            SET request_interval = %s
            WHERE id = 1
        """, (interval,))
        
        logger.info(f"采集间隔时间已更新为 {interval} 秒")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"更新采集间隔时间失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close() 

@collector_bp.route('/task/batch_create', methods=['POST'])
@login_required
def batch_create_tasks():
    """批量创建任务"""
    data = request.json
    if not data or 'tasks' not in data:
        return jsonify({
            'status': 'error',
            'message': '无效的请求数据'
        }), 400
    
    db = Database()
    created_tasks = []
    failed_tasks = []
    
    try:
        # 1. 开始事务
        db.execute("START TRANSACTION")
        
        # 2. 批量检查任务是否存在
        task_checks = [(t['server_type'], t['product_type']) for t in data['tasks']]
        placeholders = ', '.join(['(%s, %s)'] * len(task_checks))
        flat_params = [p for pair in task_checks for p in pair]
        
        existing_tasks = db.fetch_all(f"""
            SELECT server_type, product_type 
            FROM collector_tasks 
            WHERE (server_type, product_type) IN ({placeholders})
        """, flat_params)
        
        existing_set = {(t['server_type'], t['product_type']) for t in existing_tasks}
        
        # 3. 批量创建新任务
        for item in data['tasks']:
            task_key = (item['server_type'], item['product_type'])
            if task_key in existing_set:
                logger.info(f"任务已存在: 服务器{item['server_type']}/商品{item['product_type']}")
                continue
                
            try:
                # 创建市场数据表
                if create_market_table(db, item['server_type'], item['product_type']):
                    # 创建任务记录
                    db.execute("""
                        INSERT INTO collector_tasks (server_type, product_type)
                        VALUES (%s, %s)
                    """, (item['server_type'], item['product_type']))
                    created_tasks.append(item)
                    logger.info(f"成功创建任务: 服务器{item['server_type']}/商品{item['product_type']}")
                else:
                    failed_tasks.append({
                        'server_type': item['server_type'],
                        'product_type': item['product_type'],
                        'reason': '创建市场数据表失败'
                    })
                    logger.error(f"创建市场数据表失败: 服务器{item['server_type']}/商品{item['product_type']}")
            except Exception as e:
                failed_tasks.append({
                    'server_type': item['server_type'],
                    'product_type': item['product_type'],
                    'reason': str(e)
                })
                logger.error(f"创建任务失败: 服务器{item['server_type']}/商品{item['product_type']} - {str(e)}")
        
        # 4. 处理结果
        if failed_tasks:
            db.execute("ROLLBACK")
            return jsonify({
                'status': 'error',
                'message': '部分任务创建失败',
                'failed_tasks': failed_tasks,
                'created_count': 0
            }), 500
            
        # 5. 提交事务
        db.execute("COMMIT")
        return jsonify({
            'status': 'success',
            'message': f'成功创建{len(created_tasks)}个任务',
            'created_tasks': created_tasks,
            'created_count': len(created_tasks)
        })
        
    except Exception as e:
        db.execute("ROLLBACK")
        logger.error(f"批量创建任务失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close()

@collector_bp.route('/collector/tasks', methods=['GET'])
@login_required
def get_tasks():
    """获取任务列表和表统计信息"""
    db = Database()
    try:
        # 获取任务列表（添加更多字段）
        tasks_sql = """
            SELECT 
                ct.*,
                MAX(cs.last_request_time) as last_collection_time,
                COUNT(cs.last_request_time) as total_collections,
                CASE 
                    WHEN cs.error_message IS NULL THEN 1 
                    ELSE 0 
                END as last_collection_success,
                cs.error_message as last_error
            FROM collector_tasks ct
            LEFT JOIN collector_status cs ON ct.id = cs.current_task_id
            GROUP BY ct.id
            ORDER BY ct.id
        """
        tasks = db.fetch_all(tasks_sql)
        
        # 获取各表实际记录数和最新批次的数据量
        table_stats = {}
        for task in tasks:
            table_name = f"market_{task['server_type']}_{task['product_type']}"
            # 先检查表是否存在
            exists = db.fetch_one("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """, (table_name,))
            
            if exists and exists['count'] > 0:
                # 获取总记录数、最新批次的数据量和最后更新时间
                stats = db.fetch_one(f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(DISTINCT batch_id) as batch_count,
                        (
                            SELECT COUNT(*) 
                            FROM {table_name} 
                            WHERE batch_id = (
                                SELECT MAX(batch_id) 
                                FROM {table_name}
                            )
                        ) as last_batch_count,
                        MAX(updated_at) as last_update_time
                    FROM {table_name}
                """)
                
                table_stats[table_name] = {
                    'total_count': stats['total_count'] if stats else 0,
                    'batch_count': stats['batch_count'] if stats else 0,
                    'last_batch_count': stats['last_batch_count'] if stats else 0,
                    'last_update_time': stats['last_update_time'].strftime('%Y-%m-%d %H:%M:%S') if stats and stats['last_update_time'] else '-'
                }
            else:
                table_stats[table_name] = {
                    'total_count': 0,
                    'batch_count': 0,
                    'last_batch_count': 0,
                    'last_update_time': '-'
                }

        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': {
                'tasks': tasks,
                'table_stats': table_stats
            }
        })
    finally:
        db.close() 