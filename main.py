import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import os
from flask import jsonify
import io
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

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

SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACC_KEY_FILE_LOCATION")
PARENT_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_PARENT_FOLDER_ID")
USERS_FILE_ID = os.environ.get("GOOGLE_DRIVE_USERS_CSV_FILE_ID")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

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

def get_or_create_user_folder(email):
    query = f"name='{email}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{PARENT_FOLDER_ID}' in parents"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    items = results.get("files", [])

    if items:
        return items[0]['id']

    file_metadata = {
        "name": email,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [PARENT_FOLDER_ID]
    }
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    folder_id = folder.get('id')

    buffer = io.BytesIO("title,description,plan,color\n".encode("utf-8"))
    media = MediaIoBaseUpload(buffer, mimetype="text/csv", resumable=True)
    file_metadata = {
        "name": "projects.csv",
        "parents": [folder_id]
    }
    drive_service.files().create(body=file_metadata, media_body=media).execute()

    return folder_id

def get_user_projects_file_id(folder_id):
    query = f"name='projects.csv' and trashed=false and '{folder_id}' in parents"
    result = drive_service.files().list(q=query, fields="files(id)").execute()
    files = result.get("files", [])
    return files[0]["id"] if files else None

def read_projects():
    file_id = session.get("projects_file_id")
    if not file_id:
        return pd.DataFrame(columns=["title", "description", "plan", "color"])

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_csv(fh)

def write_projects(df):
    file_id = session.get("projects_file_id")
    if not file_id:
        return

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    byte_buffer = io.BytesIO(buffer.getvalue().encode("utf-8"))
    media = MediaIoBaseUpload(byte_buffer, mimetype="text/csv", resumable=True)
    drive_service.files().update(fileId=file_id, media_body=media).execute()

@app.route('/')
@login_required
def index():
    projects = read_projects().to_dict(orient='records')
    return render_template('index.html', projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        df = read_users()

        user_row = df[df['email'] == email]
        if not user_row.empty and check_password_hash(user_row.iloc[0]['password'], password):
            login_user(User(email))

            folder_id = get_or_create_user_folder(email)
            file_id = get_user_projects_file_id(folder_id)
            session['projects_folder_id'] = folder_id
            session['projects_file_id'] = file_id

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

@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    df = read_projects()
    new_entry = {
        'title': request.form['title'],
        'description': request.form['description'],
        'plan': request.form['plan'],
        'color': request.form['color']
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    write_projects(df)
    return redirect(url_for('index'))

@app.route('/edit', methods=['POST'])
@login_required
def edit_project():
    df = read_projects()
    title = request.form['original_title']
    index = df[df['title'] == title].index
    if not index.empty:
        idx = index[0]
        df.at[idx, 'title'] = request.form['title']
        df.at[idx, 'description'] = request.form['description']
        df.at[idx, 'plan'] = request.form['plan']
        df.at[idx, 'color'] = request.form['color']
        write_projects(df)
    return redirect(url_for('index'))

@app.route('/healthz')
def healthz():
    return "ok", 200

@app.route('/get-alarm-sounds')
def get_alarm_sounds():
    alarm_folder = os.path.join(app.static_folder, 'alarm_sounds')
    files = [f for f in os.listdir(alarm_folder) if f.endswith('.mp3')]
    return jsonify(files)


def main():
    app.run(host="0.0.0.0", port=8000, debug=True)


@app.route('/today')
def today():
    return render_template('today.html')


if __name__ == "__main__":
    main()
