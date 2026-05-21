from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 解决跨域问题


# 数据库连接配置
def create_db_connection():
    try:
        return create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
    except Exception as e:
        print("数据库连接错误:", e)
        return None


# ------------------------- 数据获取函数 -------------------------

def get_stress_data(stress_level=None):
    """获取指定压力等级的城市数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = f"""
            SELECT 城市, COUNT(*) as 人数 
            FROM students_02 
            {f'WHERE 学业压力 = {stress_level}' if stress_level else ''}
            GROUP BY 城市 
            ORDER BY 人数 DESC 
            LIMIT 6
            """
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None


def get_age_gender_stress():
    """获取年龄-性别压力数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 年龄, 性别, AVG(学业压力) as 平均压力 
            FROM students_02 
            GROUP BY 年龄, 性别
            ORDER BY 年龄, 性别
            """
            df = pd.read_sql(query, engine)
            df['平均压力'] = df['平均压力'].clip(0, 5).round(2)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None


def get_sleep_data():
    """获取睡眠数据"""
    engine = create_db_connection()
    if engine:
        try:
            df = pd.read_sql("SELECT 城市, 睡眠时长 FROM students_02", engine)
            df['睡眠小时数'] = df['睡眠时长'].apply(lambda s: (
                4 if '小于' in s else
                5.5 if '5到6' in s else
                7.5 if '7到8' in s else
                9 if '超过8' in s else float('nan')
            ))
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None

# ------------------------- 新增数据获取函数 -------------------------

def get_pressure_satisfaction():
    """获取学业压力与学习满意度的关系数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 学业压力, AVG(学习满意度) as 平均学习满意度 
            FROM students_02 
            GROUP BY 学业压力 
            ORDER BY 学业压力
            """
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None



def get_top_work_study_cities():
    """获取工作/学习时间最长的前10个城市"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 城市, AVG(工作学习时间) as 平均工作时间 
            FROM students_02 
            GROUP BY 城市 
            ORDER BY 平均工作时间 DESC 
            LIMIT 10
            """
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None

def get_family_mental_history():
    """获取精神疾病家族史分布数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 精神疾病家族史, COUNT(*) as 人数 
            FROM students_02 
            GROUP BY 精神疾病家族史
            """
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None

def get_stress_satisfaction_by_age_gender():
    """获取各个年龄、不同性别的平均学业压力和平均学习满意度"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 年龄, 性别, AVG(学业压力) as avg_stress, AVG(学习满意度) as avg_satisfaction
            FROM students_02
            GROUP BY 年龄, 性别
            ORDER BY 年龄
            """
            df = pd.read_sql(query, engine)
            df['平均压力'] = df['avg_stress'].clip(0, 5).round(2)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None
def get_avg_gpa_by_degree():
    """获取不同学位的平均累积平均绩点"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 学位, AVG(累积平均绩点) as avg_gpa
            FROM students_02
            GROUP BY 学位
            ORDER BY 学位
            """
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None

def get_features_with_suicidal_thoughts():
    """获取有自杀念头的人群特征"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 身份证, 性别, 年龄, 城市, 学业压力, 累积平均绩点, 学习满意度, 睡眠时长, 饮食习惯, 学位, 工作学习时间, 财务压力, 精神疾病家族史
            FROM students_02
            WHERE 是否有过自杀念头 = 'Yes'
            """
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None
# ------------------------- 新增数据获取函数 -------------------------

# ------------------------- 新增路由定义 -------------------------

@app.route('/api/work_study/top_cities')
def work_study_top_cities_api():
    """工作/学习时间最长的前10个城市API"""
    data = get_top_work_study_cities()
    if data is not None:
        return jsonify({
            'cities': data['城市'].tolist(),
            'avg_hours': data['平均工作时间'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500

@app.route('/api/family/mental_history')
def family_mental_history_api():
    """精神疾病家族史分布API"""
    data = get_family_mental_history()
    if data is not None:
        return jsonify({
            'history': data['精神疾病家族史'].tolist(),
            'counts': data['人数'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500

def get_diet_pressure():
    """获取饮食习惯与学业压力的关系数据"""
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 饮食习惯, AVG(学业压力) as 平均学业压力 
            FROM students_02 
            GROUP BY 饮食习惯 
            ORDER BY 饮食习惯
            """
            df = pd.read_sql(query, engine)
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
    """主仪表板页面"""
    return render_template('dashboard01.html')


