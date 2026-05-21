# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # 允许所有域名访问

def get_db_connection():
    conn = mysql.connector.connect(
        user='root',
        password='123456',
        host='localhost',
        database='students01'  # 替换为您的数据库名称
    )
    return conn

@app.route('/data')
def data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            年龄 as age, 
            性别 as gender, 
            AVG(学业压力) AS avg_pressure 
        FROM students_02 
        GROUP BY 年龄, 性别 
        ORDER BY avg_pressure ASC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)