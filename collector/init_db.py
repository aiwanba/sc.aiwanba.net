import sys
import os
import logging

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from models.database import Database

# 配置日志
logger = logging.getLogger('collector')

def init_database():
    """初始化数据库"""
    db = Database()
    try:
        # 创建采集器状态表
        db.execute("""
            CREATE TABLE IF NOT EXISTS collector_status (
                id INT PRIMARY KEY,
                is_running INT(1) NOT NULL DEFAULT 0 COMMENT '是否运行中',
                current_task_id INT NULL COMMENT '当前任务ID',
                current_server_type INT NULL COMMENT '当前服务器类型',
                current_product_type INT NULL COMMENT '当前商品类型',
                current_plan TEXT NULL COMMENT '当前采集方案',
                plan_index INT NULL DEFAULT 0 COMMENT '方案执行位置',
                request_interval INT NOT NULL DEFAULT 60 COMMENT '请求间隔(秒)',
                last_request_time DATETIME NULL COMMENT '上次请求时间',
                next_request_time DATETIME NULL COMMENT '下次请求时间',
                error_message TEXT NULL COMMENT '错误信息',
                batch_id BIGINT NULL COMMENT '当前采集批次号',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采集器状态表'
        """)
        
        # 创建采集任务表
        db.execute("""
            CREATE TABLE IF NOT EXISTS collector_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                server_type INT NOT NULL COMMENT '服务器类型',
                product_type INT NOT NULL COMMENT '商品类型',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                UNIQUE KEY uk_task (server_type, product_type) COMMENT '服务器和商品类型唯一'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采集任务表'
        """)
        
        # 初始化采集器状态
        db.execute("""
            INSERT IGNORE INTO collector_status (id, is_running, request_interval) VALUES (1, 0, 60)
        """)
        
        return True
        
    except Exception as e:
        logger.error(f"初始化数据库失败: {str(e)}")
        raise
    finally:
        db.close()

def create_market_table(db, server_type, product_type):
    """创建市场数据表"""
    table_name = f"market_{server_type}_{product_type}"
    
    try:
        # 1. 检查表是否已存在
        exists = db.fetch_one("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = %s
        """, (table_name,))
        
        if exists and exists['count'] > 0:
            logger.info(f"表 {table_name} 已存在")
            return True
            
        # 2. 创建表
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
        
        logger.info(f"成功创建表 {table_name}")
        return True
        
    except Exception as e:
        logger.error(f"创建表 {table_name} 失败: {str(e)}")
        return False

if __name__ == '__main__':
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/collector.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    try:
        init_database()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        sys.exit(1) 