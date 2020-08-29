import json
import datetime
from flask import Flask, make_response
from flask_restful import reqparse, abort, Api, Resource
from http import HTTPStatus

from models import Todo

DEBUG = False

app = Flask(__name__)
api = Api(app)


@app.route('/')
def hello_world():
    return 'Hello, World!'


parser = reqparse.RequestParser()
parser.add_argument('userId', default='tester') # Frontend 와 편의를 맞추기 위해 userId 의 기본값을 tester 로 함
parser.add_argument('title')
parser.add_argument('createdAt')


# Todo
# shows a single todo item and lets you delete a todo item
class TodoResource(Resource):
    def get(self, created_at):
        try:
            args = parser.parse_args()
            todo = Todo.get(args['userId'], created_at)
            return todo.attribute_values, HTTPStatus.OK
        except Todo.DoesNotExist:
            return 'Not found', HTTPStatus.NOT_FOUND

    def put(self, created_at):
        try:
            args = parser.parse_args()
            todo = Todo.get(args['userId'], created_at)
            todo.updatedAt = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            todo.title = args['title']
            todo.save()
            return 'updated', HTTPStatus.OK
        except Todo.DoesNotExist:
            return 'Not found', HTTPStatus.NOT_FOUND

    def delete(self, created_at):
        args = parser.parse_args()
        try:
            todo = Todo.get(args['userId'], created_at)
            todo.delete()
            return '', HTTPStatus.NO_CONTENT
        except Todo.DoesNotExist:
            return 'Not found', HTTPStatus.NOT_FOUND


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoListResource(Resource):
    def get(self):
        args = parser.parse_args()
        user_id = args.get('userId')
        todos = [todo.attribute_values for todo in Todo.query(user_id, rate_limit=500, scan_index_forward=False)]
        return todos, HTTPStatus.OK

    def post(self):
        args = parser.parse_args()
        args['createdAt'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        args['updatedAt'] = args['createdAt']

        todo = Todo(**args)
        todo.save()

        return todo.attribute_values, HTTPStatus.CREATED


# Actually setup the Api resource routing here
api.add_resource(TodoResource, '/todo/<string:created_at>')
api.add_resource(TodoListResource, '/todo/')


@api.representation('application/json')
def json_out(data, code, headers=None):
    resp = make_response(json.dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=DEBUG)
