from flask import Flask, redirect, url_for, session, request
import requests

app = Flask(__name__)
app.secret_key = "yoursecret"

@app.route('/')
def index():
    return 'Welcome to Flask Facebook Login!'

@app.route('/login')
def login():
    return redirect('https://www.facebook.com/v12.0/dialog/oauth?client_id=your_app_id&redirect_uri=http://localhost:5000/callback')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    response = requests.get('https://graph.facebook.com/v12.0/oauth/access_token', params={
        'client_id': '454141691833905',
        'redirect_uri': 'http://localhost:5000/callback',
        'client_secret': '3e9ac1ca794079537db2166fe7331fa1',
        'code': code
    })
    access_token = response.json()['access_token']
    session['access_token'] = access_token
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    response = requests.get('https://graph.facebook.com/me', params={
        'access_token': access_token,
        'fields': 'id,name,email'
    })
    user_data = response.json()
    return f"Hello, {user_data['name']}! Your email is: {user_data['email']}"

if __name__ == '__main__':
    app.run(debug=True)
