import os
import subprocess
from pathlib import Path

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

print("Conversion complete!")