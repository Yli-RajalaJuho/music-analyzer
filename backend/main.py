from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time
import shutil
import threading
import essentia.standard as es
import ffmpeg
import os
import uuid

from utils.audio_utils import check_audio_file
from utils.stemremover import separate_vocals

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_old_sessions(
    base_paths=["uploads", os.path.join("separated", "mdx_extra")],
    max_age_seconds=900  # 15 minutes
):
    # Deletes session files/folders older than max_age_seconds.
    now = time.time()

    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue

        for name in os.listdir(base_path):
            path = os.path.join(base_path, name)
            try:
                # Calculate age of file/folder
                age = now - os.path.getmtime(path)

                if age > max_age_seconds:
                    if os.path.isfile(path) or os.path.islink(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                    print(f"Deleted old session: {path}")
            except Exception as e:
                print(f"Failed to delete {path}: {e}")

def schedule_cleanup(interval=600):
    # Run cleanup every `interval` seconds in a background thread.
    def loop():
        while True:
            cleanup_old_sessions(max_age_seconds=900)
            time.sleep(interval)

    t = threading.Thread(target=loop, daemon=True)
    t.start()


# ------------------------------
# STARTUP
# ------------------------------
@app.on_event("startup")
def startup_event():
    schedule_cleanup()


# ------------------------------
# SHUTDOWN
# ------------------------------
@app.on_event("shutdown")
def shutdown_event():
    print("Server shutting down, cleaning up resources...")

    # Helper function to delete folder contents safely
    def clear_folder(folder_path):
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  # delete file or symlink
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # delete folder recursively
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    # Clear uploads folder
    clear_folder("uploads")

    # Clear separated/mdx_extra folder
    clear_folder(os.path.join("separated", "mdx_extra"))

    print("Temporary files cleaned up.")


# ------------------------------
# POST /process-audio
# ------------------------------
@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    separate: bool = Form(False),
    previous_session_id: Optional[str] = Form(None)
):
    # ------------------------------------
    # 0. Cleanup old sessions
    # ------------------------------------
    if previous_session_id:
        old_path = os.path.join("separated", "mdx_extra", previous_session_id)

        if os.path.exists(old_path):
            shutil.rmtree(old_path)

    # ------------------------------------
    # 1. Generate session ID
    # ------------------------------------
    session_id = str(uuid.uuid4())

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # ------------------------------------
    # 2. Save uploaded file
    # ------------------------------------
    ext = os.path.splitext(file.filename)[-1].lower()
    input_path = os.path.join(upload_dir, f"{session_id}{ext}")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # ------------------------------------
    # 3. Validate audio
    # ------------------------------------
    is_valid, message = check_audio_file(input_path, file.filename)
    if not is_valid:
        os.remove(input_path)
        return {"error": message}

    # ------------------------------------
    # 4. Convert to WAV if needed
    # ------------------------------------
    if ext == ".wav":
        wav_path = input_path
    else:
        wav_path = os.path.join(upload_dir, f"{session_id}.wav")
        try:
            ffmpeg.input(input_path).output(
                wav_path,
                format="wav",
                ac=2,
                ar="44100"
            ).run(quiet=True, overwrite_output=True)
        except ffmpeg.Error as e:
            os.remove(input_path)
            return {"error": f"ffmpeg conversion failed: {e}"}

    # ------------------------------------
    # 5. Essentia analysis (BPM + Key)
    # ------------------------------------
    try:
        # Load audio
        audio = es.MonoLoader(
            filename=wav_path,
            sampleRate=44100
        )()

        # BPM detection
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, _, _, _, _ = rhythm_extractor(audio)

        # Key detection
        key_extractor = es.KeyExtractor(profileType="edma")
        key, scale, strength = key_extractor(audio)

        # Optional vocal separation
        if separate:
            separate_vocals(wav_path)

        # ------------------------------------
        # Cleanup
        # ------------------------------------
        # Remove original uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)

        # Remove wav file if it was converted
        if os.path.exists(wav_path) and wav_path != input_path:
            os.remove(wav_path)

    except Exception as e:
        print(e)
        return {"error": "Processing failed. File may be corrupted or silent."}

    # ------------------------------------
    # 6. Response
    # ------------------------------------
    response = {
        "session_id": session_id,
        "bpm": round(bpm, 0),
        "key": f"{key} {scale}",
        "separation": separate,
    }

    return response


# ------------------------------
# GET /download/{session_id}/{stem_name}
# ------------------------------
@app.get("/download/{session_id}/{stem_name}")
async def download_stem(session_id: str, stem_name: str):
    file_path = os.path.join(
        "separated",
        "mdx_extra",
        session_id,
        f"{stem_name}.mp3"
    )

    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            filename=f"{stem_name}.mp3",
            media_type="audio/mpeg"
        )

    return {"error": "File not found"}
