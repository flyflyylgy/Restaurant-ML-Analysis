import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

# 加载数据
data = pd.read_csv('students03.csv')

# 数据预处理
# 处理分类变量
categorical_cols = ['性别', '城市', '职业', '睡眠时长', '饮食习惯', '学位', '是否有过自杀念头', '精神疾病家族史', '抑郁症']
data = pd.get_dummies(data, columns=categorical_cols, drop_first=True)

# 检查是否所有列都是数值型
if not np.issubdtype(data.dtypes, np.number).all():
    raise ValueError("数据中仍然包含非数值型列，请检查数据处理步骤。")

# 处理缺失值（如果有）
data = data.dropna()

# 定义因变量和自变量
X = data.drop(columns=['累积平均绩点'])
y = data['累积平均绩点']

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 构建线性回归模型
model = LinearRegression()
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)

# 模型评估
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f'R²: {r2}')
print(f'MSE: {mse}')
print(f'RMSE: {rmse}')