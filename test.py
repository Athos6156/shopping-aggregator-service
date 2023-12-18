import unittest
import json
from aggregator_service import aggregator_app


class TestUserAPI(unittest.TestCase):

    def setUp(self):
        self.app = aggregator_app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'),
                         'Hello World, I am the Aggregator Service, I will aggregate your requests!')

    def test_register_order_pay(self):
        data = {
            'user': {
                'Customer_ID': 'new1',
                'username': 'new1',
                'password': 'new2',
                'first_name': 'John',
                'last_name': 'Doe',
                'address': '520 Madison Ave, NY, NY',
                'phone': '555-1234',
                'gender': 'male'
            },
            'order': {
                "Customer_ID": "testuser1",  # PK
                "Order_Date": "2023-12-01",  # PK
                "required_Date": "2023-12-01",
                "Shipping_Date": "2023-12-01",
                "Status_": "Order Created",
                "Comments": "gggg",
                "Order_Num": "12345",
                "Payment_Amount": "1000"
            },
            'payment': {
                'payment_method': '4111111111111111',
                'order_id': "12345",
                'amount': 437.00
            }
        }

        response = self.app.post('/api/aggregate/register_order_pay', data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {
            'message': 'User Service: User with this username already exists; New Order API: Order Service: Order placed successfully; Payment Service: paid successfully.'})

    def test_order_pay(self):
        data = {
            'order': {
                "Customer_ID": "testuser1",  # PK
                "Order_Date": "2023-12-01",  # PK
                "required_Date": "2023-12-01",
                "Shipping_Date": "2023-12-01",
                "Status_": "Order Created",
                "Comments": "gggg",
                "Order_Num": "12345",
                "Payment_Amount": "1000"
            },
            'payment': {
                'payment_method': '4111111111111111',
                'order_id': "test_order",
                'amount': 437.00
            }
        }

        response = self.app.post('/api/aggregate/order_pay', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')),
                         {
                             'message': 'Order Service: New Order API: Order already exists; Payment Service: paid successfully'})

    def test_order_async_pay(self):
        data = {
            'order': {
                "Customer_ID": "testuser1",  # PK
                "Order_Date": "2023-12-01",  # PK
                "required_Date": "2023-12-01",
                "Shipping_Date": "2023-12-01",
                "Status_": "Order Created",
                "Comments": "gggg",
                "Order_Num": "test_order",
                "Payment_Amount": "1000"
            },
            'payment': {
                'payment_method': '4111111111111111',
                'order_id': "test_order",
                'amount': 437.00
            }
        }

        response = self.app.post('/api/aggregate/order_pay_async', data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')),
                         {'message': 'Order Service: New Order API: Order placed successfully; Payment Service: paid '
                                     'successfully'})

    def test_delete_refund(self):
        data = {
            'order': {
                "Customer_ID": "testuser1",  # PK
                "Order_Date": "2023-12-01",  # PK
                "required_Date": "2023-12-01",
                "Shipping_Date": "2023-12-01",
                "Status_": "Shipping",
                "Comments": "out of stock",
                "Order_Num": "12345",
                "Payment_Amount": "1000"
            },
            'payment': {
                'payment_method': '4111111111111111',
                'order_id': "test_order",
                'amount': 437.00
            }
        }

        response = self.app.post('/api/aggregate/delete_refund', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')),
                         {
                             'message': 'Order Service: Delete Order API: Order deleted successfully; Payment '
                                        'Service: Refunded'})


if __name__ == '__main__':
    unittest.main()
