import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    # Email configuration
    sender_email = 'etemp7354@gmail.com'
    receiver_email = 'etemp7354@gmail.com'
    app_password = 'fomx muls ofkf egdk'

    # Message configuration
    subject = 'Test Email'
    body = 'This is a test email sent from Python.'

    # Create the MIMEText object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach body to the message
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Start TLS for security
        server.starttls()

        # Login with your Gmail account
        server.login(sender_email, app_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print("Test email sent successfully!")

# Call the function to send the test email
send_test_email()
