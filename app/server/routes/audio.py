import os, tempfile, subprocess
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from utils.db import get_db
from utils.schemas import AudioPredictionResponse, ErrorEnvelope
from utils.model_adapters import predict_audio, get_audio_meta
from utils.audio_utils import wav_duration_seconds, sniff_wav
from utils.models import Prediction
from utils.id import new_uuid, sha256_of
from utils.timing import timed_ms

router = APIRouter()

WAV_CT = {"audio/wav", "audio/wave", "audio/x-wav", "audio/vnd.wave"}
# formats accept and transcode to wav
TRANSCODE_CT = {
    "audio/mp4", "audio/m4a", "audio/3gpp", "audio/3gp",
    "audio/aac", "audio/x-caf", "audio/mpeg", "audio/mp3",
}
MAX_BYTES = 15 * 1024 * 1024  # 15 MB

def _ffmpeg_to_wav(in_path: str, out_path: str) -> None:
    # Convert to mono PCM WAV, no resample here (adapter handles sample rate)
    # -y overwrite, -ac 1 = mono; omit -ar to preserve original rate
    cmd = ["ffmpeg", "-y", "-i", in_path, "-ac", "1", out_path]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0 or not os.path.exists(out_path):
        tail = proc.stderr.decode(errors="ignore")[-400:]
        raise HTTPException(
            status_code=415,
            detail={"code": "TRANSCODE_FAILED", "message": tail},
        )

@router.post("/audio", response_model=AudioPredictionResponse, responses={415: {"model": ErrorEnvelope}})
async def post_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ctype = (file.content_type or "").lower()
    if ctype not in WAV_CT and ctype not in TRANSCODE_CT:
        raise HTTPException(
            status_code=415,
            detail={"code": "UNSUPPORTED_MEDIA_TYPE",
                    "message": "Send WAV or common mobile formats (m4a/mp4, 3gpp, aac, caf, mp3)."}
        )

    blob = await file.read()
    if len(blob) == 0:
        raise HTTPException(status_code=422, detail={"code":"EMPTY_FILE","message":"Audio file is empty."})
    if len(blob) > MAX_BYTES:
        raise HTTPException(status_code=413, detail={"code":"FILE_TOO_LARGE","message": f"Max {MAX_BYTES//(1024*1024)} MB."})

    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, file.filename or "in.bin")
        with open(in_path, "wb") as f:
            f.write(blob)

        # If not WAV, transcode to WAV (mono). Leave SR as-is.
        if ctype in WAV_CT or in_path.lower().endswith(".wav"):
            wav_path = in_path
        else:
            wav_path = os.path.join(td, "converted.wav")
            _ffmpeg_to_wav(in_path, wav_path)

        if not sniff_wav(wav_path):
            raise HTTPException(status_code=422, detail={"code":"BAD_WAV","message":"File is not a valid PCM WAV."})

        duration, sample_rate = wav_duration_seconds(wav_path)
        if duration <= 0:
            raise HTTPException(status_code=422, detail={"code":"BAD_AUDIO","message":"Cannot determine audio duration."})

        with timed_ms() as t:
            scores = predict_audio(audio_path=wav_path, duration=duration, sample_rate=sample_rate)
        processing_ms = t.ms

        top_label = max(scores, key=scores.get)
        confidence = float(scores[top_label])

        pid = new_uuid()
        meta = get_audio_meta()
        rec = Prediction(
            prediction_id=pid,
            modality="audio",
            text_len=None,
            lang=None,
            duration_sec=float(duration),
            sample_rate=int(sample_rate),
            model_name=meta["name"],
            model_version=meta["version"],
            top_label=top_label,
            confidence=confidence,
            scores=scores,
            processing_ms=processing_ms,
            input_hash=sha256_of(blob),
        )
        db.add(rec); db.commit()

        return {
            "prediction_id": pid,
            "top_label": top_label,
            "confidence": confidence,
            "scores": scores,
            "model_name": meta["name"],
            "model_version": meta["version"],
            "processing_ms": processing_ms,
            "input": {"duration_sec": duration, "sample_rate": sample_rate},
        }
