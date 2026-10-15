from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import librosa
import ffmpeg
import os
import tempfile
import uuid
from utils.key_estimator import KeyEstimator
from utils.audio_utils import check_audio_file
from utils.stemremover import separate_vocals
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
key_estimator = KeyEstimator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# POST /process-audio
# ------------------------------

@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    separate: bool = Form(False)
):
    # ------------------------------------
    # 1. Generate session ID
    # ------------------------------------
    session_id = str(uuid.uuid4())

    # Make sure upload folder exists
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # ------------------------------------
    # 2. Save uploaded file as session_id.ext
    # ------------------------------------
    ext = os.path.splitext(file.filename)[-1].lower()
    temp_input_path = os.path.join(upload_dir, f"{session_id}{ext}")

    with open(temp_input_path, "wb") as f:
        f.write(await file.read())

    # ------------------------------------
    # 3. Validate audio
    # ------------------------------------
    is_valid, message = check_audio_file(temp_input_path, file.filename)
    if not is_valid:
        os.remove(temp_input_path)
        return {"error": message}

    # ------------------------------------
    # 4. Convert to WAV if needed
    # ------------------------------------
    if ext == ".wav":
        wav_path = temp_input_path
    else:
        wav_path = os.path.join(upload_dir, f"{session_id}.wav")
        try:
            ffmpeg.input(temp_input_path).output(
                wav_path, format="wav", ac=2, ar="44100"
            ).run(quiet=True, overwrite_output=True)
        except ffmpeg.Error as e:
            os.remove(temp_input_path)
            return {"error": f"ffmpeg conversion failed: {e}"}

    # ------------------------------------
    # 5. Run BPM + Key detection + Separation if asked
    # ------------------------------------
    try:
        y, sr = librosa.load(wav_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo)

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = chroma.mean(axis=1)
        key, mode = key_estimator(chroma_mean)

        if separate:
            separate_vocals(wav_path)
        else:
            session_id = "no separation"

    except Exception:
        return {"error": "Processing failed. File may be corrupted or silent."}

    # ------------------------------------
    # 6. Prepare response
    # ------------------------------------
    response = {
        "session_id": session_id,
        "bpm": round(tempo, 0),
        "key": f"{key} {mode}",
    }

    return response


@app.get("/download/{session_id}/{stem_name}")
async def download_stem(session_id: str, stem_name: str):
    file_path = os.path.join("separated", "mdx_extra", session_id, f"{stem_name}.mp3")
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=f"{stem_name}.mp3", media_type="audio/mpeg")
    return {"error": "File not found"}