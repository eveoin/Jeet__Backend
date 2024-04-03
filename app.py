import json
import os
import random
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
import secrets
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
import razorpay
from bson import json_util
from flask_cors import CORS
from tabulate import tabulate
from wtforms import csrf

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Database connection
mongo_client = MongoClient('mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/',
                           tlsAllowInvalidCertificates=True)
db_apply_data = mongo_client['jeet']['apply_data']
db_info = mongo_client['info']

# SMTP configurations
SMTP_SERVER = 'smtppro.zoho.in'
SMTP_PORT = 587  # Zoho SMTP port
EMAIL_SENDER = 'jeet.j@buone.in'
EMAIL_PASSWORD = 'VefuHWi65vRd'

# Razorpay client
razorpay_client = razorpay.Client(auth=("rzp_test_BqwXmtR5v1PWNh", "NnS89KiZoIfLw6briAZOnEje"))

# CSRF protection
csrf = CSRFProtect(app)

# Google OAuth2 configurations
GOOGLE_CLIENT_ID = "644210233864-vati2ld0o4mtem9gtf55lglsk02m0vff.apps.googleusercontent.com"
client_secrets_file = os.path.join(os.path.dirname(__file__), "client_secret.json")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:443/callback"
)


def login_is_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function(*args, **kwargs)

    return wrapper


@app.route('/')
def index():
    return "Hello World"


# Routes related to job applications
@app.route('/api/show_data', methods=['GET'])
def show_data():
    try:
        data = list(db_apply_data.find())
        json_data = json_util.dumps(data)
        return json_data, 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return jsonify({"message": "No data found"}), 404


@app.route('/api/store_data', methods=['POST'])
@csrf.exempt
def store_data():
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    mobile = request.form.get('phoneNumber')
    email = request.form.get('email')
    job_title = request.form.get('jobTitle')
    gender = request.form.get('gender')

    if not all([first_name, last_name, mobile, email, job_title, gender]):
        return jsonify({"error": "All fields are required"}), 400

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
    db_apply_data.insert_one(job_data)

    send_email_notification(first_name, last_name, email, job_title, mobile, gender)

    return jsonify({"message": "Data stored successfully"}), 200


def send_email_notification(first_name, last_name, email, job_title, mobile, gender):
    message = MIMEMultipart()
    message['From'] = EMAIL_SENDER
    message['To'] = 'etemp7354@gmail.com'  # Replace with recipient email
    message['Subject'] = 'New Job Application'

    table_data = [
        ["First Name:", first_name],
        ["Last Name:", last_name],
        ["Email:", email],
        ["Job Title:", job_title],
        ["Phone Number:", mobile],
        ["Gender:", gender]
    ]
    table = tabulate(table_data, tablefmt="html")

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

    with open(f'resumes/{first_name}_{last_name}_resume.pdf', 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    part.add_header('Content-Disposition', f'attachment; filename={first_name}_{last_name}_resume.pdf')
    message.attach(part)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)

    server.send_message(message)

    server.quit()

    os.remove(f'resumes/{first_name}_{last_name}_resume.pdf')


# Authentication routes
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
    credentials = flow.credentials
    request_session = requests.session()
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=request_session,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
