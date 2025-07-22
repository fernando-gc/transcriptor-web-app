
from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    filename = None
    if request.method == 'POST' and 'audiofile' in request.files:
        file = request.files['audiofile']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return render_template('index.html', filename=filename)
    return render_template('index.html')

@app.route('/transcribir/<filename>', methods=['POST'])
def transcribir(filename):
    import whisper
    import subprocess

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    converted_path = os.path.splitext(filepath)[0] + "_converted.wav"

    subprocess.run([
        "ffmpeg", "-i", filepath,
        "-ac", "1", "-ar", "16000",
        converted_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    model = whisper.load_model("base")
    result = model.transcribe(converted_path, language="es")

    return render_template('index.html', filename=filename, transcription=result['text'])

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
