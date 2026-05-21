from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
# 数据准备（示例）
# 设置中文显示


# 加载数据
df = pd.read_csv('students03.csv')
X = pd.get_dummies(df.drop(columns=['抑郁症']), drop_first=True)
y = df['抑郁症'] # 替换为实际数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# 构建模型
model = RandomForestClassifier(
    n_estimators=100,      # 树的数量
    max_depth=5,           # 最大深度
    max_features='sqrt',   # 每棵树分裂时的特征数
    random_state=42
)
model.fit(X_train, y_train)

# 评估
y_pred = model.predict(X_test)
print("混淆矩阵:\n", confusion_matrix(y_test, y_pred))
print("分类报告:\n", classification_report(y_test, y_pred))