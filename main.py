import io
import pandas as pd
from flask import Flask, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os

app = Flask(__name__)

# Load your service account credentials
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACC_KEY_FILE_LOCATION", None)
if SERVICE_ACCOUNT_FILE is None:
    raise ValueError("service_account_creds_file_location not present!")
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)

# Replace with your actual file ID
FILE_ID = os.environ.get("GOOGLE_DRIVE_PROJECTS_CSV_FILE_ID", None)
if FILE_ID is None:
    raise ValueError("GOOGLE_DRIVE_PROJECTS_CSV_FILE_ID not present!")

def get_project_data():
    request = drive_service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    df = pd.read_csv(fh)
    print("df: ", df)
    return df.to_dict(orient='records')

@app.route('/')
def index():
    projects = get_project_data()
    return render_template('index.html', projects=projects)

def main():
    app.run(port=8000, debug=True)

if __name__ == "__main__":
    main()
