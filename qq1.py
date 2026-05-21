import mysql.connector
import pandas as pd

# MySQL connection configuration
config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': '123456'
}

# Connect to MySQL
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Create the order02 table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS order02 (
        order_id VARCHAR(36) PRIMARY KEY,
        order_time DATETIME,
        delivery_time DATETIME,
        delivery_duration_min FLOAT,
        city VARCHAR(50),
        state VARCHAR(2),
        latitude FLOAT,
        longitude FLOAT,
        restaurant VARCHAR(100),
        is_canceled BOOLEAN,
        cancel_reason VARCHAR(100),
        customer_rating FLOAT
    )
    """

    cursor.execute(create_table_query)
    print("Table order02 created successfully")

    # Load data from CSV (assuming you have the file)
    # df = pd.read_csv('delivery_data_with_restaurants.csv')
    # You would then insert the data row by row

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()