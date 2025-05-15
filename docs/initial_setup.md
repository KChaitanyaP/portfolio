# 📄 Integrating Private Google Drive CSV with Flask Using the Google Drive API

This guide provides step-by-step instructions to access a **private file from Google Drive** in a 
**Flask web app** using the **Google Drive API** and a **service account**.

---

## 🔧 Step-by-Step Guide (Basic Setup with Public File)

### ✅ Step 1: Prepare Your CSV File

Create a CSV file named `projects.csv` with the following structure:

```csv
title,description,color
Project1,Project1Description,blue
Project2,Project2Description,green
Project3,Project3Description,purple
```

This file will be used to generate project cards dynamically in your Flask app.

---

### ✅ Step 2: Make the CSV Publicly Accessible on Google Drive *(for quick tests only)*

> **Note:** This step is only for public files. Skip if you want secure access via API.

1. Upload the `projects.csv` to Google Drive.
2. Right-click on the file → **Share**.
3. Under "General access", select **"Anyone with the link"** and set to **Viewer**.
4. Click "Copy link".
5. Extract the **file ID** from the URL:

```
https://drive.google.com/file/d/1aBcDXYZ1234567/view?usp=sharing
                                 ^^^^^^^^^^^^^^^^
                                 This is the file ID
```

Now, You can access the file programmatically via:

```
https://drive.google.com/uc?id=FILE_ID
```

---

## 🔧 Step-by-Step: Access Private Google Drive File via API
> ⚠️ This might incur billing, so proceed at your own cost
> 
> 💡 Idea: Use free tier or use publicly shared csv file to avoid costs

> **📝 TODO:** Check if this leads to any billing
> 
### ✅ Step 1: Set Up Google Cloud Project and Enable API
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a **new project** (or select an existing one).
3. Navigate to: **APIs & Services → Library**.
4. Search for **Google Drive API** and click **Enable**.

---
> **📝 TODO:** The steps below could be automated using Terraform/GoogleCloudAutomationScript
### ✅ Step 2: Create a Service Account

1. Go to: **APIs & Services → Credentials**.
2. Click **Create Credentials → Service Account**.
3. Enter a name (e.g., `flask-drive-reader`) and click **Done**.
4. In the list of service accounts, click your new account.
5. Go to the **"Keys"** tab.
6. Click **"Add Key → Create new key → JSON"**.
7. Save the `.json` key file securely (e.g., `service_account.json`).

> ⚠️ Do **not** upload this file to GitHub or any public repository.

---

### ✅ Step 3: Share File with the Service Account

1. Copy the **service account email address**, which looks like:
```
flask-drive-reader@your-project-id.iam.gserviceaccount.com
```
2. Go to your private `projects.csv` file in Google Drive.
3. Right-click → **Share**.
4. Paste the **service account email** and give it **Viewer** access.

Now the service account has permission to read the file securely.

