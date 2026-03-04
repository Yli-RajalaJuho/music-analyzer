import os
import subprocess
import json
from typing import Tuple

# Define supported formats that ffmpeg can usually convert to WAV
SUPPORTED_FORMATS = {
    ".wav", ".mp3", ".m4a", ".mp4", ".flac", ".ogg", ".opus",
    ".aac", ".wma", ".aiff", ".aif", ".mov", ".webm", ".mkv"
}

def check_audio_file(filepath: str, filename: str) -> Tuple[bool, str]:

    extension = os.path.splitext(filename)[-1].lower()

    # Check extension
    if extension not in SUPPORTED_FORMATS:
        return False, f"Error: Unsupported file format '{extension}'. Please upload an audio or video file."

    # Check if file has an audio stream using ffprobe
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_streams", "-select_streams", "a",
            "-of", "json", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout or "{}")

        if len(info.get("streams", [])) == 0:
            return False, "Error: The file does not contain any audio"

    except Exception as e:
        return False, f"Error checking audio stream: {str(e)}"

    return True, "File is supported and contains audio."
