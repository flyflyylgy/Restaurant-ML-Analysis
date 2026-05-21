import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_graphviz
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
df = pd.read_csv('students03.csv')

# 定义特征变量和目标变量
X = pd.get_dummies(df.drop(columns=['抑郁症']), drop_first=True)
y = df['抑郁症']

# 数据拆分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 创建并训练决策树分类器
clf = DecisionTreeClassifier(
    max_depth=4,
    class_weight='balanced',
    random_state=42
)
clf.fit(X_train, y_train)

# 预测测试集
y_pred = clf.predict(X_test)

# 打印评估指标
print("混淆矩阵：")
print(confusion_matrix(y_test, y_pred))
print("\n分类报告：")
print(classification_report(y_test, y_pred))

# 优化决策树可视化（Matplotlib版本）
plt.figure(figsize=(25, 15))
plot_tree(clf,
          filled=True,
          feature_names=X.columns,
          class_names=['无抑郁', '抑郁'],
          max_depth=8,
          fontsize=10,
          rounded=True,
          proportion=True,
          impurity=False,
          node_ids=False)
plt.title('决策树模型可视化 (最大深度=2)')
plt.savefig('decision_tree_clean.png', dpi=300, bbox_inches='tight')
plt.close()

# 优化特征重要性图表
feature_importance_df = pd.DataFrame({
    '特征': X.columns,
    '重要性': clf.feature_importances_
}).sort_values('重要性', ascending=True)

# 合并同类特征（处理one-hot编码产生的衍生特征）
feature_importance_df['特征'] = feature_importance_df['特征'].str.split('_').str[0]
feature_importance_df = feature_importance_df.groupby('特征').sum().reset_index()
feature_importance_df = feature_importance_df.sort_values('重要性', ascending=True)

plt.figure(figsize=(10, 8))
bars = plt.barh(
    feature_importance_df['特征'],
    feature_importance_df['重要性'],
    color='#1f77b4'
)

# 添加数值标签
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.005, bar.get_y() + bar.get_height() / 2,
             f'{width:.3f}',
             va='center',
             fontsize=10)

plt.xlabel('特征重要性', fontsize=12)
plt.ylabel('')
plt.title('关键特征重要性排名（合并同类项）', fontsize=14, pad=20)
plt.grid(axis='x', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('feature_importance_clean.png', dpi=300, bbox_inches='tight')
plt.close()

# 可选：Graphviz可视化（需要先安装Graphviz软件）
try:
    import graphviz

    # 设置Graphviz路径（根据实际安装位置修改）
    os.environ["PATH"] += os.pathsep + 'D:/Program Files/Graphviz-12.2.1-win64/bin'

    dot_data = export_graphviz(clf, out_file=None,
                               feature_names=X.columns,
                               class_names=['无抑郁', '抑郁'],
                               filled=True,
                               rounded=True,
                               special_characters=True,
                               fontname="Microsoft YaHei",
                               max_depth=12)
    graph = graphviz.Source(dot_data)
    graph.format = 'png'
    graph.engine = 'dot'
    graph.graph_attr = {'fontname': 'Microsoft YaHei'}  # 全局字体设置
    graph.node_attr = {'fontname': 'Microsoft YaHei'}  # 节点字体
    graph.edge_attr = {'fontname': 'Microsoft YaHei'}  # 连线字体
    graph.render("decision_tree_graphviz", format='png', cleanup=True)
    print("Graphviz决策树已保存为decision_tree_graphviz.png")
except Exception as e:
    print(f"Graphviz可视化失败，请确保已安装Graphviz: {e}")

# 可选：保存模型
# import joblib
# joblib.dump(clf, 'depression_detection_model.pkl')