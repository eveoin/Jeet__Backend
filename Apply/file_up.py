
from io import BytesIO
from flask import Flask, render_template, request, send_file
from flask_pymongo import PyMongo
from pymongo import MongoClient

from Profile_Data.my_file import Upload
from index import app

uri = 'mongodb+srv://jeetj:9FFVZMC6eU1qrson@jeetdb.trviwgp.mongodb.net/'
client = MongoClient(uri)
db = client['jeet']
collection = db['admin']

mongo = PyMongo(app, uri)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        upload = Upload(filename=file.filename, data=file.read())
        db.session.add(upload)
        db.session.commit()
        return f'Uploaded: {file.filename}'
    return render_template('uploads.html')


@app.route('/download/<upload_id>')
def download(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data),
                     download_name=upload.filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=300)
