from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
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

# ------------------------- 数据获取函数 -------------------------

def get_stress_depression():
    """获取学业压力与抑郁症关系数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 
                学业压力,
                SUM(CASE WHEN 抑郁症 = 1 THEN 1 ELSE 0 END) as 患抑郁症人数,
                SUM(CASE WHEN 抑郁症 = 0 THEN 1 ELSE 0 END) as 未患抑郁症人数,
                COUNT(*) as 总人数
            FROM students_02
            GROUP BY 学业压力
            ORDER BY 学业压力
            """
            df = pd.read_sql(query, engine)
            df['抑郁症占比'] = (df['患抑郁症人数'] / df['总人数'] * 100).round(2)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None

def get_financial_depression():
    """获取财务压力与抑郁症关系数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 
                财务压力,
                SUM(CASE WHEN 抑郁症 = 1 THEN 1 ELSE 0 END) as 患抑郁症人数,
                SUM(CASE WHEN 抑郁症 = 0 THEN 1 ELSE 0 END) as 未患抑郁症人数,
                COUNT(*) as 总人数
            FROM students_02
            GROUP BY 财务压力
            ORDER BY 财务压力
            """
            df = pd.read_sql(query, engine)
            df['抑郁症占比'] = (df['患抑郁症人数'] / df['总人数'] * 100).round(2)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None


def get_suicide_depression_boxplot():
    """获取自杀念头与抑郁症关系的箱线图数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 
                是否有过自杀念头,
                学业压力,
                财务压力,
                学习满意度,
                工作学习时间,
                睡眠时长
            FROM students_02
            """
            df = pd.read_sql(query, engine)

            # 转换睡眠时长为数值
            sleep_mapping = {
                '小于5小时': 4,
                '5到6小时': 5.5,
                '7到8小时': 7.5,
                '超过8小时': 9
            }
            df['睡眠小时数'] = df['睡眠时长'].map(sleep_mapping)

            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None


def get_decision_tree_data():
    """获取决策树分析数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 
                性别, 年龄, 城市, 学业压力, 财务压力, 
                学习满意度, 睡眠时长, 饮食习惯, 学位, 
                工作学习时间, 精神疾病家族史, 抑郁症
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
# ------------------------- 路由定义 -------------------------

@app.route('/')
def dashboard():
    return render_template('depression_dashboard.html')

@app.route('/api/stress/depression')
def stress_depression_api():
    data = get_stress_depression()
    if data is not None:
        return jsonify({
            'stress_levels': data['学业压力'].tolist(),
            'depressed': data['患抑郁症人数'].tolist(),
            'not_depressed': data['未患抑郁症人数'].tolist(),
            'depression_rate': data['抑郁症占比'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500

@app.route('/api/financial/depression')
def financial_depression_api():
    data = get_financial_depression()
    if data is not None:
        return jsonify({
            'financial_levels': data['财务压力'].tolist(),
            'depressed': data['患抑郁症人数'].tolist(),
            'not_depressed': data['未患抑郁症人数'].tolist(),
            'depression_rate': data['抑郁症占比'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/suicide/depression/boxplot')
def suicide_depression_boxplot_api():
    """自杀念头与抑郁症关系的箱线图API"""
    data = get_suicide_depression_boxplot()
    if data is not None:
        # 按是否有自杀念头分组
        grouped = data.groupby('是否有过自杀念头')

        result = {}
        for col in ['学业压力', '财务压力', '学习满意度', '工作学习时间', '睡眠小时数']:
            for group in ['Yes', 'No']:
                if group in grouped.groups:
                    result[f'{col}_{group}'] = grouped.get_group(group)[col].dropna().tolist()

        return jsonify(result)
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/decision/tree')
def decision_tree_api():
    """决策树分析API"""
    data = get_decision_tree_data()
    if data is not None:
        # 准备特征和目标变量
        features = data.drop('抑郁症', axis=1)
        target = data['抑郁症']

        # 训练决策树
        tree = DecisionTreeClassifier(max_depth=3, random_state=42)
        tree.fit(features, target)

        # 获取特征重要性
        importance = dict(zip(features.columns, tree.feature_importances_))

        # 获取决策树规则
        tree_rules = export_text(tree, feature_names=list(features.columns))

        return jsonify({
            'feature_importance': importance,
            'tree_rules': tree_rules
        })
    return jsonify({'error': '数据获取失败'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)