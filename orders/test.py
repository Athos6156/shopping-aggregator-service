import unittest
import json
from orders import order_app


class TestUserAPI(unittest.TestCase):

    def setUp(self):
        self.app = order_app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello World, I am the Orders Service, I will handle orders info!')

    def test_new_order(self):
        data = {
            'username': 'new_user',
            'status': 'new',
            'ship_num': 1,
        }
        response = self.app.post('/api/order/create/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'Order placed successfully'})

    def test_update_order(self):
        data = {
            'id': 1,
            'status': 'updating',
            'ship_num': 2,
        }
        response = self.app.put('/api/order/update/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'User updated successfully'})


if __name__ == '__main__':
    unittest.main()
