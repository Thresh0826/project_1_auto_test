from http.client import responses

import pytest
import requests

from api_client.client import ApiClient

BASE_URL = "https://httpbin.org/"

# 全局变量，用于存储登录后的 token
user_Agent = None


def test_login_and_get_user_info(db_connection):
    """
    一个完整的测试用例，模拟登录并使用token访问其他接口
    """
    # 1. 准备（Arrange）
    api_client = ApiClient(BASE_URL, db_connection)
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    # 2. 执行（Act） - 模拟登录
    login_response = api_client.post("/post", data=login_data)
    
    # 提取token，在实际应用中，这里会从login_response中解析token
    # 由于httpbin不返回token，我们使用一个假token
    if login_response.status_code == 200:
        fake_token = "mock_access_token"
    else:
        fake_token = None
    
    # 使用token发送GET请求
    headers = {
        "Authorization": f"Bearer {fake_token}"
    }
    params = {
        "page": 1,
        "limit": 10
    }
    #这是新加的注释，用于测试自动拉取代并构建功能，无实际作用
    user_info_response = api_client.get("/get", headers=headers)
    
    # 3. 断言（Assert） - 验证登录和获取用户信息是否成功
    assert login_response.status_code == 200
    assert user_info_response.status_code == 200
    
    # 验证我们发送的headers是否被httpbin正确接收
    assert user_info_response.json().get('headers').get('Authorization') == f"Bearer {fake_token}"
