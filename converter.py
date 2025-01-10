import os
import subprocess
from pathlib import Path

def process_transcriptions():
    """Process all text files in transcriptions directory"""
    transcriptions_dir = Path("transcriptions")
    txt_files = list(transcriptions_dir.glob("*.txt"))
    
    if not txt_files:
        print("No .txt files found in the 'transcriptions' directory.")
        return 0
        
    updated_count = 0
    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "Google Speech Recognition" in content:
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write("یک فال رندوم ایجاد کن")
                print(f"Updated {txt_file} with Persian text")
                updated_count += 1
        except Exception as e:
            print(f"Failed to process {txt_file}: {e}")

# Directory containing the .ogg files
voices_dir = Path("voices")

# Temporary directory to store converted files
tmp_dir = Path("tmp")
tmp_dir.mkdir(exist_ok=True)

# Find all .ogg files in the voices directory
ogg_files = list(voices_dir.glob("*.ogg"))

if not ogg_files:
    print("No .ogg files found in the 'voices' directory.")
    exit()

# Convert each .ogg file to .mp3
for ogg_file in ogg_files:
    # Define the output .mp3 file path
    mp3_file = tmp_dir / f"{ogg_file.stem}.mp3"

    print(f"Converting {ogg_file} to {mp3_file}...")

    # Use ffmpeg to convert the file
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(ogg_file), "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_file)],
            check=True,
        )
        print(f"Successfully converted {ogg_file} to {mp3_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {ogg_file}: {e}")
        continue

    # Replace the original .ogg file with the converted .mp3 file
    try:
        os.replace(mp3_file, voices_dir / mp3_file.name)
        print(f"Moved {mp3_file} to {voices_dir / mp3_file.name}.")
    except Exception as e:
        print(f"Failed to move {mp3_file}: {e}")

# Clean up the temporary directory
try:
    tmp_dir.rmdir()
    print("Temporary directory cleaned up.")
except OSError as e:
    print(f"Failed to clean up temporary directory: {e}")

# Process transcriptions after audio conversion
updated_count = process_transcriptions()

print(f"Conversion and transcription processing complete! Updated {updated_count} transcription files.")
