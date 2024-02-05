import json

import razorpay
from flask import Flask, request, jsonify
from flask_cors import CORS

client = razorpay.Client(auth=("rzp_test_BqwXmtR5v1PWNh", "NnS89KiZoIfLw6briAZOnEje"))

app = Flask(__name__)
CORS(app)

# Specify the full path to the data.json file
waiting_list = 'E:\py\demo\data.json'

try:
    with open(waiting_list, 'r') as file:
        waiting_list = json.load(file)
except FileNotFoundError:
    print("Error: File not found.")
    exit()

if not isinstance(waiting_list, list):
    print("Error: 'waiting_list' is not a list.")
    exit()

email_count = sum('Email' in item for item in waiting_list)
print("Number of Email IDs:", email_count)

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
         #'paymentId': data['paymentId']
    })


    return jsonify(waiting_list)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)