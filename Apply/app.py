import os

from flask import Flask, request, jsonify
import json
from bson import json_util
from pymongo import MongoClient
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate
from email.mime.base import MIMEBase

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/', tlsAllowInvalidCertificates=True)
db = client['jeet']
collection = db['apply_data']

# Zoho SMTP Configuration
SMTP_SERVER = 'smtppro.zoho.in'
SMTP_PORT = 587  # Zoho SMTP port
EMAIL_SENDER = 'jeet.j@buone.in'
EMAIL_PASSWORD = 'VefuHWi65vRd'


@app.route('/api/show_data', methods=['GET'])
def show_data():
    try:
        data = list(collection.find())
        json_data = json_util.dumps(data)
        return json_data, 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return jsonify({"message": "No data found"}), 404


@app.route('/api/store_data', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True, port=10)
