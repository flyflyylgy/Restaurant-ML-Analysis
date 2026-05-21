# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import mysql.connector

app = Flask(__name__)
CORS(app)  # 允许所有域名访问

def get_db_connection():
    conn = mysql.connector.connect(
        user='root',
        password='123456',
        host='localhost',
        database='students01'
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

    return jsonify({
        'data': data,
        'stats': {
            'total': len(data),
            'max_pressure': max(d['avg_pressure'] for d in data),
            'min_pressure': min(d['avg_pressure'] for d in data)
        }
    })

if __name__ == '__main__':
    app.run(debug=True)