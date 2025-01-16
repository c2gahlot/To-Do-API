from os import environ, path
from pathlib import Path
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import db, ToDo
import uuid
import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

current_file_path = Path(__file__).parent
dotenv_path = path.join(current_file_path, '.env')
load_dotenv(dotenv_path)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = environ["SQLALCHEMY_DATABASE_URI"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True if environ["SQLALCHEMY_TRACK_MODIFICATIONS"] == "True" else False
db.init_app(app)
with app.app_context():
    db.create_all()

# Configure logging
handler = TimedRotatingFileHandler('todo.log', when='midnight', interval=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Configure JWT
app.config['JWT_SECRET_KEY'] = environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)



# Middleware to log requests and responses with UUID
@app.before_request
def log_request_info():
    request_id = str(uuid.uuid4())
    request.environ['REQUEST_ID'] = request_id
    app.logger.info(f'Request ID: {request_id} - Request: {request.method} {request.url} - Body: {'' if not request.is_json else request.get_json()}')


@app.after_request
def log_response_info(response):
    request_id = request.environ.get('REQUEST_ID')
    app.logger.info(f'Request ID: {request_id} - Response: {response.status} - Body: {response.get_data(as_text=True)}')
    return response

class AuthAPI(MethodView):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Here you would normally verify username and password from your database.
        # For demonstration purposes, we'll assume a fixed username and password.
        if username != 'test' or password != 'test':
            return jsonify({"msg": "Bad username or password"}), 401

        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200


class TodoAPI(MethodView):

    @jwt_required()
    def get(self, todo_id=None):
        if not todo_id:
            todos = ToDo.query.all()
            return jsonify([{'id': todo.id, 'title': todo.title, 'complete': todo.complete} for todo in todos])
        else:
            todo = ToDo.query.get_or_404(todo_id)
            return jsonify({'id': todo.id, 'title': todo.title, 'complete': todo.complete})

    @jwt_required()
    def post(self):
        data = request.get_json()
        todo = ToDo(title=data.get('title'))
        db.session.add(todo)
        db.session.commit()
        return jsonify({'id': todo.id}), 201

    @jwt_required()
    def put(self, todo_id):
        data = request.get_json()
        todo = ToDo.query.get_or_404(todo_id)
        todo.title = data.get('title', todo.title)
        todo.complete = data.get('complete', todo.complete)
        db.session.commit()
        return jsonify({'id': todo.id})

    @jwt_required()
    def delete(self, todo_id):
        todo = ToDo.query.get_or_404(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return '', 204


app.add_url_rule('/login/', view_func=AuthAPI.as_view('auth_api'))
app.add_url_rule('/todos/', view_func=TodoAPI.as_view('todo_api'))
app.add_url_rule('/todos/<int:todo_id>', view_func=TodoAPI.as_view('todo_api_with_id'))

if __name__ == "__main__":
    app.run(debug=True)
