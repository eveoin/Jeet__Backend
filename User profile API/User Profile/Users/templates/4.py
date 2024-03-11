from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from sqlalchemy import text
from uuid import UUID
import pyotp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
import uuid

app = Flask(__name__)

# Flask Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_data.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'etemp7354@gmail.com'
app.config['MAIL_PASSWORD'] = 'fomx muls ofkf egdk'
app.config['MAIL_DEFAULT_SENDER'] = 'etemp7354@gmail.com'

# Flask Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


def generate_random_secret():
    random_key = os.urandom(20)
    base32_encoded_key = base64.b32encode(random_key).decode('utf-8')
    return base32_encoded_key


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32())
    return totp.now()


def send_otp_email(email, otp):
    subject = 'OTP Verification'
    body = f'Your OTP for email verification: {otp}'
    msg = Message(subject, recipients=[email], body=body)

    try:
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bio = db.Column(db.String(200), nullable=True)
    date_of_birth = db.Column(db.String(10), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(16), nullable=True)


@app.route('/create-profile', methods=['POST'])
def create_profile():
    data = request.get_json()

    if 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Username and email are required'}), 400

    username = data['username']
    email = data['email']
    bio = data.get('bio', '')
    date_of_birth = data.get('date_of_birth', '')
    gender = data.get('gender', '')

    existing_user = UserProfile.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400

    # Generate OTP
    otp_secret = pyotp.random_base32()
    totp = pyotp.TOTP(otp_secret)
    otp = totp.now()

    new_profile = UserProfile(username=username, email=email, bio=bio, date_of_birth=date_of_birth, gender=gender,
                              otp_secret=otp_secret)
    db.session.add(new_profile)
    db.session.commit()

    # Send OTP via email
    send_otp_email(email, otp)

    return jsonify(
        {'message': 'User profile created successfully. OTP sent to your email.', 'user_id': str(new_profile.id)}), 201



@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400

    email = data['email']

    # Generate OTP
    otp_secret = generate_random_secret()
    totp = pyotp.TOTP(otp_secret)
    otp = totp.now()

    # Save the secret key and OTP for later verification
    user_profile = UserProfile.query.filter_by(email=email).first()
    if user_profile:
        user_profile.otp_secret = otp_secret
        db.session.commit()
    else:
        new_profile = UserProfile(email=email, otp_secret=otp_secret)
        db.session.add(new_profile)
        db.session.commit()

    # Send the OTP via email
    send_otp_email(email, otp)

    return jsonify({'message': 'OTP sent successfully'})


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    if 'email' not in data or 'otp' not in data:
        return jsonify({'error': 'Email and OTP are required'}), 400

    email = data['email']
    user_otp = data['otp']

    # Retrieve the saved secret key and OTP
    user_profile = UserProfile.query.filter_by(email=email).first()

    if not user_profile:
        return jsonify({'error': 'Email not found'}), 400

    secret = user_profile.otp_secret
    totp = pyotp.TOTP(secret)

    # Verify the OTP
    if totp.verify(user_otp):
        user_profile.is_verified = True
        db.session.commit()
        return jsonify({'message': 'OTP verification successful'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400


@app.route('/get-profile/<string:user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400

    query = text("SELECT * FROM user_profile WHERE user_profile.id = :user_uuid")
    user_profile = db.session.execute(query, {'user_uuid': str(user_uuid)}).fetchone()

    if user_profile:
        return jsonify({
            'username': user_profile.username,
            'email': user_profile.email,
            'bio': user_profile.bio,
            'date_of_birth': user_profile.date_of_birth,
            'gender': user_profile.gender
        })
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/update-profile/<string:user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400

    user_profile = UserProfile.query.get(str(user_uuid))

    if not user_profile:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    new_email = data.get('email', user_profile.email)
    if new_email != user_profile.email and UserProfile.query.filter_by(email=new_email).first():
        return jsonify({'error': 'Email already exists'}), 400

    user_profile.email = new_email
    user_profile.bio = data.get('bio', user_profile.bio)
    user_profile.date_of_birth = data.get('date_of_birth', user_profile.date_of_birth)
    user_profile.gender = data.get('gender', user_profile.gender)

    db.session.commit()

    return jsonify({'message': 'User profile updated successfully',
                    'username': user_profile.username,
                    'email': user_profile.email,
                    'bio': user_profile.bio,
                    'date_of_birth': user_profile.date_of_birth,
                    'gender': user_profile.gender}), 200


if __name__ == '__main__':
    app.run(debug=True, port=80)
