import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# 加载CSV文件
file_path = 'students03.csv'
df = pd.read_csv(file_path)

# 创建MySQL连接
db_connection = mysql.connector.connect(
    host='localhost',       # 数据库主机地址
    user='root',   # 数据库用户名
    password='123456',  # 数据库密码
    database='student01'    # 数据库名
)

# 创建SQLAlchemy引擎
engine = create_engine('mysql+mysqlconnector://root:123456@localhost/student01')

# 将数据导入MySQL表
df.to_sql('students', con=engine, if_exists='replace', index=False)

print("数据已成功导入到MySQL数据库中的students表")