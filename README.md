# File Upload & Sharing Service

## Features
- Upload files via API
- Generate a shareable download link
- Set expiration by time or download count
- Store metadata in SQLite

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Use `/upload` to upload files and `/download/<file_id>` to retrieve them