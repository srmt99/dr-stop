import speech_recognition as sr
from pydub import AudioSegment

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

if __name__ == "__main__":
    audio_file = "voices/1.mp3"
    transcription = transcribe_audio(audio_file)
    
    # Save transcription to file
    output_file = audio_file.replace(".mp3", ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcription)
    
    print(f"Transcription saved to {output_file}")
