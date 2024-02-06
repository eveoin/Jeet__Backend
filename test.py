import json
import os

import razorpay

client = razorpay.Client(auth=("rzp_test_BqwXmtR5v1PWNh", "NnS89KiZoIfLw6briAZOnEje"))

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

waiting_list = 'data.json'


try:
    with open(waiting_list, 'r') as file:
        # Check if the file is not empty
        file_content = file.read().strip()
        waiting_list = json.loads(file_content) if file_content else []
except (FileNotFoundError, json.JSONDecodeError):
    waiting_list = []


@app.route('/test', methods=['GET'])
def get_waiting_list():
    return jsonify({'count': len(waiting_list)})


@app.route('/test', methods=['POST'])
def add_to_waiting_list():
    data = request.get_json()


    if 'Email' not in data:
        return jsonify({'error': 'Invalid data format'}), 400

    waiting_list.append({
        'Email': data['Email'],
        # 'paymentId': data['paymentId']
    })

    return jsonify(waiting_list)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
