from flask import Flask, request, jsonify
from base64 import b64decode

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify(message='Hello, API!')

@app.errorhandler(404)
def not_found(error):
    return jsonify(message='Resource not found'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify(message='Internal server error'), 500

class AuthManager:
    def __init__(self):
        self.users = {'user': 'password'}
        self.user_objects = {'user': {'name': 'Jeet', 'role': 'user'}}

    def authenticate(self, username, password):
        return self.users.get(username) == password

    def get_user_object(self, username):
        return self.user_objects.get(username)

def no_auth_required(route_function):
    route_function.no_auth = True
    return route_function

@app.route('/public', methods=['GET'])
@no_auth_required
def public_route():
    return jsonify(message='Public data')

@app.before_request
def authenticate_request():
    if request.endpoint and not getattr(app.view_functions[request.endpoint], 'no_auth', False):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_type, auth_value = auth_header.split()
            if auth_type.lower() == 'basic':
                username, password = b64decode(auth_value).decode().split(':')
                if not AuthManager().authenticate(username, password):
                    return jsonify(message='Authentication failed'), 401
        else:
            return jsonify(message='Authentication required'), 401

@app.route('/profile', methods=['GET'])
def profile():
    user = AuthManager().get_user_object(request.authorization.username)
    if user:
        return jsonify(user), 200
    return jsonify(message='User not found'), 404

def encode_password(password):
    return password.replace(':', '_COLON_')

def decode_password(encoded_password):
    return encoded_password.replace('_COLON_', ':')
    username, encoded_password = b64decode(auth_value).decode().split(':')
    password = decode_password(encoded_password)
    if not AuthManager().authenticate(username, password):
        return jsonify(message='Authentication failed'), 401


if __name__ == '__main__':
    app.run(debug=True)
