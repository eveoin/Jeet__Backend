import os

from flask import Flask, request
import requests

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
GOOGLE_DRIVE_FOLDER = 'https://drive.google.com/drive/folders/1m_JS0-1EH0AapXJcvr4Onz68_0Q92A8B?usp=sharing'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'


    file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)