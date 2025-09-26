import os
import sys
import json
import mysql.connector
from dashscope import Generation

# 数据库连接信息，来自你的 ai_data_prep.py 文件
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456789',
    'database': 'api_test_data'
}

def get_data_for_ai():
    """
    连接数据库并获取所有接口日志数据
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        sql = "SELECT endpoint, request_params, status_code, is_success FROM api_logs ORDER BY created_at DESC LIMIT 10" # 限制只获取最新的10条数据，以避免AI token超限
        cursor.execute(sql)
        
        records = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return records
    except mysql.connector.Error as err:
        print(f"数据库连接失败：{err}")
        return None

def generate_ai_prompt(api_logs_data):
    """
    根据接口日志数据，生成用于AI的Prompt
    """
    if not api_logs_data:
        return "没有可用的接口日志数据，无法生成测试用例。"
        
    # 我们只使用数据来构建JSON，而不是将整个数据dump到prompt中
    log_json = json.dumps(api_logs_data, indent=2, ensure_ascii=False)
    
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

def generate_test_cases(ai_prompt):
    """
    使用通义千问模型生成函数的单元测试用例。
    """
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')
    if not DASHSCOPE_API_KEY:
        raise ValueError("未找到 DASHSCOPE_API_KEY 环境变量。请先设置它。")

    try:
        print("正在调用通义千问模型生成测试用例...")
        response = Generation.call(
            model='qwen-plus',
            api_key=DASHSCOPE_API_KEY,
            prompt=ai_prompt,
            result_format='message',
            temperature=0.8
        )

        if response.status_code == 200:
            content = response.output.choices[0]['message']['content']
            try:
                # 尝试直接解析 JSON
                test_cases = json.loads(content)
                return test_cases
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试从字符串中提取JSON
                print("模型返回的不是标准JSON格式，正在尝试提取JSON...")
                start_index = content.find('{')
                end_index = content.rfind('}') + 1
                if start_index != -1 and end_index != -1:
                    json_string = content[start_index:end_index]
                    test_cases = json.loads(json_string)
                    return test_cases
                else:
                    print("无法从返回内容中提取JSON。")
                    return None
        else:
            print("请求失败，状态码：", response.status_code)
            print("错误信息：", response.message)
            return None

    except Exception as e:
        print(f"调用 API 失败：{e}")
        return None

def save_test_cases(test_cases, file_path="generated_test_cases.json"):
    """将生成的测试用例保存到文件中。"""
    if test_cases:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(test_cases, file, indent=4, ensure_ascii=False)
            print(f"测试用例已成功保存到 '{file_path}'。")
        except Exception as e:
            print(f"保存文件时发生错误：{e}")

if __name__ == "__main__":
    api_logs = get_data_for_ai()
    
    if api_logs:
        ai_prompt = generate_ai_prompt(api_logs)
        test_cases = generate_test_cases(ai_prompt)
        save_test_cases(test_cases)
    else:
        print("无法生成测试用例，因为没有从数据库获取到有效数据。")