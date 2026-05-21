import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
df = pd.read_csv('students03.csv')

# 1. 聚类分析 (无监督学习)
# 准备数据 - 只使用特征，不使用标签
X_cluster = pd.get_dummies(df.drop(columns=['抑郁症']), drop_first=True)

# 标准化数据 (聚类对尺度敏感)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

# 寻找最佳K值 (使用轮廓系数)
silhouette_scores = []
k_range = range(2, 8)  # 测试2-7个聚类

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    cluster_labels = kmeans.fit_predict(X_scaled)
    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
    silhouette_scores.append(silhouette_avg)
    print(f"对于k={k}，轮廓系数={silhouette_avg:.3f}")

# 绘制轮廓系数图
plt.figure(figsize=(10, 6))
plt.plot(k_range, silhouette_scores, 'bo-')
plt.xlabel('聚类数量(k)', fontsize=12)
plt.ylabel('轮廓系数', fontsize=12)
plt.title('不同k值的轮廓系数', fontsize=14)
plt.grid(True)
plt.savefig('silhouette_scores.png', dpi=300, bbox_inches='tight')
plt.close()

# 使用最佳k值进行最终聚类
best_k = k_range[np.argmax(silhouette_scores)]
print(f"\n最佳聚类数量: {best_k} (基于最高轮廓系数)")

final_kmeans = KMeans(n_clusters=best_k, random_state=42)
final_clusters = final_kmeans.fit_predict(X_scaled)

# 将聚类结果添加到原始数据
df['聚类分组'] = final_clusters

# 2. KNN分类 (监督学习)
# 准备数据
X = pd.get_dummies(df.drop(columns=['抑郁症', '聚类分组']), drop_first=True)
y = df['抑郁症']

# 数据拆分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 创建并训练KNN分类器
knn = KNeighborsClassifier(n_neighbors=5)  # 默认使用5个邻居
knn.fit(X_train, y_train)

# 预测测试集
y_pred = knn.predict(X_test)

# 打印评估指标
print("\nKNN分类结果:")
print("混淆矩阵：")
print(confusion_matrix(y_test, y_pred))
print("\n分类报告：")
print(classification_report(y_test, y_pred))

# 保存聚类结果
df.to_csv('students_with_clusters.csv', index=False)
print("\n聚类分析结果已保存到students_with_clusters.csv")