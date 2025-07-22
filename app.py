from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
import whisper
import subprocess

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audiofile' not in request.files:
            return 'No file part'
        file = request.files['audiofile']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Convert to WAV mono 16kHz
            converted_path = os.path.splitext(filepath)[0] + "_converted.wav"
            subprocess.run([
                "ffmpeg", "-i", filepath,
                "-ac", "1", "-ar", "16000",
                converted_path
            ])

            # Transcribe with Whisper
            model = whisper.load_model("base")
            result = model.transcribe(converted_path, language="es")

            return f"<h2>Transcripción:</h2><pre>{result['text']}</pre>"

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
