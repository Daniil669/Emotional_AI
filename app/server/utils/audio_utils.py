import wave, contextlib

def sniff_wav(path: str) -> bool:
    # Validation: openable as WAV, PCM/uncompressed
    try:
        with contextlib.closing(wave.open(path, "rb")) as wf:
            # If this works without error, assume valid enough for prototype
            return wf.getcomptype() in ("NONE", "ULAW", "ALAW")# common types
    except Exception:
        return False

def wav_duration_seconds(path: str) -> tuple[float, int]:
    with contextlib.closing(wave.open(path, "rb")) as wf:
        frames = wf.getnframes()
        sr = wf.getframerate()
        duration = frames / float(sr) if sr else 0.0
        return duration, sr
