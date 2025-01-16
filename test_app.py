import unittest
import json
from app import app, db
from flask_jwt_extended import create_access_token


class TodoAPITestCase(unittest.TestCase):
    def setUp(self):
        # Set up a test client and a temporary database
        self.app = app.test_client()
        self.app.testing = True
        self.secret_key = 'NORX6ELnPbzOYuMj'

        # Create a temporary database for testing
        with app.app_context():
            db.create_all()
            self.token = create_access_token(identity='test')

    def tearDown(self):
        # Clean up after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_todo(self):
        response = self.app.post('/todos/',
                                 data=json.dumps({'title': 'Test Todo'}),
                                 headers={'Authorization': f'Bearer {self.token}'},
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', json.loads(response.data))

    def test_get_todos(self):
        # First create a todo item
        self.app.post('/todos/',
                      data=json.dumps({'title': 'Test Todo'}),
                      headers={'Authorization': f'Bearer {self.token}'},
                      content_type='application/json')

        response = self.app.get('/todos/', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        todos = json.loads(response.data)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]['title'], 'Test Todo')

    def test_get_todo_by_id(self):
        # Create a todo item first
        response = self.app.post('/todos/',
                                 data=json.dumps({'title': 'Test Todo'}),
                                 headers={'Authorization': f'Bearer {self.token}'},
                                 content_type='application/json')
        todo_id = json.loads(response.data)['id']

        response = self.app.get(f'/todos/{todo_id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        todo = json.loads(response.data)
        self.assertEqual(todo['title'], 'Test Todo')

    def test_update_todo(self):
        # Create a todo item first
        response = self.app.post('/todos/',
                                 data=json.dumps({'title': 'Test Todo'}),
                                 headers={'Authorization': f'Bearer {self.token}'},
                                 content_type='application/json')
        todo_id = json.loads(response.data)['id']

        response = self.app.put(f'/todos/{todo_id}',
                                data=json.dumps({'title': 'Updated Todo', 'complete': True}),
                                headers={'Authorization': f'Bearer {self.token}'},
                                content_type='application/json')

        self.assertEqual(response.status_code, 200)

        # Verify the update
        response = self.app.get(f'/todos/{todo_id}', headers={'Authorization': f'Bearer {self.token}'})
        updated_todo = json.loads(response.data)
        self.assertEqual(updated_todo['title'], 'Updated Todo')
        self.assertTrue(updated_todo['complete'])

    def test_delete_todo(self):
        # Create a todo item first
        response = self.app.post('/todos/',
                                 data=json.dumps({'title': 'Test Todo'}),
                                 headers={'Authorization': f'Bearer {self.token}'},
                                 content_type='application/json')
        todo_id = json.loads(response.data)['id']

        response = self.app.delete(f'/todos/{todo_id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 204)

        # Verify deletion
        response = self.app.get(f'/todos/{todo_id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 404)  # Should return 404 after deletion


if __name__ == '__main__':
    unittest.main()