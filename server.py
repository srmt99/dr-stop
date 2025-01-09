from flask import Flask, send_file
import random
import os
from pathlib import Path

app = Flask(__name__)

def get_random_voice():
    voices_dir = Path("voices")
    voices = list(voices_dir.glob("*.[mo][pg][g3]"))  # Matches .mp3 and .ogg
    if not voices:
        return None
    return random.choice(voices)

@app.route('/health')
def health():
    return "OK", 200

@app.route('/dr_stop')
def dr_stop():
    voice_file = get_random_voice()
    if not voice_file:
        return "No voices available", 404
    return send_file(voice_file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
