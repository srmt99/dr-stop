import speech_recognition as sr
from pydub import AudioSegment
import os
from pathlib import Path

def transcribe_audio(file_path):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Convert MP3 to WAV
    sound = AudioSegment.from_mp3(file_path)
    wav_path = file_path.replace(".mp3", ".wav")
    sound.export(wav_path, format="wav")

    # Load the converted WAV file
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)  # Read the entire audio file

    # Transcribe using Google Speech Recognition
    try:
        text = recognizer.recognize_google(audio, language="fa-IR")  # Persian language code
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    finally:
        # Clean up temporary WAV file
        if os.path.exists(wav_path):
            os.remove(wav_path)

def process_all_mp3_files():
    # Directory containing the .mp3 files
    voices_dir = Path("voices")
    
    # Directory to store transcriptions
    transcriptions_dir = Path("transcriptions")
    transcriptions_dir.mkdir(exist_ok=True)

    # Find all .mp3 files in the voices directory
    mp3_files = list(voices_dir.glob("*.mp3"))

    if not mp3_files:
        print("No .mp3 files found in the 'voices' directory.")
        return

    # Process each MP3 file
    for mp3_file in mp3_files:
        print(f"Processing {mp3_file.name}...")
        
        # Transcribe the audio
        transcription = transcribe_audio(str(mp3_file))
        
        # Save transcription to file
        output_file = transcriptions_dir / f"{mp3_file.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        print(f"Transcription saved to {output_file}\n")

if __name__ == "__main__":
    process_all_mp3_files()
