from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid
import hashlib
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SECRET_KEY = "secretary"
TOKEN_EXPIRATION_SECONDS = 300

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(64), nullable=True)
    token_expiration = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"

with app.app_context():
    db.create_all()

def generate_token(username):
    token_data = username + SECRET_KEY
    token = hashlib.sha256(token_data.encode()).hexdigest()
    return token

def is_token_valid(token):
    return token in User.query.filter_by(token=token).all() and User.query.filter_by(token=token).first().token_expiration > time.time()

def generate_reset_token(username):
    reset_token = str(uuid.uuid4())
    return reset_token

@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()

    if 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    username = data['username']
    password = data['password']
    email = data['email']

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User signed up successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(username)
    user.token = token
    user.token_expiration = time.time() + TOKEN_EXPIRATION_SECONDS

    db.session.commit()

    return jsonify({'token': token}), 200

@app.route('/verify', methods=['POST'])
def verify_token():
    data = request.get_json()

    if 'token' not in data:
        return jsonify({'error': 'Token is required'}), 400

    token = data['token']

    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    if is_token_valid(token):
        return jsonify({'message': 'Token is valid'}), 200
    else:
        return jsonify({'error': 'Invalid token'}), 401

# The rest of your code...

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400

    email = data['email']

    username = next((user for user, data in users.items() if data['email'] == email), None)

    if username:
        reset_token = generate_reset_token(username)
        reset_tokens[reset_token] = username

        # Send the reset token to the user via email (in a real-world scenario)

        return jsonify({'message': 'Reset token generated successfully'}), 200
    else:
        return jsonify({'error': 'Email not found'}), 404


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()

    if 'token' not in data or 'new_password' not in data:
        return jsonify({'error': 'Token and new_password are required'}), 400

    reset_token = data['token']
    new_password = data['new_password']

    username = reset_tokens.get(reset_token)

    if username:
        users[username]['password'] = new_password

        # Remove the reset token from the dictionary (optional)
        del reset_tokens[reset_token]

        return jsonify({'message': 'Password reset successfully'}), 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401


if __name__ == '__main__':
    app.run(debug=True, port=808)
