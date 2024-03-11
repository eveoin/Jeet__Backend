from flask import Flask, request, jsonify
import uuid
import hashlib
import time

app = Flask(__name__)

users = {}
tokens = {}  # Store token and expiration timestamp
verified_tokens = set()  # Set to keep track of verified tokens

SECRET_KEY = "secretary"
TOKEN_EXPIRATION_SECONDS = 60  # Set expiration time to 1 minute

def generate_token(username):
    token_data = username + SECRET_KEY
    token = hashlib.sha256(token_data.encode()).hexdigest()
    tokens[token] = time.time() + TOKEN_EXPIRATION_SECONDS  # Set expiration timestamp
    return token

def is_token_valid(token):
    return token in tokens and tokens[token] > time.time()

@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']

    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    users[username] = {'password': password}

    return jsonify({'message': 'User signed up successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']

    if username not in users or users[username]['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(username)
    return jsonify({'token': token}), 200


@app.route('/verify', methods=['POST'])
def verify_token():
    data = request.get_json()

    if 'token' not in data:
        return jsonify({'error': 'Token is required'}), 400

    token = data['token']

    if token in verified_tokens:
        return jsonify({'message': 'Token has already been verified'}), 200

    for username, user_data in users.items():
        if generate_token(username) == token and is_token_valid(token):
            password = user_data['password']

            with open('token_verify.txt', 'a') as file:
                file.write(f"User Name: {username},\nPassword: {password}, \nToken: {token}, \nExpiration Time: {tokens[token]}\n\n\n")

            verified_tokens.add(token)

            return jsonify({'message': 'Token is valid'}), 200

    return jsonify({'error': 'Invalid token or expired token'}), 401

def get_username_from_token(token):
    return token[:10]

if __name__ == '__main__':
    app.run(debug=True)
