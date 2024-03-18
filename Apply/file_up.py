from flask import Flask, render_template, request, send_file
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__)


uri = 'mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/'
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
db = client['jeet']
collection = db['admin']

mongo = PyMongo(app, uri)

class Upload:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        data = file.read()

        uploads_collection = collection
        upload = Upload(filename, data)
        result = uploads_collection.insert_one(upload.__dict__)

        if result.inserted_id:
            return f'Uploaded: {filename}'
        else:
            return 'Failed to upload file'

    return render_template('uploads.html')

if __name__ == '__main__':
    app.run(debug=True, port=30)