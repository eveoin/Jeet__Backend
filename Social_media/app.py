from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.contrib.client import OAuth

#from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.secret_key = 'appsecreate'

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='709129487030-tn0sb0j1n4s42lnjuq3tdphj6ko0qikc.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def index():
    return 'Welcome to the Google Social Media Authentication Example'

@app.route('/login')
def login():
    return google.authorize(login=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={}, error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')
    return jsonify(user_info.data)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)
