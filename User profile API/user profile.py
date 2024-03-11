from flask import Flask, request, jsonify

app = Flask(__name__)

user_profiles = {}


@app.route('/create-profile', methods=['POST'])
def create_profile():
    data = request.get_json()

    if 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Username and email are required'}), 400

    username = data['username']
    email = data['email']
    bio = data.get('bio', '')  # Optional bio field

    if username in user_profiles:
        return jsonify({'error': 'Username already exists'}), 400

    user_profiles[username] = {'email': email, 'bio': bio}

    return jsonify({'message': 'User profile created successfully'}), 201


@app.route('/get-profile/<username>', methods=['GET'])
def get_profile(username):
    if username in user_profiles:
        return jsonify(user_profiles[username])
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/update-profile/<username>', methods=['PUT'])
def update_profile(username):
    if username in user_profiles:
        data = request.get_json()

        new_email = data.get('email', user_profiles[username]['email'])
        new_bio = data.get('bio', user_profiles[username]['bio'])

        user_profiles[username]['email'] = new_email
        user_profiles[username]['bio'] = new_bio

        return jsonify({'message': 'User profile updated successfully'})
    else:
        return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=8080)
