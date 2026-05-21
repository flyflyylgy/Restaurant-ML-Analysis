from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)


def create_db_connection():
    try:
        return create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
    except Exception as e:
        app.logger.error(f"数据库连接错误: {str(e)}")
        return None

@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('a1.html')
@app.route('/api/stress_depression')
def get_stress_depression():
    engine = None
    try:
        engine = create_db_connection()
        if not engine:
            return jsonify({'error': '数据库连接失败'}), 500

        query = """
        SELECT 
            学业压力 as stress_level,
            COUNT(*) as total_count,
            SUM(抑郁症) as depression_count,
            ROUND(AVG(学习满意度), 2) as avg_satisfaction
        FROM students_02
        GROUP BY 学业压力
        ORDER BY 学业压力
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            return jsonify({'warning': '没有查询到数据'}), 404

        df['depression_rate'] = (df['depression_count'] / df['total_count'] * 100).round(2)

        return jsonify({
            'stress_levels': df['stress_level'].tolist(),
            'total_counts': df['total_count'].tolist(),
            'depression_counts': df['depression_count'].tolist(),
            'depression_rates': df['depression_rate'].tolist(),
            'avg_satisfaction': df['avg_satisfaction'].tolist()
        })

    except Exception as e:
        app.logger.error(f"错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    finally:
        if engine:
            engine.dispose()


@app.route('/api/gpa_depression')
def get_gpa_depression():
    engine = None
    try:
        engine = create_db_connection()
        if not engine:
            return jsonify({'error': '数据库连接失败'}), 500

        query = """
        SELECT 
            学位 as degree,
            ROUND(AVG(CASE 
                WHEN 累积平均绩点 = '9到10' THEN 9.5
                WHEN 累积平均绩点 = '8到9' THEN 8.5
                WHEN 累积平均绩点 = '7到8' THEN 7.5
                WHEN 累积平均绩点 = '6到7' THEN 6.5
                WHEN 累积平均绩点 = '5到6' THEN 5.5
                ELSE 0
            END), 2) as avg_gpa,
            COUNT(*) as total_count,
            SUM(抑郁症) as depression_count
        FROM students_02
        GROUP BY 学位
        ORDER BY avg_gpa DESC
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            return jsonify({'warning': '没有查询到数据'}), 404

        df['depression_rate'] = (df['depression_count'] / df['total_count'] * 100).round(2)

        return jsonify({
            'degrees': df['degree'].tolist(),
            'avg_gpas': df['avg_gpa'].tolist(),
            'total_counts': df['total_count'].tolist(),
            'depression_counts': df['depression_count'].tolist(),
            'depression_rates': df['depression_rate'].tolist()
        })

    except Exception as e:
        app.logger.error(f"错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    finally:
        if engine:
            engine.dispose()


@app.route('/api/sleep_depression')
def get_sleep_depression():
    engine = None
    try:
        engine = create_db_connection()
        if not engine:
            return jsonify({'error': '数据库连接失败'}), 500

        query = """
        SELECT 
            睡眠时长 as sleep_duration,
            COUNT(*) as total_count,
            SUM(抑郁症) as depression_count,
            ROUND(AVG(学业压力), 2) as avg_stress
        FROM students_02
        GROUP BY 睡眠时长
        ORDER BY FIELD(睡眠时长, '小于5小时', '5到6小时', '7到8小时', '超过8小时')
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            return jsonify({'warning': '没有查询到数据'}), 404

        df['depression_rate'] = (df['depression_count'] / df['total_count'] * 100).round(2)

        return jsonify({
            'sleep_durations': df['sleep_duration'].tolist(),
            'total_counts': df['total_count'].tolist(),
            'depression_counts': df['depression_count'].tolist(),
            'depression_rates': df['depression_rate'].tolist(),
            'avg_stress': df['avg_stress'].tolist()
        })

    except Exception as e:
        app.logger.error(f"错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    finally:
        if engine:
            engine.dispose()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)