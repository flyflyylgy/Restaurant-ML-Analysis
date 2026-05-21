from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS
import numpy as np
from scipy import stats

app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 数据库连接配置
def create_db_connection():
    try:
        return create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
    except Exception as e:
        print("数据库连接错误:", e)
        return None

# 计算相关系数
def calculate_correlation(data, factor):
    depression = data['抑郁症']
    factor_data = data[factor]
    
    # 处理非数值型数据
    if factor_data.dtype == 'object':
        # 对分类变量进行编码
        try:
            encoded = pd.get_dummies(factor_data)
            correlations = {}
            for col in encoded.columns:
                # 确保没有完全为0或1的情况
                if encoded[col].nunique() > 1 and depression.nunique() > 1:
                    corr, _ = stats.pointbiserialr(encoded[col], depression)
                    correlations[col] = corr
            return correlations
        except:
            return {"error": "无法计算分类变量相关性"}
    else:
        # 对连续变量使用Pearson相关系数
        try:
            # 确保数据有效且不全是相同的值
            if factor_data.nunique() > 1 and depression.nunique() > 1:
                # 处理可能的空值
                valid_idx = factor_data.notna() & depression.notna()
                if sum(valid_idx) > 0:
                    corr, _ = stats.pearsonr(factor_data[valid_idx], depression[valid_idx])
                    return corr
            return 0  # 如果无法计算，返回0表示无相关性
        except:
            return 0  # 如果出错，返回0表示无相关性

# 获取抑郁症相关数据
def get_depression_data():
    engine = create_db_connection()
    if engine:
        try:
            # 获取完整数据
            query = "SELECT * FROM students_02"
            df = pd.read_sql(query, engine)
            
            # 预处理数据 - 确保"工作/学习时间"是数值
            if '工作/学习时间' in df.columns:
                df['工作/学习时间'] = pd.to_numeric(df['工作/学习时间'], errors='coerce')
            
            # 1. 基本统计数据
            depression_rate = df['抑郁症'].mean()
            depression_by_gender = df.groupby('性别')['抑郁症'].mean().to_dict()
            
            # 2. 相关性分析 - 只选择可以计算相关性的因素
            factors = ['学业压力', '睡眠时长', '饮食习惯', '财务压力', '精神疾病家族史', 
                      '是否有过自杀念头', '学习满意度']
            
            # 如果"工作/学习时间"存在且可以转换为数值，则加入分析
            if '工作/学习时间' in df.columns and df['工作/学习时间'].notna().any():
                factors.append('工作/学习时间')
            
            correlations = {}
            for factor in factors:
                correlations[factor] = calculate_correlation(df, factor)
            
            # 3. 抑郁症高风险群体分析
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
                                   (df['精神疾病家族史'] == 'Yes')]['抑郁症'].mean(),
                '学业压力+睡眠时长+精神疾病家族史': df[(df['学业压力'] >= 4) & 
                            (df['睡眠时长'] == '小于5小时') & 
                            (df['精神疾病家族史'] == 'Yes')]['抑郁症'].mean()
            }
            
            # 5. 城市分析
            city_depression = df.groupby('城市')['抑郁症'].mean().sort_values(ascending=False).head(10)
            
            # 6. 年龄分析
            age_depression = df.groupby('年龄')['抑郁症'].mean().sort_index()
            
            # 7. 风险因素趋势分析 (新增部分)
            factor_trends = {}
            trend_factors = ['学业压力', '睡眠时长', '财务压力', '学习满意度']
            
            for factor in trend_factors:
                if factor in df.columns:
                    if df[factor].dtype == 'object':  # 分类变量
                        trend = df.groupby(factor)['抑郁症'].mean().sort_values()
                        factor_trends[factor] = {
                            'categories': trend.index.tolist(),
                            'rates': trend.values.tolist()
                        }
                    else:  # 数值变量
                        # 将数值变量分箱处理
                        bins = pd.cut(df[factor], bins=5, duplicates='drop')
                        trend = df.groupby(bins)['抑郁症'].mean()
                        factor_trends[factor] = {
                            'categories': [str(x) for x in trend.index],
                            'rates': trend.values.tolist()
                        }
            
            return {
                'depression_rate': depression_rate,
                'depression_by_gender': depression_by_gender,
                'correlations': correlations,
                'high_risk_groups': high_risk_groups,
                'combo_analysis': combo_analysis,
                'city_depression': {
                    'cities': city_depression.index.tolist(),
                    'rates': city_depression.values.tolist()
                },
                'age_depression': {
                    'ages': age_depression.index.tolist(),
                    'rates': age_depression.values.tolist()
                },
                'factor_trends': factor_trends  # 新增数据
            }
        except Exception as e:
            print("查询执行错误:", str(e))
            return None
        finally:
            if engine:
                engine.dispose()
    return None

# 路由定义
@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('d6.html')

@app.route('/api/depression/data')
def depression_api():
    """抑郁症数据API"""
    data = get_depression_data()
    if data is not None:
        return jsonify(data)
    return jsonify({'error': '数据获取失败'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)