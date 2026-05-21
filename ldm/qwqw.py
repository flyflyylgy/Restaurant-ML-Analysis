# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import confusion_matrix, recall_score, f1_score, roc_auc_score, roc_curve, auc
# import matplotlib.pyplot as plt
#
# # 加载数据
# file_path = 'students03.csv'
# df = pd.read_csv(file_path)
#
# # 特征选择
# features = ['性别', '年龄', '城市', '学业压力', '累积平均绩点', '学习满意度', '睡眠时长', '饮食习惯', '学位', '工作/学习时间', '财务压力', '精神疾病家族史']
# target = '抑郁症'
#
# # 数据编码
# label_encoders = {}
# for feature in features:
#     if df[feature].dtype == 'object':
#         le = LabelEncoder()
#         df[feature] = le.fit_transform(df[feature])
#         label_encoders[feature] = le
#
# # 数据分割
# X = df[features]
# y = df[target]
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # 模型选择
# model = LogisticRegression(max_iter=1000)
#
# # 模型训练
# model.fit(X_train, y_train)
#
# # 模型预测
# y_pred = model.predict(X_test)
# y_pred_proba = model.predict_proba(X_test)[:, 1]
#
# # 模型评估
# conf_matrix = confusion_matrix(y_test, y_pred)
# recall = recall_score(y_test, y_pred)
# f1 = f1_score(y_test, y_pred)
# roc_auc = roc_auc_score(y_test, y_pred_proba)
#
# # 输出评估指标
# print("混淆矩阵：")
# print(conf_matrix)
# print(f"Recall: {recall:.2f}")
# print(f"F1 Score: {f1:.2f}")
# print(f"AUC: {roc_auc:.2f}")
#
# # 绘制ROC曲线
# fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
# roc_auc = auc(fpr, tpr)
#
# plt.figure()
# plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
# plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
# plt.xlim([0.0, 1.0])
# plt.ylim([0.0, 1.05])
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive Rate')
# plt.title('Receiver Operating Characteristic')
# plt.legend(loc="lower right")
# plt.show()

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, recall_score, f1_score, roc_auc_score, roc_curve, auc
import matplotlib
matplotlib.use('Agg')  # 设置非交互式后端
import matplotlib.pyplot as plt

# 加载数据
file_path = 'students03.csv'
df = pd.read_csv(file_path)

# 特征选择
features = ['性别', '年龄', '城市', '学业压力', '累积平均绩点', '学习满意度', '睡眠时长', '饮食习惯', '学位', '工作/学习时间', '财务压力', '精神疾病家族史']
target = '抑郁症'

# 数据编码
label_encoders = {}
for feature in features:
    if df[feature].dtype == 'object':
        le = LabelEncoder()
        df[feature] = le.fit_transform(df[feature])
        label_encoders[feature] = le

# 数据分割
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 模型选择
model = LogisticRegression(max_iter=1000)

# 模型训练
model.fit(X_train, y_train)

# 模型预测
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# 模型评估
conf_matrix = confusion_matrix(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

# 输出评估指标
print("混淆矩阵：")
print(conf_matrix)
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1:.2f}")
print(f"AUC: {roc_auc:.2f}")

# 绘制ROC曲线
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.savefig('roc_curve.png')  # 保存图像