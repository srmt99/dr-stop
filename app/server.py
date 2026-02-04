from flask import Flask, send_file, render_template, session, Response
import time
import random
import requests
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Load environment variables from .env file
load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("No DEEPSEEK_API_KEY found in environment variables")

def generate_fortune(transcription_text, prompt_template):
    """Generate a fortune telling using DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"{prompt_template}\n{transcription_text}"
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a funny Persian fortune teller who is not afraid of upsetting a person!."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 250
    }
    
    try:
        print("Sending to API:", prompt.encode('utf-8').decode('utf-8'))  # Debug print with explicit encoding
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating fortune: {e}")
        return "امروز فال‌گیری خوابه! بعداً بیا :)"

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    static_url_path="",
    template_folder=str(TEMPLATES_DIR),
)
app.secret_key = 'your-secret-key-here'  # Change this to a real secret key
app.permanent_session_lifetime = timedelta(minutes=5)  # Session lasts 5 minutes

def get_random_voice():
    voices_dir = DATA_DIR / "voices"
    voices = list(voices_dir.glob("*.[mo][pg][g3]"))  # Matches .mp3 and .ogg
    if not voices:
        return None
    return random.choice(voices)

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dr_stop_estekhare')
def dr_stop():
    return render_template('loading.html')

@app.route('/dr_stop_estekhare/result')
def dr_stop_result():
    # Always get a new random voice for each request
    voice_file = get_random_voice()
    if not voice_file:
        return "No voices available", 404

    # Store the selected voice in session
    session.permanent = True
    session['current_voice'] = str(voice_file)

    # Check for corresponding transcription
    transcription_text = ""
    voice_number = voice_file.stem  # Get the number from filename (without extension)
    transcription_file = DATA_DIR / "transcriptions" / f"{voice_number}.txt"

    fortune_text = ""
    if transcription_file.exists():
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_text = f.read().strip()
            prompt_file = random.choice([
                DATA_DIR / "prompts" / "estekhare_negative.txt",
                DATA_DIR / "prompts" / "estekhare_positive.txt",
            ])
            with open(prompt_file, 'r', encoding='utf-8') as pf:
                prompt_template = pf.read().strip()
            fortune_text = generate_fortune(transcription_text, prompt_template)

    return render_template('index.html',
        mimetype="audio/mpeg" if voice_file.suffix == ".mp3" else "audio/ogg",
        transcription=fortune_text)

def generate_audio_stream():
    """Generate a continuous stream of random audio files"""
    while True:
        voice_file = get_random_voice()
        if not voice_file:
            yield b""
            continue
            
        # Add a small delay between files
        time.sleep(0.5)
        
        # Read the audio file in chunks
        with open(voice_file, 'rb') as f:
            while chunk := f.read(1024 * 1024):  # Read 1MB chunks
                yield chunk

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

@app.route('/dr_stop_radio')
def dr_stop_radio():
    """Continuous audio stream of random voices with avatar"""
    return render_template('radio.html')

@app.route('/dr_stop_radio_stream')
def dr_stop_radio_stream():
    """Audio stream endpoint for the radio"""
    voice_file = get_random_voice()
    if not voice_file:
        return "No voices available", 404
        
    # Determine MIME type
    mimetype = "audio/mpeg" if voice_file.suffix == ".mp3" else "audio/ogg"
    
    return Response(
        generate_audio_stream(),
        mimetype=mimetype,
        headers={
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked'
        }
    )

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the fortune telling server')
    parser.add_argument('--port', type=int, default=3100, help='Port to run the server on')
    parser.add_argument('--ssl-cert', help='Path to SSL certificate file')
    parser.add_argument('--ssl-key', help='Path to SSL private key file')
    args = parser.parse_args()
    
    ssl_context = None
    if args.ssl_cert and args.ssl_key:
        ssl_context = (args.ssl_cert, args.ssl_key)
    
    app.run(host='0.0.0.0', 
            port=args.port, 
            ssl_context=ssl_context)
