from flask import Flask, send_file, render_template_string, request, session
import random
from pathlib import Path
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a real secret key
app.permanent_session_lifetime = timedelta(minutes=5)  # Session lasts 5 minutes

def get_random_voice():
    voices_dir = Path("voices")
    voices = list(voices_dir.glob("*.[mo][pg][g3]"))  # Matches .mp3 and .ogg
    if not voices:
        return None
    return random.choice(voices)

@app.route('/health')
def health():
    return "OK", 200

@app.route('/dr_stop_estekhare')  # Updated route
def dr_stop():
    # Store the selected voice in session
    session.permanent = True
    voice_file = get_random_voice()
    if not voice_file:
        return "No voices available", 404
    
    session['current_voice'] = str(voice_file)

    # Check for corresponding transcription
    transcription_text = ""
    voice_number = voice_file.stem  # Get the number from filename (without extension)
    transcription_file = Path(f"transcriptions/{voice_number}.txt")
    
    if transcription_file.exists():
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_text = f.read().strip()

    # Serve an HTML page with an embedded audio player
    return render_template_string('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Play Audio</title>
                <style>
                    .container {
                        max-width: 600px;
                        margin: 0 auto;
                        text-align: center;
                    }
                    img {
                        max-width: 100%;
                        height: auto;
                        border-radius: 50%;
                        margin-bottom: 20px;
                    }
                    audio {
                        width: 100%;
                    }
                    .transcription {
                        margin-top: 20px;
                        padding: 15px;
                        background-color: #f5f5f5;
                        border-radius: 5px;
                        text-align: right;
                        direction: rtl;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <img src="{{ url_for('serve_avatar') }}" alt="Dr. Avatar">
                    <audio controls autoplay>
                    <source src="{{ url_for('serve_audio') }}" type="{{ mimetype }}">
                    Your browser does not support the audio element.
                    </audio>
                    {% if transcription %}
                    <div class="transcription">
                        <p>فال شما این است:</p>
                        <p>{{ transcription }}</p>
                    </div>
                    {% endif %}
                </div>
            </body>
        </html>
    ''', mimetype="audio/mpeg" if voice_file.suffix == ".mp3" else "audio/ogg",
        transcription=transcription_text)

@app.route('/dr_avatar')
def serve_avatar():
    return send_file('images/dr_avatar.jpg', mimetype='image/jpeg')

@app.route('/serve_audio')
def serve_audio():
    if 'current_voice' not in session:
        return "No voice selected", 404
    
    voice_file = Path(session['current_voice'])
    if not voice_file.exists():
        return "Voice file not found", 404

    # Determine the MIME type based on the file extension
    if voice_file.suffix == ".mp3":
        mimetype = "audio/mpeg"
    elif voice_file.suffix == ".ogg":
        mimetype = "audio/ogg"
    else:
        return "Unsupported file type", 400

    # Serve the audio file with the correct MIME type and support for range requests
    return send_file(
        voice_file,
        mimetype=mimetype,
        as_attachment=False,
        conditional=True  # Enable range requests
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3100)
