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


def get_sleep_data():
    engine = create_db_connection()
    if engine:
        try:
            df = pd.read_sql("SELECT 城市, 睡眠时长 FROM students_02", engine)
            # 转换睡眠时长
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


@app.route('/')
def sleep_dashboard():
    data = get_sleep_data()
    if data is not None:
        # 处理睡眠不足5小时的数据
        less_5 = data[data['睡眠小时数'] < 5]['城市'].value_counts().head(6)
        # 处理睡眠超过8小时的数据
        over_8 = data[data['睡眠小时数'] > 8]['城市'].value_counts().head(6)

        return render_template('sleep_dashboard.html',
                               less5_cities=json.dumps(less_5.index.tolist(), ensure_ascii=False),
                               less5_values=json.dumps(less_5.values.tolist()),
                               over8_cities=json.dumps(over_8.index.tolist(), ensure_ascii=False),
                               over8_values=json.dumps(over_8.values.tolist()))
    else:
        return "无法获取数据", 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)