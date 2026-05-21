import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

# 加载数据
df = pd.read_csv('students03.csv')

# 定义特征变量和目标变量
X = df.drop(columns=['抑郁症'])
y = df['抑郁症']

# 将分类变量转换为数值变量
X = pd.get_dummies(X, drop_first=True)

# 数据拆分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建决策树分类器
clf = DecisionTreeClassifier(max_depth=4, random_state=42)

# 训练模型
clf.fit(X_train, y_train)

# 预测测试集
y_pred = clf.predict(X_test)

# 打印评估指标
print("混淆矩阵：")
print(confusion_matrix(y_test, y_pred))
print("\n分类报告：")
print(classification_report(y_test, y_pred))

# 绘制决策树
plt.figure(figsize=(20, 12))
plot_tree(clf, filled=True, feature_names=X.columns, class_names=['No Depression', 'Depression'], max_depth=3)
plt.title('决策树')
plt.show()

# 获取特征重要性
feature_importances = clf.feature_importances_

# 创建特征重要性数据框
feature_importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

# 可视化特征重要性
plt.figure(figsize=(12, 8))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.xlabel('重要性')
plt.ylabel('特征')
plt.title('特征重要性')
plt.show()