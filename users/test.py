import unittest
import json
from users import user_app

class TestUserAPI(unittest.TestCase):

    def setUp(self):
        self.app = user_app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello World, I am the Users Service, I will handle users info!')

    def test_user_create(self):
        data = {
            'username': 'new1',
            'password': 'new2',
            'first_name': 'John',
            'last_name': 'Doe',
            'address': '123 Main St',
            'phone': '555-1234',
            'gender': 'male'
        }
        response = self.app.post('/api/user/create/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'User created successfully'})

    def test_user_login(self):
        data = {'username': 'new1', 'password': 'new2'}
        response = self.app.post('/api/user/login/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'Login failed'})


    def test_user_update(self):
        data = {'username': 'testuser', 'new_password': 'newpassword'}
        response = self.app.put('/api/user/update/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'User not found'})

    def test_user_delete(self):
        data = {'username': 'existinguser'}
        response = self.app.delete('/api/user/delete/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8')), {'message': 'User not found'})

if __name__ == '__main__':
    unittest.main()
