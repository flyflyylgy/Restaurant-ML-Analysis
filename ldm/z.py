import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector import Error

# 创建数据库连接
def create_connection():
    try:
        # 使用 SQLAlchemy 创建连接
        engine = create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
        return engine
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# 数据处理函数
def process_and_insert_data(engine):
    try:
        # 从数据库读取数据
        df = pd.read_sql('SELECT * FROM students_02', engine)

        # 1. 获取各个年龄，不同性别的平均学业压力，按升序排列
        df_avg_pressure = df.groupby(['年龄', '性别'])['学业压力'].mean().reset_index()
        df_avg_pressure.sort_values('学业压力', inplace=True)
        df_avg_pressure.to_sql('avg_academic_pressure', engine, if_exists='replace', index=False)

        # 2. 获取各个年龄，不同性别的平均学习满意度
        df_avg_satisfaction = df.groupby(['年龄', '性别'])['学习满意度'].mean().reset_index()
        df_avg_satisfaction.to_sql('avg_satisfaction', engine, if_exists='replace', index=False)

        # 3. 学业压力最高为5的前6城市
        df_top_pressure = df[df['学业压力'] == 5].groupby('城市').size().reset_index(name='数量').nlargest(6, columns='数量')

        df_top_pressure.to_sql('top_6_academic_pressure', engine, if_exists='replace', index=False)

        # 4. 学业压力最低的前6个城市
        df_lowest_pressure = df.groupby('城市')['学业压力'].mean().nsmallest(6).reset_index()
        df_lowest_pressure.to_sql('lowest_6_academic_pressure', engine, if_exists='replace', index=False)

        # 5. 睡眠时长小于5小时的前6个城市
        df_least_sleep = df[df['睡眠时长'] == '小于5小时'].groupby('城市').size().reset_index(name='数量').nlargest(6, columns='数量')
        df_least_sleep.to_sql('least_6_sleep_duration', engine, if_exists='replace', index=False)

        # 6. 学业压力为5的人数占城市总人数的比例，并取前6个城市
        df_pressure_count = df[df['学业压力'] == 5].groupby('城市').size()
        df_total_count = df.groupby('城市').size()
        df_ratio = df_pressure_count / df_total_count
        top_6_pressure_ratio = df_ratio.nlargest(6).reset_index(name='比例')
        top_6_pressure_ratio.to_sql('top_6_pressure_ratio', engine, if_exists='replace', index=False)

        print("Data processed and inserted successfully")

    except Error as e:
        print("Error while processing and inserting data", e)

# 主函数
def main():
    engine = create_connection()
    if engine:
        process_and_insert_data(engine)

if __name__ == "__main__":
    main()