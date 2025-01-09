from flask import Flask, send_file, render_template, request, session
import random
import requests
import json
from pathlib import Path
from datetime import timedelta

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "your-deepseek-api-key"  # Replace with your actual API key

def generate_fortune(transcription_text):
    """Generate a fortune telling using DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    این متن یک فال است. لطفاً یک فال طنز و خنده‌دار ۲-۳ جمله‌ای به زبان فارسی بنویس که با این متن مرتبط باشد اما محتوای نامناسب نداشته باشد:
    {transcription_text}
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a funny Persian fortune teller."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating fortune: {e}")
        return "امروز فال‌گیری خوابه! بعداً بیا :)"

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
    
    fortune_text = ""
    if transcription_file.exists():
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_text = f.read().strip()
            fortune_text = generate_fortune(transcription_text)

    # Serve an HTML page with an embedded audio player
    return render_template('index.html',
        mimetype="audio/mpeg" if voice_file.suffix == ".mp3" else "audio/ogg",
        transcription=fortune_text)

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
