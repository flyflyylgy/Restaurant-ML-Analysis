import pandas as pd

# 读取CSV文件
df = pd.read_csv('students.csv')

# 查看城市属性有多少种类型，每个类型有多少个数量，去掉个位数的城市
city_counts = df['城市'].value_counts()
print("城市属性的类型和数量：")
print(city_counts)
# 过滤掉数量小于2的城市
df = df[city_counts[city_counts >= 2].index]

# 查看职业有多少种属性，将职业这一列属性去掉
occupation_types = df['职业'].unique()
print("\n职业属性的种类：")
print(occupation_types)
df = df.drop('职业', axis=1)

# 查看学业压力有多少类别，去掉类型为0的类别
academic_pressure_types = df['学业压力'].unique()
print("\n学业压力的类别：")
print(academic_pressure_types)
df = df[df['学业压力'] != 0]

# 查看累积平均绩点属性，去掉类型为0的类别
gpa_types = df['累积平均绩点'].unique()
print("\n累积平均绩点的类别：")
print(gpa_types)
df = df[df['累积平均绩点'] != 0]

# 对累积平均绩点进行数据清洗
def clean_gpa(gpa):
    if pd.isna(gpa):
        return gpa
    elif gpa < 1 or gpa >= 10:
        return '其他'
    else:
        return f"{int(gpa)}-{int(gpa)+1}"

df['累积平均绩点'] = df['累积平均绩点'].apply(clean_gpa)
print("\n累积平均绩点数据清洗结果：")
print(df['累积平均绩点'].unique())

# 查看学习满意度属性的类别，去掉为0的数据
satisfaction_types = df['学习满意度'].unique()
print("\n学习满意度的类别：")
print(satisfaction_types)
df = df[df['学习满意度'] != 0]

# 查看睡眠时长属性，并进行转换
sleep_duration_map = {
    "'5-6 hours'": "5到6小时",
    "'7-8 hours'": "7到8小时",
    "'Less than 5 hours'": "小于5小时",
    "'More than 8 hours'": "超过8小时",
    "Others": "其他"
}
df['睡眠时长'] = df['睡眠时长'].map(sleep_duration_map)
print("\n睡眠时长属性转换结果：")
print(df['睡眠时长'].unique())

# 导出处理后的数据到CSV文件
df.to_csv('students04.csv', index=False, encoding='utf_8_sig')