import pandas as pd

# 加载数据
file_path = 'student_depression_dataset.csv'
df = pd.read_csv(file_path)

# 查看数据的行列数量
print("数据的行列数量：", df.shape)

# 查看数据的前几行
print("数据的前几行：")
print(df.head())

# 查看数据的列名（属性字段）
print("数据的列名：", df.columns)

# 查看是否有空缺值
print("是否有空缺值：")
print(df.isnull().sum())

# 统计每个属性名的类型数量并列出所有唯一值
for column in df.columns:
    print(f"\n{column} 的类型数量：", df[column].nunique())
    print(f"{column} 的所有唯一值：", df[column].unique())


# 筛选Age小于35岁的人
df_age_less_than_35 = df[df['Age'] < 35]

# 去掉Work Pressure不为0的数据
df_work_pressure_zero = df_age_less_than_35[df_age_less_than_35['Work Pressure'] == 0]

# 去掉Job Satisfaction不为0的数据
df_final = df_work_pressure_zero[df_work_pressure_zero['Job Satisfaction'] == 0]

# 查看最终筛选后的数据
print("最终筛选后的数据：")
print(df_final)