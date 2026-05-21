from flask import Flask, render_template
from sqlalchemy import create_engine
import pandas as pd
import json

app = Flask(__name__)


def create_connection():
    try:
        engine = create_engine('mysql+mysqlconnector://root:123456@localhost/students01')
        return engine
    except Exception as e:
        print("数据库连接错误:", e)
        return None


def get_data_from_db():
    engine = create_connection()
    if engine:
        try:
            query = """
            SELECT 城市, COUNT(*) as 压力人数 
            FROM students_02 
            WHERE 学业压力 = 5 
            GROUP BY 城市 
            ORDER BY 压力人数 DESC 
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


@app.route('/')
def index():
    data = get_data_from_db()
    if data is not None:
        # 确保城市名为字符串类型
        cities = [str(city) for city in data['城市'].tolist()]
        counts = data['压力人数'].tolist()

        return render_template('top_6_cities_with_stress_5.html',
                               cities=json.dumps(cities, ensure_ascii=False),
                               counts=json.dumps(counts))
    else:
        return "无法获取数据", 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 使用不同端口避免冲突