from flask import Flask, request, jsonify
import uuid
import json

app = Flask(__name__)

# Load existing user profiles from the file or start with an empty dictionary
try:
    with open('user_profile_data.txt', 'r') as file:
        content = file.read()
        if content:
            user_profiles = json.loads(content)
        else:
            user_profiles = {}
except (FileNotFoundError, json.JSONDecodeError):
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

    # Generate a unique ID for the user profile using UUID
    user_id = str(uuid.uuid4())

    user_profiles[user_id] = {'username': username, 'email': email, 'bio': bio}

    return jsonify({'message': 'User profile created successfully', 'user_id': user_id}), 201


@app.route('/get-profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    if user_id in user_profiles:
        return jsonify(user_profiles[user_id])
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/update-profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    if user_id in user_profiles:
        data = request.get_json()

        new_email = data.get('email', user_profiles[user_id]['email'])
        new_bio = data.get('bio', user_profiles[user_id]['bio'])

        user_profiles[user_id]['email'] = new_email
        user_profiles[user_id]['bio'] = new_bio

        # Save the updated user profiles to the file
        with open('user_profile_data.txt', 'w') as file:
            for id, profile in user_profiles.items():
                file.write(
                    f"User Id: {id},\nUser Name: {profile['username']}, \nEmail Id: {profile['email']}, \nBIO: {profile['bio']}\n\n\n")

        # Retrieve the updated user profile
        updated_profile = user_profiles[user_id]

        return jsonify({'message': 'User profile updated successfully',
                        'username': updated_profile['username'],
                        'email': updated_profile['email'],
                        'bio': updated_profile['bio']}), 200
    else:
        return jsonify({'error': 'User not found'}), 404



if __name__ == '__main__':
    app.run(debug=True, port=808)
