import os
import uuid
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            unique_id TEXT UNIQUE NOT NULL,
            expiry_time DATETIME,
            max_downloads INTEGER,
            download_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "Welcome to the File Upload Service!"

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload and generates a unique download link."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    expiry_days = request.form.get('expiry_days', type=int)
    max_downloads = request.form.get('max_downloads', type=int)
    
    unique_id = str(uuid.uuid4())
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_id + '_' + filename)
    file.save(filepath)
    
    expiry_time = None
    if expiry_days:
        expiry_time = datetime.utcnow() + timedelta(days=expiry_days)
    
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (filename, filepath, unique_id, expiry_time, max_downloads, download_count)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (filename, filepath, unique_id, expiry_time, max_downloads))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'File uploaded successfully', 'download_link': f'http://127.0.0.1:5000/download/{unique_id}'})

@app.route('/download/<unique_id>', methods=['GET'])
def download_file(unique_id):
    """Handles file download and checks expiration rules."""
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT filename, filepath, expiry_time, max_downloads, download_count FROM files WHERE unique_id = ?
    ''', (unique_id,))
    file_data = cursor.fetchone()
    conn.close()
    
    if not file_data:
        return jsonify({'error': 'File not found or expired'}), 404
    
    filename, filepath, expiry_time, max_downloads, download_count = file_data
    
    if expiry_time and datetime.utcnow() > datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S.%f"):
        os.remove(filepath)
        conn = sqlite3.connect('files.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE unique_id = ?', (unique_id,))
        conn.commit()
        conn.close()
        return jsonify({'error': 'File has expired'}), 410
    
    if max_downloads and download_count >= max_downloads:
        os.remove(filepath)
        conn = sqlite3.connect('files.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE unique_id = ?', (unique_id,))
        conn.commit()
        conn.close()
        return jsonify({'error': 'Maximum downloads reached'}), 410
    
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE files SET download_count = download_count + 1 WHERE unique_id = ?', (unique_id,))
    conn.commit()
    conn.close()
    
    return send_file(filepath, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    init_db()
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
