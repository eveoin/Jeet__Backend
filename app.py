import json
import os
import random
import secrets
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import razorpay
from bson import json_util
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_wtf.csrf import generate_csrf, CSRFProtect
from pymongo import MongoClient
from tabulate import tabulate
from wtforms import csrf

app = Flask(__name__)
CORS(app)

client1 = MongoClient('mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/', tlsAllowInvalidCertificates=True)
db = client1['jeet']
collection = db['apply_data']

client2 = MongoClient('mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/', tlsAllowInvalidCertificates=True)
db = client2['info']



SMTP_SERVER = 'smtppro.zoho.in'
SMTP_PORT = 587  # Zoho SMTP port
EMAIL_SENDER = 'jeet.j@buone.in'
EMAIL_PASSWORD = 'VefuHWi65vRd'


client = razorpay.Client(auth=("rzp_test_BqwXmtR5v1PWNh", "NnS89KiZoIfLw6briAZOnEje"))

data_file_path = 'data.json'

app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_SECRET_KEY'] = 'dc6f8cf55952d4550b2a54a1a79b6398'

csrf = CSRFProtect(app)


# Initialize waiting_list as an empty list
waiting_list = []

# Check if the file exists and is not empty
if os.path.exists(data_file_path) and os.path.getsize(data_file_path) > 0:
    # Load existing data from the JSON file
    with open(data_file_path, 'r') as json_file:
        loaded_data = json.load(json_file)

        # Ensure the loaded data is a list
        if isinstance(loaded_data, list):
            waiting_list = loaded_data


def send_email_notification(first_name, last_name, email, job_title, gender):
    # Prepare email message
    message = MIMEMultipart()
    message['From'] = EMAIL_SENDER
    message['To'] = 'etemp7354@gmail.com'  # Replace with recipient email
    message['Subject'] = 'New Job Application'

    # Create table with job application data
    table_data = [
        ["First Name:", first_name],
        ["Last Name:", last_name],
        ["Email:", email],
        ["Job Title:", job_title],
        ["Gender:", gender]
    ]
    table = tabulate(table_data, tablefmt="html")

    # Email body
    body = f"""
    <html>
    <head></head>
    <body>
        <h2>New job application received:</h2>
        {table}
    </body>
    </html>
    """
    message.attach(MIMEText(body, 'html'))

    # Attach resume file
    with open(f'resumes/{first_name}_{last_name}_resume.pdf', 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    part.add_header('Content-Disposition', f'attachment; filename={first_name}_{last_name}_resume.pdf')
    message.attach(part)

    # Connect to Zoho SMTP server
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)

    # Send email
    server.send_message(message)

    # Quit SMTP server
    server.quit()

    os.remove(f'resumes/{first_name}_{last_name}_resume.pdf')



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

def generate_reset_token(username):
    reset_token = secrets.token_urlsafe(16)
    db.reset_tokens.insert_one({'user_username': username, 'token': reset_token})
    return reset_token


def send_reset_email(receiver_email, reset_token):
    subject = 'Password Reset Instructions'
    body = f'Click the following link to reset your password: http://your-reset-url/    {reset_token}'
    send_otp_email(receiver_email, subject, body, otp=None)

@app.route('/api/show_data', methods=['GET'])
def show_data():
    try:
        data = list(collection.find())
        json_data = json_util.dumps(data)
        return json_data, 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return jsonify({"message": "No data found"}), 404

@app.route('/api/store_data', methods=['POST'])
@csrf.exempt
def store_data():
    # Get form data
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')

    # Check if first_name and last_name are provided
    if first_name is None or last_name is None:
        return jsonify({"error": "First name and last name are required"}), 400


    mobile = request.form.get('phoneNumber')
    email = request.form.get('email')
    job_title = request.form.get('jobTitle')
    gender = request.form.get('gender')

    # Save resume file
    resume = request.files.get('resume')

    if resume:
        resume.save(f'resumes/{first_name}_{last_name}_resume.pdf')

    job_data = {
        "firstName": first_name,
        "lastName": last_name,
        "phoneNumber": mobile,
        "email": email,
        "jobTitle": job_title,
        "gender": gender
    }
    collection.insert_one(job_data)

    # Send email notification
    send_email_notification(first_name, last_name, email, job_title, gender)

    return jsonify({"message": "Data stored successfully"}), 200




@app.route('/api/count', methods=['GET'])
def get_waiting_list():
    return jsonify({'count': len(waiting_list)})


@app.route('/api', methods=['POST'])
@csrf.exempt
def add_to_waiting_list():
    data = request.get_json()


    if 'Email' not in data:
        return jsonify({'error': 'Invalid data format'}), 400

    waiting_list.append({
        'Email': data['Email'],
        # 'paymentId': data['paymentId']
    })

    # Save the updated data back to the JSON file
    with open(data_file_path, 'w') as json_file:
        json.dump(waiting_list, json_file, indent=2)
    return jsonify({})



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

        welcome_subject = 'Welcome to Our Service!'
        welcome_message = f'Hello {first_name} {last_name},\n\nWelcome to our service!'
        send_otp_email(email, welcome_subject, welcome_message, otp=None)

        reset_token = generate_reset_token(username)

        email_data = {
            'to_email': email,
            'subject': 'Password Reset Instructions',
            'message': f'Click the following link to reset your password: http://your-reset-url/    {reset_token}'
        }
        #requests.post('http://localhost:5000/send_email', json=email_data)

        csrf_token = generate_csrf()

        response = jsonify({"message": "Signup successful"})
        response.headers["X-CSRF-TOKEN"] = csrf_token
        return response, 200

    else:
        return jsonify({"error": "Username, password, email, mobile, and gender are required"}), 400


@app.route('/api/login', methods=['POST'])
@csrf.exempt
def login():
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
    app.run(debug=True, host='0.0.0.0', port=443)