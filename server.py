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

    # Serve an HTML page with an embedded audio player
    return render_template_string('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Play Audio</title>
            </head>
            <body>
                <audio controls autoplay>
                    <source src="{{ url_for('serve_audio') }}" type="{{ mimetype }}">
                    Your browser does not support the audio element.
                </audio>
            </body>
        </html>
    ''', mimetype="audio/mpeg" if voice_file.suffix == ".mp3" else "audio/ogg")

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
