import mysql.connector
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456789',  # 替换成你的真实密码
    'database': 'api_test_data'
}

def get_data_for_ai():
    """
    连接数据库并获取所有接口日志数据
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)  # 使用字典游标，方便获取数据
        
        sql = "SELECT endpoint, request_params, status_code, is_success FROM api_logs ORDER BY created_at DESC"
        cursor.execute(sql)
        
        records = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return records
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# 获取数据
api_logs = get_data_for_ai()

if api_logs:
    print("成功从数据库获取数据。")
    print("数据示例:")
    print(json.dumps(api_logs, indent=4))
else:
    print("获取数据失败。请检查数据库连接或配置。")



def generate_ai_prompt(api_logs_data):
    """
    根据接口日志数据，生成用于AI的Prompt
    """
    if not api_logs_data:
        return "没有可用的接口日志数据，无法生成测试用例。"
        
    log_json = json.dumps(api_logs_data, indent=2)
    
    prompt = f"""
    请根据以下接口调用日志数据，生成3个新的、具有创新性的接口测试用例。
    
    数据格式说明：
    - endpoint: 接口路径
    - request_params: 请求参数
    - status_code: HTTP响应码
    - is_success: 调用是否成功
    
    请重点关注：
    - **边界条件**：参数为空、超出限制、特殊字符等。
    - **异常情况**：错误的状态码、不合法的参数组合等。
    - **业务逻辑**：根据已有的成功案例，提出新的、有挑战性的测试场景。
    
    接口日志数据:
    {log_json}
    
    请以以下JSON格式输出，每个测试用例包含：
    - `case_name`: 用例名称
    - `description`: 详细描述
    - `endpoint`: 测试的接口
    - `request_params`: 推荐的请求参数
    - `expected_status_code`: 期望的HTTP状态码
    
    ---JSON START---
    """
    return prompt

if api_logs:
    ai_prompt = generate_ai_prompt(api_logs)
    print("\n---以下是为AI生成的Prompt---")
    print(ai_prompt)