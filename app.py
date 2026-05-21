from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS
import numpy as np
from scipy import stats
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)


# 数据库连接配置
def create_db_connection():
    try:
        return create_engine('mysql+pymysql://root:123456@localhost/students01?charset=utf8mb4')
    except Exception as e:
        print("数据库连接错误:", e)
        return None


# 计算相关系数
def calculate_correlation(data, factor):
    depression = data['抑郁症']
    factor_data = data[factor]

    if factor_data.dtype == 'object':
        try:
            encoded = pd.get_dummies(factor_data)
            correlations = {}
            for col in encoded.columns:
                if encoded[col].nunique() > 1 and depression.nunique() > 1:
                    corr, _ = stats.pointbiserialr(encoded[col], depression)
                    correlations[col] = corr
            return correlations
        except:
            return {"error": "无法计算分类变量相关性"}
    else:
        try:
            if factor_data.nunique() > 1 and depression.nunique() > 1:
                valid_idx = factor_data.notna() & depression.notna()
                if sum(valid_idx) > 0:
                    corr, _ = stats.pearsonr(factor_data[valid_idx], depression[valid_idx])
                    return corr
            return 0
        except:
            return 0


# 获取抑郁症相关数据
def get_depression_data():
    engine = create_db_connection()
    if engine:
        try:
            df = pd.read_sql("SELECT * FROM students_02", engine)

            # 预处理
            if '工作/学习时间' in df.columns:
                df['工作/学习时间'] = pd.to_numeric(df['工作/学习时间'], errors='coerce')

            # 1. 基本统计数据
            depression_rate = df['抑郁症'].mean()
            depression_by_gender = df.groupby('性别')['抑郁症'].mean().to_dict()

            # 2. 相关性分析
            factors = ['学业压力', '睡眠时长', '饮食习惯', '财务压力', '精神疾病家族史',
                       '是否有过自杀念头', '学习满意度']

            if '工作/学习时间' in df.columns and df['工作/学习时间'].notna().any():
                factors.append('工作/学习时间')

            correlations = {}
            for factor in factors:
                correlations[factor] = calculate_correlation(df, factor)

            # 3. 高风险群体分析
            high_risk_groups = {
                '自杀念头': df[df['是否有过自杀念头'] == 'Yes']['抑郁症'].mean(),
                '家族史': df[df['精神疾病家族史'] == 'Yes']['抑郁症'].mean(),
                '睡眠不足': df[df['睡眠时长'] == '小于5小时']['抑郁症'].mean(),
                '高学业压力': df[df['学业压力'] >= 4]['抑郁症'].mean()
            }

            # 4. 多因素组合分析
            combo_analysis = {
                '学业压力+睡眠不足': df[(df['学业压力'] >= 4) &
                                        (df['睡眠时长'] == '小于5小时')]['抑郁症'].mean(),
                '财务压力+家族史': df[(df['财务压力'] >= 4) &
                                      (df['精神疾病家族史'] == 'Yes')]['抑郁症'].mean()
            }

            # 5. 城市分析
            city_depression = df.groupby('城市')['抑郁症'].mean().sort_values(ascending=False).head(10)

            # 6. 年龄分析
            age_depression = df.groupby('年龄')['抑郁症'].mean().sort_index()

            # 7. 决策树分析
            le = LabelEncoder()
            df_encoded = df.apply(lambda col: le.fit_transform(col.astype(str)) if col.dtype == 'object' else col)

            clf = DecisionTreeClassifier(max_depth=3)
            X = df_encoded.drop('抑郁症', axis=1)
            y = df_encoded['抑郁症']
            clf.fit(X, y)
            tree_rules = export_text(clf, feature_names=list(X.columns))

            return {
                'depression_rate': depression_rate,
                'depression_by_gender': depression_by_gender,
                'correlations': correlations,
                'high_risk_groups': high_risk_groups,
                'combo_analysis': combo_analysis,
                'city_depression': city_depression.to_dict(),
                'age_depression': age_depression.to_dict(),
                'decision_tree': tree_rules
            }
        except Exception as e:
            print("查询执行错误:", str(e))
            return None
        finally:
            engine.dispose()
    return None


# 路由定义
@app.route('/')
def dashboard():
    return render_template('d6.html')


@app.route('/api/depression/data')
def depression_api():
    data = get_depression_data()
    if data is not None:
        # 转换数据结构以匹配前端需求
        processed_data = {
            # 基础统计数据
            'depression_rate': data['depression_rate'],
            'depression_by_gender': data['depression_by_gender'],

            # 转换城市数据格式
            'city_depression': {
                'cities': list(data['city_depression'].keys()),
                'rates': [round(v * 100, 1) for v in data['city_depression'].values()]  # 转换为百分比
            },

            # 转换年龄数据格式
            'age_depression': {
                'ages': [str(age) for age in data['age_depression'].keys()],  # 确保年龄为字符串
                'rates': [round(v * 100, 1) for v in data['age_depression'].values()]
            },

            # 风险因素趋势分析数据
            'factor_trends': {
                '学业压力': {
                    'categories': ['<2', '2-3', '3-4', '4-5', '>5'],  # 示例分箱
                    'rates': [0.35, 0.45, 0.55, 0.65, 0.75]  # 示例数据
                },
                '睡眠时长': {
                    'categories': ['<5小时', '5-6小时', '6-7小时', '7-8小时', '>8小时'],
                    'rates': [0.65, 0.55, 0.45, 0.35, 0.25]
                }
            },

            # 其他数据保持不变
            'correlations': data['correlations'],
            'high_risk_groups': data['high_risk_groups'],
            'combo_analysis': data['combo_analysis'],
            'decision_tree': data['decision_tree']
        }

        return jsonify(processed_data)
    return jsonify({'error': '数据获取失败'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)