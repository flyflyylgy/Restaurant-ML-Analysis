import mysql.connector
import pandas as pd
from datetime import datetime

# MySQL连接配置（使用您提供的参数）
config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': '12345'
}


def create_table(cursor):
    """创建order02表"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS order02 (
        order_id VARCHAR(36) PRIMARY KEY,
        order_time DATETIME,
        delivery_time DATETIME,
        delivery_duration_min FLOAT,
        city VARCHAR(50),
        state VARCHAR(2),
        latitude FLOAT,
        longitude FLOAT,
        restaurant VARCHAR(100),
        is_canceled BOOLEAN,
        cancel_reason VARCHAR(100),
        customer_rating FLOAT
    )
    """
    cursor.execute(create_table_query)
    print("表order02创建成功")


def import_data(cursor, file_path):
    """从CSV文件导入数据"""
    # 读取CSV文件（使用您提供的路径）
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件: {file_path}")
        print(f"包含{len(df)}条记录")
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return

    # 准备插入语句
    insert_query = """
    INSERT INTO order02 (
        order_id, order_time, delivery_time, delivery_duration_min, 
        city, state, latitude, longitude, restaurant, 
        is_canceled, cancel_reason, customer_rating
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # 转换数据并插入
    success_count = 0
    for _, row in df.iterrows():
        try:
            # 处理日期时间格式
            order_time = datetime.strptime(row['order_time'], '%Y-%m-%d %H:%M:%S') if pd.notna(
                row['order_time']) else None
            delivery_time = datetime.strptime(row['delivery_time'], '%Y-%m-%d %H:%M:%S') if pd.notna(
                row['delivery_time']) else None

            # 处理布尔值
            is_canceled = bool(row['is_canceled']) if pd.notna(row['is_canceled']) else False

            # 准备数据元组
            data = (
                str(row['order_id']),
                order_time,
                delivery_time,
                float(row['delivery_duration_min']) if pd.notna(row['delivery_duration_min']) else None,
                str(row['city']) if pd.notna(row['city']) else None,
                str(row['state']) if pd.notna(row['state']) else None,
                float(row['latitude']) if pd.notna(row['latitude']) else None,
                float(row['longitude']) if pd.notna(row['longitude']) else None,
                str(row['restaurant']) if pd.notna(row['restaurant']) else None,
                is_canceled,
                str(row['cancel_reason']) if pd.notna(row['cancel_reason']) else None,
                float(row['customer_rating']) if pd.notna(row['customer_rating']) else None
            )

            cursor.execute(insert_query, data)
            success_count += 1
        except Exception as e:
            print(f"插入数据时出错(跳过该行): {e}")
            print(f"问题数据: {row.to_dict()}")

    print(f"成功导入{success_count}/{len(df)}条数据")


def main():
    # 使用您提供的CSV文件路径
    csv_file_path = r"D:\Download\delivery_data_with_restaurants.csv"

    try:
        # 连接MySQL
        print("正在连接MySQL数据库...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("数据库连接成功")

        # 创建表
        print("正在创建表...")
        create_table(cursor)

        # 导入数据
        print("正在导入数据...")
        import_data(cursor, csv_file_path)

        # 提交事务
        conn.commit()
        print("数据导入完成并已提交")

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        if 'conn' in locals():
            conn.rollback()
            print("已回滚未提交的更改")
    except Exception as e:
        print(f"程序错误: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")


if __name__ == "__main__":
    print("=== 开始执行数据导入程序 ===")
    main()
    print("=== 程序执行完毕 ===")