import pandas as pd
import mysql.connector
from mysql.connector import Error

# 创建数据库连接
def create_connection():
    try:
        connection = mysql.connector.connect(
            user='root',
            password='123456',
            host='localhost',
            database='students01'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# 读取CSV文件
df = pd.read_csv('students04.csv')

# 数据处理函数
def process_and_insert_data(connection):
    try:
        cursor = connection.cursor()

        # 1. 获取各个年龄，不同性别的平均学业压力，按升序排列
        df_avg_pressure = df.groupby(['年龄', '性别'])['学业压力'].mean().reset_index()
        df_avg_pressure = df_avg_pressure.sort_values(by='学业压力')
        df_avg_pressure.to_sql('avg_academic_pressure', connection, if_exists='replace', index=False)

        # 2. 获取各个年龄，不同性别的平均学习满意度
        df_avg_satisfaction = df.groupby(['年龄', '性别'])['学习满意度'].mean().reset_index()
        df_avg_satisfaction.to_sql('avg_satisfaction', connection, if_exists='replace', index=False)

        # 3. 学业压力最高为5的前6城市
        df_top_pressure = df[df['学业压力'] == 5].groupby('城市')['学业压力'].mean().nlargest(6).reset_index()
        df_top_pressure.to_sql('top_6_academic_pressure', connection, if_exists='replace', index=False)

        # 4. 学业压力最低的前6个城市
        df_lowest_pressure = df.groupby('城市')['学业压力'].mean().nsmallest(6).reset_index()
        df_lowest_pressure.to_sql('lowest_6_academic_pressure', connection, if_exists='replace', index=False)

        # 5. 睡眠时长最长的前6个城市
        df_top_sleep = df.groupby('城市')['睡眠时长'].mean().nlargest(6).reset_index()
        df_top_sleep.to_sql('top_6_sleep_duration', connection, if_exists='replace', index=False)

        # 6. 睡眠时长小于5小时的前6个城市
        df_least_sleep = df[df['睡眠时长'] == '小于5小时'].groupby('城市').size().nlargest(6).reset_index(name='数量')
        df_least_sleep.to_sql('least_6_sleep_duration', connection, if_exists='replace', index=False)

        # 7. 抑郁症最多的前10个城市
        df_top_depression = df.groupby('城市')['抑郁症'].sum().nlargest(10).reset_index()
        df_top_depression.to_sql('top_10_depression', connection, if_exists='replace', index=False)

        # 8. 不同学位的人数和男女比
        df_degree_ratio = df.groupby('学位')['性别'].count().reset_index(name='总人数')
        df_degree_ratio['男女比'] = df_degree_ratio.apply(lambda row: row['总人数'] / (df[df['学位'] == row['学位']]['性别'].value_counts().get('女', 0) + df[df['学位'] == row['学位']]['性别'].value_counts().get('男', 0)), axis=1)
        df_degree_ratio.to_sql('degree_gender_ratio', connection, if_exists='replace', index=False)

        connection.commit()
        print("Data processed and inserted successfully")

    except Error as e:
        print("Error while processing and inserting data", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# 主函数
def main():
    connection = create_connection()
    if connection:
        process_and_insert_data(connection)

if __name__ == "__main__":
    main()