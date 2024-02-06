import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import razorpay

app = Flask(__name__)
CORS(app)

# This is the list where the waiting list data is stored
waiting_list = 'data.json'

try:
    with open(waiting_list, 'r') as file:
        waiting_list = json.load(file)
except FileNotFoundError:
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

    return jsonify()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
