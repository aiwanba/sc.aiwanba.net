import sys
import os
import time
import json
import requests
from datetime import datetime, timedelta
import signal
import threading
import logging
import logging.handlers
import codecs

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

# 修改导入方式
from collector.collector_config import BASE_API_URL
from models.database import Database

class DataCollector:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        """获取采集器单例"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        """初始化采集器"""
        if DataCollector._instance:
            raise RuntimeError("DataCollector 是单例类，请使用 get_instance() 方法获取实例")
        
        # 先初始化logger
        self.logger = logging.getLogger('collector')
        self.logger.info("正在初始化数据采集器...")
        
        self.db = Database()
        self.session = requests.Session()
        self._stop_event = threading.Event()  # 添加停止事件
        
        # 检查表是否存在
        try:
            table_exists = self.db.fetch_one("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'collector_status'
            """)
            
            if not table_exists or table_exists['count'] == 0:
                self.logger.warning("collector_status表不存在，尝试初始化数据库...")
                from collector.init_db import init_database
                init_database()
                self.logger.info("数据库初始化完成")
        except Exception as e:
            self.logger.error(f"检查数据库表失败: {str(e)}")
            raise
        
        # 从数据库读取状态
        try:
            status = self.db.fetch_one("""
                SELECT is_running, current_plan, plan_index, request_interval,
                       current_task_id, current_server_type, current_product_type,
                       last_request_time, next_request_time, batch_id
                FROM collector_status 
                WHERE id = 1
            """)
            
            self.is_running = bool(status['is_running']) if status else False
            self.current_plan = json.loads(status['current_plan']) if status and status['current_plan'] else []
            self.plan_index = status['plan_index'] if status else 0
            self.request_interval = status['request_interval'] if status else 60
            self.current_task_id = status['current_task_id']
            self.current_server_type = status['current_server_type']
            self.current_product_type = status['current_product_type']
            self.last_request_time = status['last_request_time']
            self.next_request_time = status['next_request_time']
            self.batch_id = status['batch_id']
            
        except Exception as e:
            self.logger.error(f"读取采集器状态失败: {str(e)}")
            self.is_running = False
            self.current_plan = []
            self.plan_index = 0
            self.request_interval = 60
            self.current_task_id = None
            self.current_server_type = None
            self.current_product_type = None
            self.last_request_time = None
            self.next_request_time = None
            self.batch_id = None
            
        self._collector_thread = None
        self.logger.info(f"数据采集器初始化完成，当前状态: {'运行中' if self.is_running else '已停止'}")

        # 如果数据库显示正在运行，则自动启动采集
        if self.is_running and self.current_plan:
            self.logger.info("检测到上次运行状态为运行中，自动启动采集...")
            self.start_collection()

        # 在主线程中设置信号处理器
        if threading.current_thread() is threading.main_thread():
            self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        try:
            signal.signal(signal.SIGTERM, self._handle_shutdown)
            signal.signal(signal.SIGINT, self._handle_shutdown)
            self.logger.info("信号处理器设置成功")
        except ValueError as e:
            self.logger.warning(f"无法设置信号处理器: {str(e)}")
        except Exception as e:
            self.logger.error(f"设置信号处理器失败: {str(e)}")

    def _handle_shutdown(self, signum, frame):
        """处理关闭信号"""
        self.stop_collection("收到停止信号")

    def start_collection(self):
        """启动采集进程"""
        self.logger.info("尝试启动采集进程...")
        
        if self._collector_thread and self._collector_thread.is_alive():
            self.logger.warning("采集进程已经在运行中")
            return

        try:
            # 重置停止事件
            self._stop_event.clear()
            
            # 更新状态
            self.db.execute("""
                UPDATE collector_status 
                SET is_running = 1,
                    error_message = NULL,
                    updated_at = NOW()
                WHERE id = 1
            """)

            self.is_running = True
            # 创建新线程
            self._collector_thread = threading.Thread(target=self._run_collection)
            self._collector_thread.daemon = True
            self._collector_thread.start()
            self.logger.info("数据采集器启动成功")

        except Exception as e:
            self._handle_start_error(e)

    def _run_collection(self):
        """在线程中运行采集器"""
        try:
            self.run()
        except Exception as e:
            self.logger.error(f"采集线程异常退出: {str(e)}", exc_info=True)
        finally:
            self.is_running = False
            self._collector_thread = None
            # 确保数据库状态更新
            try:
                self.db.execute("""
                    UPDATE collector_status 
                    SET is_running = 0,
                        error_message = NULL,
                        updated_at = NOW()
                    WHERE id = 1
                """)
            except Exception as e:
                self.logger.error(f"更新数据库状态失败: {str(e)}")

    def stop_collection(self, reason="手动停止"):
        """停止采集进程"""
        self.logger.info(f"尝试停止采集进程: {reason}")
        try:
            # 1. 设置停止事件和状态
            self._stop_event.set()
            self.is_running = False
            
            # 2. 立即更新数据库状态
            self.db.execute("""
                UPDATE collector_status 
                SET is_running = 0,
                    current_task_id = NULL,
                    current_server_type = NULL,
                    current_product_type = NULL,
                    current_plan = NULL,
                    plan_index = 0,
                    error_message = NULL,
                    next_request_time = NULL,
                    updated_at = NOW()
                WHERE id = 1
            """)

            # 3. 强制结束当前请求
            if self.session:
                self.session.close()
                self.session = requests.Session()

            # 4. 等待线程结束（最多1秒）
            if self._collector_thread and self._collector_thread.is_alive():
                self._collector_thread.join(timeout=1)
                self._collector_thread = None
                
            self.logger.info(f"数据采集器停止成功: {reason}")

        except Exception as e:
            self._handle_stop_error(e)

    def save_market_data(self, server_type, product_type, data):
        """保存市场数据(增量更新)"""
        if not data:
            return 0
            
        table_name = f"market_{server_type}_{product_type}"
        new_count = 0
        update_count = 0
        
        try:
            # 生成新的批次号
            batch_id = int(time.time())
            
            # 更新采集器状态的批次号
            self.db.execute("""
                UPDATE collector_status 
                SET batch_id = %s
                WHERE id = 1
            """, (batch_id,))
            
            # 批量获取现有记录
            market_ids = [item['id'] for item in data]
            existing_records = {}
            if market_ids:
                records = self.db.fetch_all(f"""
                    SELECT market_id, data_version 
                    FROM {table_name} 
                    WHERE market_id IN ({','.join(['%s'] * len(market_ids))})
                """, market_ids)
                existing_records = {r['market_id']: r['data_version'] for r in records}
            
            # 批量处理数据
            updates = []
            inserts = []
            
            for item in data:
                posted_time = datetime.fromisoformat(item['posted'].replace('Z', '+00:00'))
                
                if item['id'] in existing_records:
                    # 更新已存在的记录
                    current_version = existing_records[item['id']]
                    updates.append((
                        item['quantity'],
                        item['quality'],
                        item['price'],
                        item['seller']['certificates'],
                        item['seller']['contest_wins'],
                        item['fees'],
                        posted_time,
                        batch_id,
                        current_version + 1,  # 版本号递增
                        item['id']  # WHERE market_id = ?
                    ))
                else:
                    # 插入新记录
                    inserts.append((
                        item['id'],
                        item['kind'],
                        item['quantity'],
                        item['quality'],
                        item['price'],
                        item['seller']['id'],
                        item['seller']['company'],
                        item['seller']['realmId'],
                        item['seller']['certificates'],
                        item['seller']['contest_wins'],
                        1 if item['seller']['npc'] else 0,
                        item['fees'],
                        posted_time,
                        batch_id,
                        1,  # 初始版本号
                        1,  # 有效数据
                        'api'  # 数据来源
                    ))
            
            # 批量更新
            if updates:
                self.db.executemany(f"""
                    UPDATE {table_name} SET
                        quantity = %s,
                        quality = %s,
                        price = %s,
                        seller_certificates = %s,
                        seller_contest_wins = %s,
                        fees = %s,
                        posted_time = %s,
                        batch_id = %s,
                        data_version = %s,
                        updated_at = NOW()
                    WHERE market_id = %s
                """, updates)
                update_count = len(updates)
                
            # 批量插入
            if inserts:
                self.db.executemany(f"""
                    INSERT INTO {table_name} (
                        market_id, kind, quantity, quality, price,
                        seller_id, seller_name, seller_realm_id,
                        seller_certificates, seller_contest_wins,
                        seller_is_npc, fees, posted_time,
                        batch_id, data_version, is_valid, data_source
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, inserts)
                new_count = len(inserts)
            
            self.logger.info(f"表 {table_name} 新增 {new_count} 条数据，更新 {update_count} 条数据")
            return new_count + update_count
            
        except Exception as e:
            self.logger.error(f"保存市场数据失败: {str(e)}")
            raise

    def run(self):
        """运行采集器"""
        self.logger.info("数据采集器开始运行")
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # 检查停止事件
                if self._stop_event.is_set():
                    break

                # 1. 检查运行状态
                status = self.db.fetch_one("""
                    SELECT * FROM collector_status 
                    WHERE id = 1
                """)
                
                if not status or not status['is_running'] or self._stop_event.is_set():
                    self.logger.info("采集器状态已变更为停止")
                    break

                # 2. 检查是否需要等待
                if status['last_request_time']:
                    elapsed = (datetime.now() - status['last_request_time']).total_seconds()
                    request_interval = status['request_interval']
                    if elapsed < request_interval:
                        wait_time = request_interval - elapsed
                        next_request_time = datetime.now() + timedelta(seconds=wait_time)
                        # 更新下次请求时间
                        self.db.execute("""
                            UPDATE collector_status 
                            SET next_request_time = %s
                            WHERE id = 1
                        """, (next_request_time,))
                        self.logger.debug(f"等待 {wait_time:.1f} 秒后继续")
                        time.sleep(wait_time)

                # 3. 获取当前方案和执行位置
                current_plan = json.loads(status['current_plan']) if status['current_plan'] else []
                plan_index = status['plan_index'] or 0
                
                if not current_plan:
                    self.logger.error("没有可用的采集方案")
                    time.sleep(10)
                    continue

                # 4. 获取当前要执行的任务
                if plan_index >= len(current_plan):
                    plan_index = 0
                    self.logger.info("开始新一轮采集")
                    
                current_task = current_plan[plan_index]
                
                # 获取当前任务ID
                task_id = self.db.fetch_one("""
                    SELECT id FROM collector_tasks 
                    WHERE server_type = %s AND product_type = %s
                """, (current_task['server_type'], current_task['product_type']))
                
                if not task_id:
                    self.logger.error("任务配置已被删除")
                    time.sleep(10)
                    continue

                self.logger.info(f"开始执行任务: 服务器{current_task['server_type']}/商品{current_task['product_type']}")

                # 5. 更新当前任务状态
                self.db.execute("""
                    UPDATE collector_status 
                    SET current_server_type = %s,
                        current_product_type = %s,
                        current_task_id = %s,
                        plan_index = %s,
                        last_request_time = NOW(),
                        error_message = NULL
                    WHERE id = 1
                """, (
                    current_task['server_type'],
                    current_task['product_type'],
                    task_id['id'],
                    (plan_index + 1) % len(current_plan)
                ))

                # 6. 执行采集（添加超时检查）
                url = BASE_API_URL.format(
                    server_type=current_task['server_type'],
                    product_type=current_task['product_type']
                )
                self.logger.info(f"开始采集数据，API地址: {url}")
                try:
                    # 设置较短的超时时间
                    response = self.session.get(url, timeout=(3, 5))  # (连接超时, 读取超时)
                    response.raise_for_status()
                    data = response.json()
                    self.logger.info(f"采集成功: {url}, 获取到 {len(data)} 条数据")
                except requests.Timeout:
                    self.logger.error(f"采集超时: {url}")
                    if self._stop_event.is_set():
                        break
                    raise
                except requests.RequestException as e:
                    self.logger.error(f"采集请求失败: {url}, 错误: {str(e)}")
                    if self._stop_event.is_set():
                        break
                    raise

                # 检查是否需要停止
                if self._stop_event.is_set():
                    break

                # 7. 保存数据
                self.save_market_data(
                    current_task['server_type'],
                    current_task['product_type'],
                    data
                )

                self.logger.info(f"采集成功: 服务器{current_task['server_type']}/商品{current_task['product_type']}, {len(data)}条数据")

            except Exception as e:
                if self._stop_event.is_set():
                    break
                error_msg = f"采集失败: {str(e)}"
                self.logger.exception(error_msg)
                self.db.execute("""
                    UPDATE collector_status 
                    SET error_message = %s
                    WHERE id = 1
                """, (error_msg,))
                time.sleep(5)

    def _handle_start_error(self, e):
        """处理启动错误"""
        error_msg = f"启动采集进程失败: {str(e)}"
        try:
            self.db.execute("""
                UPDATE collector_status 
                SET error_message = %s,
                    is_running = 0
                WHERE id = 1
            """, (error_msg,))
        except Exception as db_error:
            self.logger.error(f"更新数据库状态失败: {str(db_error)}")
        self.logger.error(error_msg, exc_info=True)
        raise

    def _handle_stop_error(self, e):
        """处理停止错误"""
        error_msg = f"停止采集进程失败: {str(e)}"
        try:
            self.db.execute("""
                UPDATE collector_status 
                SET is_running = 0,
                    error_message = %s,
                    updated_at = NOW()
                WHERE id = 1
            """, (error_msg,))
        except Exception as db_error:
            self.logger.error(f"更新数据库状态失败: {str(db_error)}")
        self.logger.error(error_msg, exc_info=True)
        raise

if __name__ == '__main__':
    collector = DataCollector()
    collector.start_collection()
    collector.run() 