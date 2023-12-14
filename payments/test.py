import unittest
import json
from payments import app

class TestUserAPI(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()

	def test_hello_world(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data.decode('utf-8'), 'Hello World, I am the payments service. Wheres your money?!')

	def test_pay(self):
		data = {
			'payment_method': '4111111111111111',
			'order_id': 'test_order2',
			'amount': 437.00,
		}
		response = self.app.post('/api/payment/pay', data=json.dumps(data), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'paid successfully'})

	def test_pay2(self):
		data = {
			'payment_method': '4111111111111111',
			'order_id': 'test_order',
			'amount': 435.00,
		}
		response = self.app.post('/api/payment/pay', data=json.dumps(data), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'paid successfully'})


	def test_refund(self):
		data = {'order_id': 'test_order'}
		response = self.app.post('/api/payment/refund', data=json.dumps(data), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'Refunded'})


	def test_payment_find(self):
		data = {'order_id': 'test_order'}
		response = self.app.post('/api/payment/find', data=json.dumps(data), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(json.loads(response.data.decode('utf-8')), {'amount': 435,
																	 'id': 0,
																	 'order_id': 'test_order',
																	 'payment_method': '4111111111111111',
																	 'refunded': 1,
																	 'status': 1})


if __name__ == '__main__':
	unittest.main()
