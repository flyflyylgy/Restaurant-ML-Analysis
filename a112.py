import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
import os
from datetime import datetime

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

# CSV文件路径
CSV_FILE = os.path.normpath(r"D:\Download\delivery_data_with_restaurants.csv")


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
    """
    数据清洗和类型转换
    根据图片中的数据结构处理特殊格式
    """
    # 重命名列以匹配数据库表结构
    df = df.rename(columns={
        'city': 'delivery_city',
        'restaurant': 'restaurant_name',
        'is_canceled': 'is_cancelled'
    })

    # 处理空值
    df = df.fillna({
        'delivery_duration_min': 0,
        'latitude': 0,
        'longitude': 0,
        'customer_rating': 0,
        'cancel_reason': ''
    })

    # 转换日期时间 - 处理图片中的混合格式
    for col in ['order_time', 'delivery_time']:
        if col in df.columns:
            # 尝试多种日期格式
            df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')

    # 处理特殊值
    df['is_cancelled'] = df['is_cancelled'].replace({
        'FALSE': False,
        'FACE': True,
        'F': False,
        'T': True
    }).fillna(False).astype(bool)

    # 清理文本字段
    text_cols = ['delivery_city', 'state', 'restaurant_name', 'cancel_reason']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            if col == 'state':
                df[col] = df[col].str.upper()[:2]  # 确保州代码不超过2个字符

    # 处理customer_rating中的特殊字符
    if 'customer_rating' in df.columns:
        df['customer_rating'] = df['customer_rating'].replace({
            "0'": 0,
            "4.8": 4.8,
            "4.9": 4.9
        }).astype(float)

    # 计算delivery_time_processed（如果未提供）
    if 'delivery_time_processed' not in df.columns:
        df['delivery_time_processed'] = df['delivery_time']

    return df.dropna(subset=['order_id', 'delivery_time'])


def batch_insert_data(connection, data):
    """
    批量插入数据到MySQL
    完全匹配目标表结构
    """
    insert_sql = """
    INSERT INTO orders (
        order_id, delivery_time, delivery_time_processed, delivery_city,
        state, latitude, longitude, restaurant_name, 
        is_cancelled, cancel_reason, customer_rating
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        delivery_time = VALUES(delivery_time),
        delivery_time_processed = VALUES(delivery_time_processed),
        delivery_city = VALUES(delivery_city),
        state = VALUES(state),
        restaurant_name = VALUES(restaurant_name),
        is_cancelled = VALUES(is_cancelled),
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
                    row['delivery_time'].to_pydatetime(),
                    row.get('delivery_time_processed', row['delivery_time']).to_pydatetime(),
                    str(row['delivery_city']),
                    str(row.get('state', 'UN'))[:2],
                    float(row.get('latitude', 0)),
                    float(row.get('longitude', 0)),
                    str(row.get('restaurant_name', 'Unknown'))[:100],  # 限制长度
                    bool(row['is_cancelled']),
                    str(row.get('cancel_reason', ''))[:255],  # 限制长度
                    float(row.get('customer_rating', 0))
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
        # 根据图片中的列名手动指定
        column_names = [
            'order_id', 'order_time', 'delivery_time', 'delivery_duration_min',
            'city', 'state', 'latitude', 'longitude',
            'restaurant', 'is_canceled', 'customer_rating', 'cancel_reason'
        ]

        df = pd.read_csv(
            CSV_FILE,
            names=column_names,
            header=0,  # 如果第一行是列名则设为0
            parse_dates=['order_time', 'delivery_time'],
            encoding='utf-8',
            engine='python',
            on_bad_lines='warn'
        )
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