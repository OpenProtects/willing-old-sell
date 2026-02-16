import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.admin_token = None
        self.admin_id = None
        self.goods_id = None
        self.category_id = None
        self.wishlist_id = None
        self.order_id = None
        self.chat_room_id = None
        self.report_id = None
        
    def print_result(self, name, response):
        print(f"\n{'='*50}")
        print(f"测试: {name}")
        print(f"状态码: {response.status_code}")
        try:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"响应: {response.text}")
        print(f"{'='*50}")
        return response
    
    def test_register(self):
        print("\n\n" + "="*60)
        print("用户注册测试")
        print("="*60)
        
        response = requests.post(f"{BASE_URL}/auth/register/", json={
            "username": "testuser2",
            "password": "test123456",
            "password_confirm": "test123456",
            "phone": "13800138003",
            "email": "test2@example.com"
        })
        self.print_result("注册普通用户", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('code') == 200:
                self.token = data['data']['token']['access']
                self.user_id = data['data']['user']['id']
                return True
        return False
    
    def test_register_admin(self):
        response = requests.post(f"{BASE_URL}/auth/register/", json={
            "username": "buyer_user",
            "password": "buyer123456",
            "password_confirm": "buyer123456",
            "phone": "13800138004",
            "email": "buyer@example.com"
        })
        self.print_result("注册买家用户", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('code') == 200:
                self.admin_token = data['data']['token']['access']
                self.admin_id = data['data']['user']['id']
                return True
        return False
    
    def test_login(self):
        print("\n\n" + "="*60)
        print("用户登录测试")
        print("="*60)
        
        response = requests.post(f"{BASE_URL}/auth/login/", json={
            "username": "testuser2",
            "password": "test123456"
        })
        self.print_result("登录普通用户", response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                self.token = data['data']['token']['access']
                return True
        return False
    
    def test_get_user_info(self):
        print("\n\n" + "="*60)
        print("用户信息测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/auth/users/", headers=headers)
        self.print_result("获取用户信息", response)
        
    def test_verify_realname(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/auth/users/verify_realname/", 
            headers=headers,
            json={
                "real_name": "测试用户",
                "id_card": "110101199001011234",
                "school_id": "2021001"
            }
        )
        self.print_result("实名认证-卖家", response)
        
    def test_verify_realname_buyer(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(f"{BASE_URL}/auth/users/verify_realname/", 
            headers=headers,
            json={
                "real_name": "买家用户",
                "id_card": "110101199001015678",
                "school_id": "2021002"
            }
        )
        self.print_result("实名认证-买家", response)
        
    def test_create_category(self):
        print("\n\n" + "="*60)
        print("品类测试")
        print("="*60)
        
        from goods.models import Category
        category, created = Category.objects.get_or_create(
            name="教材",
            defaults={"description": "各类教材书籍"}
        )
        self.category_id = category.id
        print(f"品类ID: {self.category_id}")
        
    def test_create_goods(self):
        print("\n\n" + "="*60)
        print("闲置物品测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/goods/goods/", 
            headers=headers,
            json={
                "name": "高等数学教材",
                "category": self.category_id,
                "description": "九成新高等数学教材，有少量笔记",
                "price": 25.00,
                "condition": "good",
                "images": [],
                "pickup_location": "图书馆门口"
            }
        )
        self.print_result("发布闲置物品", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('code') == 200:
                self.goods_id = data['data']['id']
                return True
        return False
    
    def test_list_goods(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/goods/goods/", headers=headers)
        self.print_result("获取物品列表", response)
        
    def test_search_goods(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/goods/goods/?keyword=数学", headers=headers)
        self.print_result("搜索物品", response)
        
    def test_get_goods_detail(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/goods/goods/{self.goods_id}/", headers=headers)
        self.print_result("获取物品详情", response)
        
    def test_create_wishlist(self):
        print("\n\n" + "="*60)
        print("心愿单测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(f"{BASE_URL}/wishlist/wishlists/", 
            headers=headers,
            json={
                "name": "高等数学",
                "category": self.category_id,
                "min_price": 10,
                "max_price": 50,
                "description": "需要高等数学教材，八成新以上"
            }
        )
        self.print_result("创建心愿单", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('code') == 200:
                self.wishlist_id = data['data']['wishlist']['id']
                return True
        return False
    
    def test_list_wishlists(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{BASE_URL}/wishlist/wishlists/", headers=headers)
        self.print_result("获取心愿单列表", response)
        
    def test_get_match_results(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{BASE_URL}/wishlist/wishlists/{self.wishlist_id}/match_results/", headers=headers)
        self.print_result("获取匹配结果", response)
        
    def test_create_order(self):
        print("\n\n" + "="*60)
        print("订单测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(f"{BASE_URL}/orders/orders/", 
            headers=headers,
            json={"goods_id": self.goods_id}
        )
        self.print_result("创建订单", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('code') == 200:
                self.order_id = data['data']['id']
                return True
        return False
    
    def test_pay_order(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(f"{BASE_URL}/orders/orders/{self.order_id}/pay/", headers=headers)
        self.print_result("模拟支付", response)
        
    def test_confirm_order(self):
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(f"{BASE_URL}/orders/orders/{self.order_id}/confirm/", headers=headers)
        self.print_result("确认收货", response)
        
    def test_create_evaluation(self):
        print("\n\n" + "="*60)
        print("评价测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.post(f"{BASE_URL}/orders/evaluations/", 
            headers=headers,
            json={
                "order": self.order_id,
                "rating": "good",
                "content": "物品很好，卖家很诚信"
            }
        )
        self.print_result("创建评价", response)
        
    def test_send_message(self):
        print("\n\n" + "="*60)
        print("聊天测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/chat/rooms/send_message/", 
            headers=headers,
            json={
                "receiver_id": self.admin_id,
                "content": "你好，请问物品还在吗？",
                "goods_id": self.goods_id,
                "goods_name": "高等数学教材"
            }
        )
        self.print_result("发送消息", response)
        
    def test_list_chat_rooms(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/chat/rooms/", headers=headers)
        self.print_result("获取聊天室列表", response)
        
    def test_create_report(self):
        print("\n\n" + "="*60)
        print("举报测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/report/reports/", 
            headers=headers,
            json={
                "reported_user": self.admin_id,
                "report_type": "other",
                "description": "测试举报",
                "evidence": []
            }
        )
        self.print_result("创建举报", response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('code') == 200:
                self.report_id = data['data']['id']
                return True
        return False
    
    def test_get_notifications(self):
        print("\n\n" + "="*60)
        print("通知测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/auth/notifications/", headers=headers)
        self.print_result("获取通知列表", response)
        
    def test_get_credit_records(self):
        print("\n\n" + "="*60)
        print("诚信值测试")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/credit/records/", headers=headers)
        self.print_result("获取诚信值记录", response)
        
    def run_all_tests(self):
        print("\n" + "#"*70)
        print("# 开始API测试")
        print("#"*70)
        
        self.test_register()
        self.test_register_admin()
        self.test_login()
        self.test_get_user_info()
        self.test_verify_realname()
        self.test_verify_realname_buyer()
        
        self.test_create_category()
        self.test_create_goods()
        self.test_list_goods()
        self.test_search_goods()
        self.test_get_goods_detail()
        
        self.test_create_wishlist()
        self.test_list_wishlists()
        self.test_get_match_results()
        
        self.test_create_order()
        self.test_pay_order()
        self.test_confirm_order()
        self.test_create_evaluation()
        
        self.test_send_message()
        self.test_list_chat_rooms()
        
        self.test_create_report()
        self.test_get_notifications()
        self.test_get_credit_records()
        
        print("\n" + "#"*70)
        print("# 测试完成!")
        print("#"*70)


if __name__ == "__main__":
    import django
    import os
    import sys
    
    sys.path.insert(0, '/Users/blackfruithouse/Documents/willing-manage')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    tester = APITester()
    tester.run_all_tests()
