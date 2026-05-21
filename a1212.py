import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
from datetime import datetime
import os

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_import.log'
)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'order_management_system'
}

# CSV文件路径（使用原始字符串处理Windows路径）
CSV_FILE = r"D:\Download\delivery_data_with_restaurants.csv"


def create_db_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        logging.info("成功连接到MySQL数据库")
        return connection
    except Error as e:
        logging.error(f"连接数据库时出错: {e}")
        return None


def clean_data(df):
    """数据清洗和类型转换"""
    # 处理空值
    df = df.fillna({
        'delivery_duration_min': 0,
        'latitude': 0,
        'longitude': 0,
        'cancel_reason': '',
        'customer_rating': 0
    })

    # 转换日期时间 - 处理混合格式
    for col in ['order_time', 'delivery_time']:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')

    # 处理特殊布尔值
    df['is_canceled'] = df['is_canceled'].replace({
        'FALSE': False, 'FACE': True, 'F': False, 'T': True
    }).astype(bool)

    # 清理文本字段
    text_cols = ['city', 'state', 'restaurant', 'cancel_reason']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            if col == 'state':
                df[col] = df[col].str.upper().str[:2]  # 确保州代码不超过2个字符

    # 处理customer_rating中的特殊字符
    df['customer_rating'] = pd.to_numeric(df['customer_rating'], errors='coerce').fillna(0)

    return df.dropna(subset=['order_id'])


def batch_insert_data(connection, data):
    """批量插入数据到MySQL"""
    insert_sql = """
    INSERT INTO orders (
        order_id, order_time, delivery_time, delivery_duration_min,
        city, state, latitude, longitude, restaurant, 
        is_canceled, cancel_reason, customer_rating
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        delivery_time = VALUES(delivery_time),
        is_canceled = VALUES(is_canceled),
        customer_rating = VALUES(customer_rating)
    """

    cursor = None
    try:
        cursor = connection.cursor()

        # 准备批量数据
        batch_values = []
        for _, row in data.iterrows():
            try:
                batch_values.append((
                    str(row['order_id']),
                    row['order_time'].to_pydatetime(),
                    row['delivery_time'].to_pydatetime(),
                    float(row['delivery_duration_min']),
                    str(row['city'])[:50],  # 限制长度
                    str(row['state'])[:2],  # 确保不超过2字符
                    float(row['latitude']),
                    float(row['longitude']),
                    str(row['restaurant'])[:100],  # 限制长度
                    bool(row['is_canceled']),
                    str(row['cancel_reason'])[:255],  # 限制长度
                    float(row['customer_rating'])
                ))
            except Exception as e:
                logging.warning(f"处理行 {_} 时出错: {e}")
                continue

        # 执行批量插入
        cursor.executemany(insert_sql, batch_values)
        connection.commit()
        logging.info(f"成功插入 {len(batch_values)} 条记录")
        return True
    except Exception as e:
        logging.error(f"批量插入时出错: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()


def main():
    """主函数"""
    logging.info("开始数据导入流程")

    # 1. 读取CSV文件
    try:
        # 使用新的读取方式避免date_parser警告
        df = pd.read_csv(CSV_FILE, dtype=str)
        logging.info(f"成功读取CSV文件，共 {len(df)} 条记录")
    except Exception as e:
        logging.error(f"读取CSV文件时出错: {e}")
        return

    # 2. 数据清洗
    cleaned_data = clean_data(df)
    if len(cleaned_data) < len(df):
        logging.warning(f"清洗后丢弃 {len(df) - len(cleaned_data)} 条无效记录")

    # 3. 连接数据库
    conn = create_db_connection()
    if not conn:
        return

    # 4. 批量插入数据
    success = batch_insert_data(conn, cleaned_data)

    if success:
        logging.info("数据导入成功")
    else:
        logging.error("数据导入过程中出现错误")

    # 5. 关闭连接
    conn.close()
    logging.info("数据库连接已关闭")


if __name__ == "__main__":
    main()