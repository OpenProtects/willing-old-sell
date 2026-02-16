import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("=" * 60)
    print("API测试开始")
    print("=" * 60)
    
    # 1. 注册测试用户
    print("\n1. 注册测试用户...")
    response = requests.post(f"{BASE_URL}/auth/register/", json={
        "username": "testuser_api",
        "password": "test123456",
        "password_confirm": "test123456",
        "phone": "13900139001",
        "email": "testapi@example.com"
    })
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    token = None
    user_id = None
    if data.get('code') == 200:
        token = data['data']['token']['access']
        user_id = data['data']['user']['id']
    else:
        # 尝试登录
        print("\n尝试登录...")
        response = requests.post(f"{BASE_URL}/auth/login/", json={
            "username": "testuser_api",
            "password": "test123456"
        })
        data = response.json()
        print(f"登录响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if data.get('code') == 200:
            token = data['data']['token']['access']
            user_id = data['data']['user']['id']
    
    if not token:
        print("无法获取token，测试终止")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取用户信息
    print("\n2. 获取用户信息...")
    response = requests.get(f"{BASE_URL}/auth/users/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 3. 实名认证
    print("\n3. 实名认证...")
    response = requests.post(f"{BASE_URL}/auth/users/verify_realname/", 
        headers=headers,
        json={
            "real_name": "API测试用户",
            "id_card": "110101199001011111",
            "school_id": "2021999"
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 4. 获取品类列表
    print("\n4. 获取品类列表...")
    response = requests.get(f"{BASE_URL}/goods/categories/")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    category_id = data['data'][0]['id'] if data.get('code') == 200 and data['data'] else None
    
    # 5. 获取物品列表（首页API）
    print("\n5. 获取物品列表（首页API）...")
    response = requests.get(f"{BASE_URL}/goods/goods/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 6. 发布物品
    print("\n6. 发布物品...")
    response = requests.post(f"{BASE_URL}/goods/goods/", 
        headers=headers,
        json={
            "name": "API测试物品",
            "category": category_id,
            "description": "这是一个API测试物品",
            "price": 99.00,
            "condition": "good",
            "pickup_location": "图书馆"
        }
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    goods_id = data['data']['id'] if data.get('code') == 200 else None
    
    # 7. 获取物品详情
    if goods_id:
        print("\n7. 获取物品详情...")
        response = requests.get(f"{BASE_URL}/goods/goods/{goods_id}/", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 8. 搜索物品
    print("\n8. 搜索物品...")
    response = requests.get(f"{BASE_URL}/goods/goods/?keyword=测试", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 9. 创建心愿单
    print("\n9. 创建心愿单...")
    response = requests.post(f"{BASE_URL}/wishlist/wishlists/", 
        headers=headers,
        json={
            "name": "测试心愿单",
            "category": category_id,
            "min_price": 10,
            "max_price": 100,
            "description": "想要测试物品"
        }
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    wishlist_id = data['data']['wishlist']['id'] if data.get('code') == 200 else None
    
    # 10. 获取心愿单列表
    print("\n10. 获取心愿单列表...")
    response = requests.get(f"{BASE_URL}/wishlist/wishlists/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 11. 获取匹配结果
    if wishlist_id:
        print("\n11. 获取匹配结果...")
        response = requests.get(f"{BASE_URL}/wishlist/wishlists/{wishlist_id}/match_results/", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 12. 创建订单
    if goods_id:
        print("\n12. 创建订单...")
        response = requests.post(f"{BASE_URL}/orders/orders/", 
            headers=headers,
            json={"goods_id": goods_id}
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        order_id = data['data']['id'] if data.get('code') == 200 else None
        
        # 13. 支付订单
        if order_id:
            print("\n13. 支付订单...")
            response = requests.post(f"{BASE_URL}/orders/orders/{order_id}/pay/", headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            
            # 14. 确认收货
            print("\n14. 确认收货...")
            response = requests.post(f"{BASE_URL}/orders/orders/{order_id}/confirm/", headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            
            # 15. 评价
            print("\n15. 评价订单...")
            response = requests.post(f"{BASE_URL}/orders/evaluations/", 
                headers=headers,
                json={
                    "order": order_id,
                    "rating": "good",
                    "content": "非常好的交易"
                }
            )
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 16. 发送消息
    print("\n16. 发送消息...")
    response = requests.post(f"{BASE_URL}/chat/rooms/send_message/", 
        headers=headers,
        json={
            "receiver_id": 1,
            "content": "测试消息",
            "goods_id": goods_id,
            "goods_name": "API测试物品"
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 17. 获取聊天室列表
    print("\n17. 获取聊天室列表...")
    response = requests.get(f"{BASE_URL}/chat/rooms/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 18. 创建举报
    print("\n18. 创建举报...")
    response = requests.post(f"{BASE_URL}/report/reports/", 
        headers=headers,
        json={
            "reported_user": 1,
            "report_type": "other",
            "description": "测试举报"
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 19. 获取通知
    print("\n19. 获取通知...")
    response = requests.get(f"{BASE_URL}/auth/notifications/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 20. 获取诚信记录
    print("\n20. 获取诚信记录...")
    response = requests.get(f"{BASE_URL}/credit/records/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    print("\n" + "=" * 60)
    print("API测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
