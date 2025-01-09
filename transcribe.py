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
        try:
            print(f"Processing {mp3_file.name}...")
            
            # Check if file exists and is readable
            if not mp3_file.is_file():
                print(f"Error: File {mp3_file.name} does not exist or is not accessible")
                continue
                
            # Transcribe the audio
            try:
                transcription = transcribe_audio(str(mp3_file))
            except Exception as e:
                print(f"Error processing {mp3_file.name}: {str(e)}")
                continue
                
            # Save transcription to file
            output_file = transcriptions_dir / f"{mp3_file.stem}.txt"
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(transcription)
                print(f"Transcription saved to {output_file}\n")
            except IOError as e:
                print(f"Error saving transcription for {mp3_file.name}: {str(e)}")
                
        except Exception as e:
            print(f"Unexpected error processing {mp3_file.name}: {str(e)}")
            continue

if __name__ == "__main__":
    process_all_mp3_files()
