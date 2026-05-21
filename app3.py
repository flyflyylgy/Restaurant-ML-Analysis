from flask import Flask, render_template
from sqlalchemy import create_engine
import pandas as pd
import json

app = Flask(__name__)

def create_db_connection():
    try:
        engine = create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
        return engine
    except Exception as e:
        print("数据库连接错误:", e)
        return None

def get_age_gender_stress():
    engine = create_db_connection()
    if engine:
        try:
            query = """
            SELECT 年龄, 性别, AVG(学业压力) as 平均学业压力 
            FROM students_02 
            GROUP BY 年龄, 性别
            ORDER BY 年龄, 平均学业压力
            """
            df = pd.read_sql(query, engine)
            # 数据清洗
            df['平均学业压力'] = df['平均学业压力'].clip(0, 5).round(2)
            return df
        except Exception as e:
            print("查询执行错误:", e)
            return None
        finally:
            if engine:
                engine.dispose()
    return None

@app.route('/age_gender')
def age_gender_stress():
    data = get_age_gender_stress()
    if data is not None:
        ages = data['年龄'].astype(str).unique().tolist()
        male_stress = data[data['性别'] == '男']['平均学业压力'].tolist()
        female_stress = data[data['性别'] == '女']['平均学业压力'].tolist()

        return render_template('age_gender_stress.html',
                             ages=json.dumps(ages, ensure_ascii=False),
                             male_stress=json.dumps(male_stress),
                             female_stress=json.dumps(female_stress))
    else:
        return "无法获取数据", 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)