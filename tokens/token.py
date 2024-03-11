from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tokens_data.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SECRET_KEY = 'your_secret_key'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    token = db.Column(db.String(500), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)


@app.route('/login', methods=['POST'])
def login():
    # Get user credentials from the request data
    user_data = request.json  # Assuming the request data is in JSON format
    user_id = user_data.get('user_id')
    email = user_data.get('email')

    if not user_id or not email:
        return jsonify({'message': 'User credentials are missing!'}), 400

    # Check if the user exists in the database
    existing_user = User.query.filter_by(user_id=user_id).first()

    if not existing_user:
        # If the user does not exist, create a new user in the database
        new_user = User(user_id=user_id, email=email)
        db.session.add(new_user)
        db.session.commit()
    else:
        new_user = existing_user

    token_payload = {
        'user_id': new_user.user_id,
        'email': new_user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    }

    token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

    # Save the token information in the database
    new_token = Token(user_id=new_user.user_id, token=token, expiration_date=token_payload['exp'])
    db.session.add(new_token)
    db.session.commit()

    return jsonify({'token': token})


@app.route('/protected', methods=['GET'])
def protected_route():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Authentication Token is missing!'}), 401

    try:
        decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=['HS256'])

        return jsonify({'message': 'You have access to the protected route!'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid Token!'}), 401


if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=8080)
