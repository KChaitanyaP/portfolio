import pandas as pd
from flask import Flask, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import csv
from flask import request, redirect, url_for
from googleapiclient.http import MediaIoBaseUpload
import io

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email):
        self.id = email

@login_manager.user_loader
def load_user(email):
    df = read_users()
    if email in df['email'].values:
        return User(email)
    return None

# Load your service account credentials
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACC_KEY_FILE_LOCATION", None)
if SERVICE_ACCOUNT_FILE is None:
    raise ValueError("service_account_creds_file_location not present!")
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)

# Replace with your actual file ID
FILE_ID = os.environ.get("GOOGLE_DRIVE_PROJECTS_CSV_FILE_ID", None)
if FILE_ID is None:
    raise ValueError("GOOGLE_DRIVE_PROJECTS_CSV_FILE_ID not present!")

USERS_FILE_ID = os.environ.get("GOOGLE_DRIVE_USERS_CSV_FILE_ID", None)
if USERS_FILE_ID is None:
    raise ValueError("GOOGLE_DRIVE_USERS_FILE_ID not present!")

def get_project_data():
    request = drive_service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    df = pd.read_csv(fh)
    print("df: ")
    print(df)
    return df.to_dict(orient='records')


@app.route('/healthz')
def healthz():
    return {"status": "ok"}, 200


@app.route('/')
@login_required
def index():
    projects = get_project_data()
    return render_template('index.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    title = request.form['title']
    description = request.form['description']
    plan = request.form['plan']
    color = request.form['color']

    # Step 1: Download the file
    request_drive = drive_service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_drive)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    # Step 2: Append new project
    fh.seek(0)
    lines = fh.read().decode('utf-8').splitlines()
    reader = csv.reader(lines)
    rows = list(reader)
    rows.append([title, description, color, plan])

    # Step 3: Write to temp file
    string_buffer = io.StringIO()
    writer = csv.writer(string_buffer)
    writer.writerows(rows)

    # Step 4: Encode to bytes and upload
    byte_buffer = io.BytesIO(string_buffer.getvalue().encode('utf-8'))
    media = MediaIoBaseUpload(byte_buffer, mimetype='text/csv', resumable=True)
    drive_service.files().update(fileId=FILE_ID, media_body=media).execute()

    return redirect(url_for('index'))

@app.route('/edit', methods=['POST'])
def edit_project():
    original_title = request.form['original_title']
    new_title = request.form['title']
    new_description = request.form['description']
    new_plan = request.form['plan']
    new_color = request.form['color']

    # Step 1: Download existing file
    request_drive = drive_service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_drive)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    lines = fh.read().decode('utf-8').splitlines()
    reader = csv.reader(lines)
    rows = list(reader)

    print([new_title, new_description, new_color, new_plan])
    # Step 2: Edit the matching project
    headers = rows[0]
    updated_rows = [headers]
    for row in rows[1:]:
        if row[0] == original_title:
            updated_rows.append([new_title, new_description, new_color, new_plan])
        else:
            updated_rows.append(row)

    # Write CSV to a string buffer
    string_buffer = io.StringIO()
    writer = csv.writer(string_buffer)
    writer.writerows(updated_rows)

    # Encode string buffer into bytes
    byte_buffer = io.BytesIO(string_buffer.getvalue().encode('utf-8'))
    media = MediaIoBaseUpload(byte_buffer, mimetype='text/csv', resumable=True)
    drive_service.files().update(fileId=FILE_ID, media_body=media).execute()

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        df = read_users()

        user_row = df[df['email'] == email]
        if not user_row.empty and check_password_hash(user_row.iloc[0]['password'], password):
            login_user(User(email))
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        df = read_users()

        if email in df['email'].values:
            return render_template('register.html', error='User already exists.')

        new_user = pd.DataFrame([[email, generate_password_hash(password)]], columns=['email', 'password'])
        df = pd.concat([df, new_user], ignore_index=True)
        write_users(df)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def read_users():
    request = drive_service.files().get_media(fileId=USERS_FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_csv(fh)

def write_users(df):
    string_buffer = io.StringIO()
    df.to_csv(string_buffer, index=False)
    byte_buffer = io.BytesIO(string_buffer.getvalue().encode('utf-8'))
    media = MediaIoBaseUpload(byte_buffer, mimetype='text/csv', resumable=True)
    drive_service.files().update(fileId=USERS_FILE_ID, media_body=media).execute()


def main():
    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()
