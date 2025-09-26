import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456789',  # 替换成你刚刚设置的密码
    'database': 'api_test_data'
}

try:
    print("Trying to connect to the database...")
    db_connection = mysql.connector.connect(**DB_CONFIG)
    print("Database connection established successfully!")
    
    cursor = db_connection.cursor()
    
    # 尝试插入一条测试数据
    sql = "INSERT INTO api_logs (endpoint, request_params, response_time, status_code, is_success) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, ('/test_path', '{}', 0.5, 200, True))
    db_connection.commit()
    
    print("Test data inserted successfully!")
    
    cursor.close()
    db_connection.close()
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
    
print("Script finished.")