import os
import secrets
import smtplib
import random
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
#from random import random
from urllib.parse import urljoin

import requests
from flask import Flask, request, jsonify, session, redirect, abort
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect, generate_csrf
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pymongo import MongoClient
from pip._vendor import cachecontrol

app = Flask(__name__)
app.config['SECRET_KEY'] = '2WFMFM2ZaosK4p'  # make sure this matches what's in client_secret1.json
app.config['JWT_SECRET_KEY'] = 'dc6f8cf55952d4550b2a54a1a79b6398'

client = MongoClient('mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/',
                     tlsAllowInvalidCertificates=True)
db = client['info']
jwt = JWTManager(app)
csrf = CSRFProtect(app)

otp = random.randint(1000, 9999)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "644210233864-vati2ld0o4mtem9gtf55lglsk02m0vff.apps.googleusercontent.com"
client_secrets_file = os.path.join(os.path.dirname(__file__), "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:80/callback"
)


def login_is_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function(*args, **kwargs)

    return wrapper


def send_otp_email(receiver_email, subject, body, otp):
    # Zoho Mail SMTP Configuration
    smtp_server = 'smtppro.zoho.in'
    smtp_port = 587
    smtp_username = 'jeet.j@buone.in'
    smtp_password = 'atEFF0UMQ4mx'

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    server.login(smtp_username, smtp_password)

    server.sendmail(smtp_username, receiver_email, msg.as_string())

    server.quit()


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


def generate_reset_token(username):
    pass


@app.route('/api/signup', methods=['POST'])
@csrf.exempt
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    mobile = data.get('mobile')
    email = data.get('email')
    gender = data.get('gender')

    if password != confirm_password:
        return jsonify({"error": "Password and confirm password do not match"}), 400

    if username and password and first_name and last_name and email and mobile and gender:
        existing_user = db.users.find_one({'username': username})

        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        new_user = {
            'username': username,
            'password': password,
            'confirm_password': confirm_password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'mobile': mobile,
            'gender': gender,
            'otp': None
        }

        db.users.insert_one(new_user)

        welcome_subject = 'Welcome to EVEO'
        welcome_message = f'Hello {first_name} {last_name},\n\nWelcome to EVEO'
        send_otp_email(email, welcome_subject, welcome_message, otp=None)

        reset_token = generate_reset_token(username)

        email_data = {
            'to_email': email,
            'subject': 'Password Reset Instructions',
            'message': f'Click the following link to reset your password: http://your-reset-url/    {reset_token}'
        }

        csrf_token = generate_csrf()

        response = jsonify({"message": "Signup successful"})
        response.headers["X-CSRF-TOKEN"] = csrf_token
        return response, 200
    else:
        return jsonify({"error": "Username, password, email, mobile, and gender are required"}), 400


@app.route('/api/login', methods=['POST'])
@csrf.exempt
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    existing_user = db.users.find_one({'username': username, 'password': password})

    if existing_user:
        otp = random.randint(1000, 9999)
        db.users.update_one({'username': username}, {'$set': {'otp': otp}})

        subject = 'Your OTP for User Profile Management'
        body = f'Your OTP is: {otp}'

        send_otp_email(existing_user['email'], subject, body, otp)

        return jsonify({"message": "Login successful. OTP generated and sent via email"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/api/verify_otp', methods=['POST'])
@csrf.exempt
def verify_otp():
    data = request.json
    username = data.get('username')
    otp_attempt = data.get('otp')

    existing_user = db.users.find_one({'username': username, 'otp': int(otp_attempt)})

    if existing_user:
        db.users.update_one({'username': username}, {'$set': {'otp': None}})
        return jsonify({"message": "OTP verification successful"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401


@app.route('/api/get_profile/<username>', methods=['GET'])
@csrf.exempt
def get_profile(username):
    existing_user = db.users.find_one({'username': username})

    if existing_user:
        user_profile = {
            'username': existing_user['username'],
            'password': existing_user['password'],
            'first_name': existing_user['first_name'],
            'last_name': existing_user['last_name'],
            'email': existing_user['email'],
            'mobile': existing_user['mobile'],
            'gender': existing_user['gender']
        }
        return jsonify(user_profile), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/api/update_profile/<username>', methods=['PUT'])
@csrf.exempt
def update_profile(username):
    data = request.json

    existing_user = db.users.find_one({'username': username})

    if existing_user:
        update_data = {
            'password': data.get('password', existing_user['password']),
            'first_name': data.get('first_name', existing_user['first_name']),
            'last_name': data.get('last_name', existing_user['last_name']),
            'email': data.get('email', existing_user['email']),
            'mobile': data.get('mobile', existing_user['mobile']),
            'gender': data.get('gender', existing_user['gender']),
        }

        db.users.update_one({'username': username}, {'$set': update_data})

        return jsonify({"message": "Profile updated successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/api/forgot_password', methods=['POST'])
@csrf.exempt
def forgot_password():
    data = request.json
    username = data.get('username')

    user = db.users.find_one({'username': username})

    if user:
        reset_token = secrets.token_urlsafe(16)

        new_reset_token = {
            'user_username': user['username'],
            'token': reset_token
        }

        db.reset_tokens.insert_one(new_reset_token)

        subject = 'Password Reset Instructions'
        body = f'Your reset token is:   {reset_token}'
        send_otp_email(user['email'], subject, body, otp=None)

        return jsonify({"message": "Password reset instructions sent"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/api/reset_password', methods=['POST'])
@csrf.exempt
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    if not token:
        return jsonify({"error": "Reset token not provided"}), 400

    reset_token = db.reset_tokens.find_one({'token': token})

    if reset_token:
        user = db.users.find_one({'username': reset_token['user_username']})

        if user:
            db.users.update_one({'username': user['username']}, {'$set': {'password': new_password}})
            db.reset_tokens.delete_one({'token': token})

            return jsonify({"message": "Password reset successful"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"error": "Invalid or expired reset token"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=80)

