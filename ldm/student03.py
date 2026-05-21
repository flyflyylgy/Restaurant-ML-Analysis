import pandas as pd

# 加载数据
file_path = 'student_depression_dataset.csv'
df = pd.read_csv(file_path)

# 筛选Age小于35岁的人
df_age_less_than_35 = df[df['Age'] < 35]

# 去掉Work Pressure不为0的数据
df_work_pressure_zero = df_age_less_than_35[df_age_less_than_35['Work Pressure'] == 0]

# 去掉Job Satisfaction不为0的数据
df_job_satisfaction_zero = df_work_pressure_zero[df_work_pressure_zero['Job Satisfaction'] == 0]

# 去掉Profession不为'Student'的数据
df_profession_student = df_job_satisfaction_zero[df_job_satisfaction_zero['Profession'] == 'Student']

# 去掉'Work Pressure'和'Job Satisfaction'这两列
df_cleaned = df_profession_student.drop(columns=['Work Pressure', 'Job Satisfaction'])

# 清理'Financial Stress'列中的非数值部分
df_cleaned = df_cleaned[pd.to_numeric(df_cleaned['Financial Stress'], errors='coerce').notnull()]

# 将字段名从英文改为中文
df_cleaned = df_cleaned.rename(columns={
    'id': '身份证',
    'Gender': '性别',
    'Age': '年龄',
    'City': '城市',
    'Profession': '职业',
    'Academic Pressure': '学业压力',
    'CGPA': '累积平均绩点',
    'Study Satisfaction': '学习满意度',
    'Sleep Duration': '睡眠时长',
    'Dietary Habits': '饮食习惯',
    'Degree': '学位',
    'Have you ever had suicidal thoughts ?': '是否有过自杀念头',
    'Work/Study Hours': '工作/学习时间',
    'Financial Stress': '财务压力',
    'Family History of Mental Illness': '精神疾病家族史',
    'Depression': '抑郁症'
})

# 查看最终筛选后的数据
print("最终筛选后的数据：")
print(df_cleaned)

# 将最终筛选后的数据导出到新的CSV文件
output_file_path = 'students03.csv'
df_cleaned.to_csv(output_file_path, index=False)

print(f"筛选后的数据已导出到 {output_file_path}")