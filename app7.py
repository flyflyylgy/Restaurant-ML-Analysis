from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)


# 数据库连接配置
def create_db_connection():
    try:
        return create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
    except Exception as e:
        print("数据库连接错误:", e)
        return None


# 获取箱线图数据
def get_boxplot_data():
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 
                学业压力, 财务压力, 学习满意度, 
                工作学习时间, 睡眠时长, 饮食习惯,
                是否有过自杀念头, 抑郁症
            FROM students_02
            """
            df = pd.read_sql(query, engine)

            # 数据转换
            df['睡眠小时数'] = df['睡眠时长'].map({
                '小于5小时': 4,
                '5到6小时': 5.5,
                '7到8小时': 7.5,
                '超过8小时': 9
            })

            df['饮食习惯'] = df['饮食习惯'].map({
                'Healthy': 1,
                'Moderate': 2,
                'Unhealthy': 3
            })

            df['抑郁症分类'] = df['抑郁症'].map({1: '患抑郁症', 0: '未患抑郁症'})
            df['是否有过自杀念头'] = df['是否有过自杀念头'].map({'Yes': 1, 'No': 0})

            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None


# 获取决策树数据
def get_decision_tree_data():
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 
                性别, 年龄, 城市, 学业压力, 财务压力, 
                学习满意度, 睡眠时长, 饮食习惯, 学位, 
                工作学习时间, 精神疾病家族史, 是否有过自杀念头, 抑郁症
            FROM students_02
            """
            df = pd.read_sql(query, engine)

            # 数据预处理
            df['睡眠时长'] = df['睡眠时长'].map({
                '小于5小时': 0,
                '5到6小时': 1,
                '7到8小时': 2,
                '超过8小时': 3
            })

            df['饮食习惯'] = df['饮食习惯'].map({
                'Healthy': 0,
                'Moderate': 1,
                'Unhealthy': 2
            })

            df['是否有过自杀念头'] = df['是否有过自杀念头'].map({'Yes': 1, 'No': 0})

            # 编码分类变量
            le = LabelEncoder()
            categorical_cols = ['性别', '城市', '学位', '精神疾病家族史']
            for col in categorical_cols:
                df[col] = le.fit_transform(df[col])

            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None


# 路由定义
@app.route('/')
def dashboard():
    return render_template('dashboard02.html')


@app.route('/api/boxplot')
def boxplot_api():
    data = get_boxplot_data()
    if data is not None:
        grouped = data.groupby('抑郁症分类')
        result = {}

        # 包含所有需要分析的属性
        factors = [
            '学业压力', '财务压力', '学习满意度',
            '工作学习时间', '睡眠小时数', '饮食习惯',
            '是否有过自杀念头'
        ]

        for factor in factors:
            for group in ['患抑郁症', '未患抑郁症']:
                if group in grouped.groups:
                    result[f'{factor}_{group}'] = grouped.get_group(group)[factor].dropna().tolist()

        return jsonify({
            'factors': factors,
            'data': result
        })
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/treemap')
def treemap_api():
    data = get_decision_tree_data()
    if data is not None:
        try:
            # 准备特征和目标变量
            features = data.drop('抑郁症', axis=1)
            target = data['抑郁症']

            # 训练决策树
            tree = DecisionTreeClassifier(max_depth=4, random_state=42)
            tree.fit(features, target)

            # 获取特征重要性
            importance = dict(zip(features.columns, tree.feature_importances_))

            # 构建矩形树图数据
            treemap_data = {
                'name': '抑郁症影响因素',
                'children': []
            }

            for feature, imp in importance.items():
                if imp > 0.01:  # 只显示重要性大于1%的特征
                    treemap_data['children'].append({
                        'name': feature,
                        'value': round(imp * 100, 2)
                    })

            return jsonify({
                'treemap_data': treemap_data,
                'feature_importance': importance
            })
        except Exception as e:
            print("决策树训练错误:", e)
            return jsonify({'error': '决策树训练失败'}), 500
    return jsonify({'error': '数据获取失败'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)