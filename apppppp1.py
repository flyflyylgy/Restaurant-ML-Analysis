from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine
import pandas as pd
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('a2.html')
def create_db_connection():
    try:
        return create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
    except Exception as e:
        app.logger.error(f"数据库连接错误: {str(e)}")
        return None


@app.route('/api/boxplot_data')
def get_boxplot_data():
    engine = None
    try:
        engine = create_db_connection()
        if not engine:
            return jsonify({'error': '数据库连接失败'}), 500

        # 使用正确的列名查询
        query = """
        SELECT 
            抑郁症 as has_depression,
            学业压力 as stress,
            学习满意度 as satisfaction,
            CASE 
                WHEN 睡眠时长 = '小于5小时' THEN 4.5
                WHEN 睡眠时长 = '5到6小时' THEN 5.5
                WHEN 睡眠时长 = '7到8小时' THEN 7.5
                WHEN 睡眠时长 = '超过8小时' THEN 8.5
                ELSE NULL
            END as sleep_hours
        FROM students_02
        WHERE 学业压力 IS NOT NULL
        AND 学习满意度 IS NOT NULL
        AND 睡眠时长 IS NOT NULL
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            return jsonify({'warning': '没有查询到有效数据'}), 404

        # 将数据分为抑郁症和非抑郁症两组
        depressed = df[df['has_depression'] == 1]
        non_depressed = df[df['has_depression'] == 0]

        # 准备箱型图数据
        def prepare_box_data(data, label):
            return {
                'label': label,
                'stress': data['stress'].tolist(),
                'satisfaction': data['satisfaction'].tolist(),
                'sleep_hours': data['sleep_hours'].tolist()
            }

        return jsonify({
            'depressed': prepare_box_data(depressed, '抑郁症群体'),
            'non_depressed': prepare_box_data(non_depressed, '非抑郁症群体'),
            'columns_used': {
                'depression': '抑郁症',
                'stress': '学业压力',
                'satisfaction': '学习满意度',
                'sleep_duration': '睡眠时长'
            }
        })

    except Exception as e:
        app.logger.error(f"服务器错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': '内部服务器错误',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
    finally:
        if engine:
            engine.dispose()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)