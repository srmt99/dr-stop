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
    
    return updated_count

if __name__ == "__main__":
    updated_count = process_transcriptions()
    print(f"Transcription processing complete! Updated {updated_count} transcription files.")
