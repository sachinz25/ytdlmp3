import os
import uuid
import shutil
from flask import Flask, request, send_file
from yt_dlp import YoutubeDL
from zipfile import ZipFile

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h2>YouTube Playlist Audio Downloader (AAC/M4A)</h2>
    <form action="/download" method="post">
        <input name="playlist_url" type="text" placeholder="Paste playlist URL" style="width: 400px"/>
        <input type="submit" value="Download ZIP">
    </form>
    '''

@app.route('/download', methods=['POST'])
def download_audio():
    url = request.form.get('playlist_url')
    if not url:
        return "Error: No URL provided", 400

    session_id = str(uuid.uuid4())
    out_dir = f'temp/{session_id}'
    os.makedirs(out_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': f'{out_dir}/%(title).200s.%(ext)s',
        'postprocessors': [],  # No conversion needed
        'quiet': True,
        'noplaylist': False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        shutil.rmtree(out_dir, ignore_errors=True)
        return f"Download error: {str(e)}", 500

    zip_path = f'{out_dir}.zip'
    try:
        with ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(out_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)

        shutil.rmtree(out_dir, ignore_errors=True)
        return send_file(zip_path, as_attachment=True, download_name="playlist_audio.zip")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

# 🚨 Add this block to make it work on Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