@app.route('/api/stress/high')
def stress_high_api():
    """高压数据API"""
    data = get_stress_data(5)
    if data is not None:
        return jsonify({
            'cities': data['城市'].tolist(),
            'counts': data['人数'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/stress/low')
def stress_low_api():
    """低压数据API"""
    data = get_stress_data(1)
    if data is not None:
        return jsonify({
            'cities': data['城市'].tolist(),
            'counts': data['人数'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/age_gender/stress')
def age_gender_api():
    """年龄性别压力API"""
    data = get_age_gender_stress()
    if data is not None:
        # 处理数据格式，确保男女数据对应相同的年龄
        ages = sorted(data['年龄'].unique())
        male_data = []
        female_data = []

        for age in ages:
            male = data[(data['年龄'] == age) & (data['性别'] == '男')]
            female = data[(data['年龄'] == age) & (data['性别'] == '女')]

            male_data.append(male['平均压力'].values[0] if not male.empty else 0)
            female_data.append(female['平均压力'].values[0] if not female.empty else 0)

        return jsonify({
            'ages': [str(age) for age in ages],
            'male': male_data,
            'female': female_data
        })
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/sleep/data')
def sleep_api():
    """睡眠数据API"""
    data = get_sleep_data()
    if data is not None:
        less_5 = data[data['睡眠小时数'] < 5]['城市'].value_counts().head(6)
        over_8 = data[data['睡眠小时数'] > 8]['城市'].value_counts().head(6)
        return jsonify({
            'less5': {
                'cities': less_5.index.tolist(),
                'counts': less_5.values.tolist()
            },
            'over8': {
                'cities': over_8.index.tolist(),
                'counts': over_8.values.tolist()
            }
        })
    return jsonify({'error': '数据获取失败'}), 500
# ------------------------- 新增路由定义 -------------------------

@app.route('/api/pressure/satisfaction')
def pressure_satisfaction_api():
    """学业压力与学习满意度API"""
    data = get_pressure_satisfaction()
    if data is not None:
        return jsonify({
            'pressure_levels': data['学业压力'].tolist(),
            'avg_satisfaction': data['平均学习满意度'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500


@app.route('/api/diet/pressure')
def diet_pressure_api():
    """饮食习惯与学业压力API"""
    data = get_diet_pressure()
    if data is not None:
        return jsonify({
            'diets': data['饮食习惯'].tolist(),
            'avg_pressure': data['平均学业压力'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500

@app.route('/api/stress/satisfaction/by_age_gender')
def stress_satisfaction_by_age_gender_api():
    """获取各个年龄、不同性别的平均学业压力和平均学习满意度API"""
    data = get_stress_satisfaction_by_age_gender()
    if data is not None:
        return jsonify({
            'ages': data['年龄'].tolist(),
            'male': data[data['性别'] == '男']['平均压力'].tolist(),
            'female': data[data['性别'] == '女']['平均压力'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500

@app.route('/api/avg_gpa_by_degree')
def avg_gpa_by_degree_api():
    """获取不同学位的平均累积平均绩点API"""
    data = get_avg_gpa_by_degree()
    if data is not None:
        return jsonify({
            'degrees': data['学位'].tolist(),
            'avg_gpa': data['avg_gpa'].tolist()
        })
    return jsonify({'error': '数据获取失败'}), 500

@app.route('/api/features_with_suicidal_thoughts')
def features_with_suicidal_thoughts_api():
    """获取有自杀念头的人群特征API"""
    data = get_features_with_suicidal_thoughts()
    if data is not None:
        return jsonify({
            'features': data.to_dict('records')
        })
    return jsonify({'error': '数据获取失败'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)