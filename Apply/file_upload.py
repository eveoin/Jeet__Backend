from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

app = Flask(__name__)

SCOPES = ['https://drive.google.com/drive/my-drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    drive_service = build('drive', 'v3', credentials=service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES))

    file_metadata = {'name': file.filename}
    media_body = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.content_type, resumable=True)

    file = drive_service.files().create(body=file_metadata, media_body=media_body, fields='id').execute()

    return jsonify({'message': 'File uploaded successfully', 'file_id': file.get('id')})

if __name__ == '__main__':
    app.run(debug=True)
