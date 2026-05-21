import pandas as pd

# 加载数据
file_path = 'student_depression_dataset.csv'
df = pd.read_csv(file_path)

# 筛选Age小于35岁的人
df_age_less_than_35 = df[df['Age'] < 35]

# 去掉Work Pressure不为0的数据
df_work_pressure_zero = df_age_less_than_35[df_age_less_than_35['Work Pressure'] == 0]

# 去掉Job Satisfaction不为0的数据
df_final = df_work_pressure_zero[df_work_pressure_zero['Job Satisfaction'] == 0]

# 查看最终筛选后的数据
print("最终筛选后的数据：")
print(df_final)

# 将最终筛选后的数据导出到新的CSV文件
output_file_path = 'students01.csv'
df_final.to_csv(output_file_path, index=False)

print(f"筛选后的数据已导出到 {output_file_path}")