import requests
import mysql.connector
import time
import json

class ApiClient:
    def __init__(self, base_url, db_connection):
        self.base_url = base_url
        self.session = requests.Session()
        self.db_connection = db_connection  # 接收从 fixture 传来的连接
        self.cursor = self.db_connection.cursor()

    def post(self, path, data=None, json=None, headers=None, **kwargs):
        url = self.base_url + path
        start_time=time.time()
        response = self.session.post(url, data=data, json=json, headers=headers, **kwargs)
        end_time=time.time()
        response_time=end_time-start_time
        self.log_api_call(
            endpoint=path,
            request_params=json or data,
            response_time=response_time,
            status_code=response.status_code
        )
        return response

    def get(self, path, params=None, headers=None, **kwargs):
        url = self.base_url + path
        start_time = time.time()
        
        response = self.session.get(url, params=params, headers=headers, **kwargs)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 记录日志
        self.log_api_call(
            endpoint=path,
            request_params=params,
            response_time=response_time,
            status_code=response.status_code
        )
        return response
    def log_api_call(self, endpoint, request_params, response_time, status_code):
        is_success = status_code == 200
        error_type = None if is_success else "HTTP Error"
        if request_params is None:
        	params_json="null"
        else:
        	 params_json = json.dumps(request_params)
        sql = "INSERT INTO api_logs (endpoint, request_params, response_time, status_code, is_success, error_type) VALUES (%s, %s, %s, %s, %s, %s)"
        
        try:
            self.cursor.execute(sql, (
                endpoint,
                params_json,  # 数据库中我们使用 VARCHAR 或 JSON 存储，这里用 str 转换
                response_time,
                status_code,
                is_success,
                error_type
            ))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")