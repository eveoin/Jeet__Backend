import json
import os
import re

import razorpay
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client = razorpay.Client(auth=("rzp_test_BqwXmtR5v1PWNh", "NnS89KiZoIfLw6briAZOnEje"))

data_file_path = 'E://py/demo/info.json'


with open(data_file_path, 'r') as json_file:
    waiting_list = json.load(json_file)

email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


@app.route('/testing', methods=['GET'])
def get_waiting_list():
    return jsonify({'count': len(waiting_list)})


@app.route('/testing', methods=['POST'])
def add_to_waiting_list():
    data = request.get_json()

    if 'Email' not in data or not data['Email'].strip() or not re.match(email_regex, data['Email']):
        return jsonify({'error': 'Invalid data format'}), 400

    new_email = data['Email']

    if any(entry['Email'] == new_email for entry in waiting_list):
        return jsonify({'error': 'Email already in waiting list'}), 400

    waiting_list.append({
        'Email': data['Email']
    })

    with open(data_file_path, 'w') as json_file:
        json.dump(waiting_list, json_file, indent=2)

    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
