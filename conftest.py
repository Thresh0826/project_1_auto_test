import pytest
import mysql.connector

@pytest.fixture(scope="session")
def db_connection():
    """
    一个 Pytest fixture，用于管理数据库连接
    """
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456789',  # 替换成你刚刚设置的密码
        'database': 'api_test_data'
    }
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("\nDatabase connection established successfully.")
        yield connection  # 在这里，Pytest 会运行你的测试用例
        connection.close()
        print("\nDatabase connection closed.")
    except mysql.connector.Error as err:
        print(f"\nError: {err}")
        pytest.fail("Failed to connect to the database.")