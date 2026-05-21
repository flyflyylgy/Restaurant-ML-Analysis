import pandas as pd
import mysql.connector

# 连接MySQL数据库
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    database='12345'
)

# 读取整个表到DataFrame
query = "SELECT * FROM order02"
df = pd.read_sql(query, conn)

# 统计每列的空值数量
null_counts = df.isnull().sum()

# 筛选出有空值的列
columns_with_nulls = null_counts[null_counts > 0]

# 打印结果
print("各列缺失值统计:")
for col, count in columns_with_nulls.items():
    print(f"{col}: {count}个缺失值 ({count/len(df)*100:.2f}%)")

# 关闭连接
conn.close()