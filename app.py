import json
import os
import razorpay
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client = razorpay.Client(auth=("rzp_test_BqwXmtR5v1PWNh", "NnS89KiZoIfLw6briAZOnEje"))

data_file_path = 'data.json'

# Initialize waiting_list as an empty list
waiting_list = []

# Check if the file exists and is not empty
if os.path.exists(data_file_path) and os.path.getsize(data_file_path) > 0:
    # Load existing data from the JSON file
    with open(data_file_path, 'r') as json_file:
        loaded_data = json.load(json_file)

        # Ensure the loaded data is a list
        if isinstance(loaded_data, list):
            waiting_list = loaded_data


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

    # Save the updated data back to the JSON file
    with open(data_file_path, 'w') as json_file:
        json.dump(waiting_list, json_file, indent=2)
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
