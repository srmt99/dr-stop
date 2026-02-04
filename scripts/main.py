import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def organize_voices():
    """Organize voice files into voices directory"""
    # Create voices directory if it doesn't exist
    voices_dir = DATA_DIR / "voices"
    voices_dir.mkdir(exist_ok=True)
    
    # Find all sound files
    sound_files = []
    for root, _, files in os.walk(str(BASE_DIR)):
        for file in files:
            if file.lower().endswith((".mp3", ".ogg")):
                sound_files.append(Path(root) / file)
    
    # Rename and move files
    for i, sound_file in enumerate(sound_files):
        ext = sound_file.suffix.lower()
        new_name = voices_dir / f"{i}{ext}"
        sound_file.rename(new_name)
        print(f"Moved {sound_file} -> {new_name}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Organize voice files')
    parser.add_argument('--port', type=int, default=3100, help='Port to run the server on (if applicable)')
    args = parser.parse_args()
    
    organize_voices()
