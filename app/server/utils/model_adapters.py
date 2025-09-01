import os, json, hashlib, sys
from pathlib import Path
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
import torch, torchaudio
from transformers import AutoTokenizer, AutoModelForSequenceClassification


load_dotenv()  # load server/.env into process env

def _resolve_path(p: str | None) -> str:
    if not p: return ""
    p = os.path.expanduser(p)
    if os.path.isabs(p) and os.path.exists(p):
        return p
    # try CWD
    if os.path.exists(p):
        return os.path.abspath(p)
    # try repo root (server/utils/ >> repo is 2 levels up)
    repo_root = Path(__file__).resolve().parents[2] # ../app
    candidate = repo_root / p
    if candidate.exists():
        return str(candidate)
    return p # will fail later, log below

def _read_meta(dir_path: str, fallback_name: str):
    meta_path = Path(dir_path) / "model_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r") as f:
                m = json.load(f)
            # minimal fields
            return {"name": m.get("name", fallback_name), "version": m.get("version", Path(dir_path).name)}
        except Exception:
            pass
    return {"name": fallback_name, "version": Path(dir_path).name}

MODE = os.getenv("MODE", "MOCK").upper()


MODE = os.getenv("MODE")

# Labels (for mock defaults)
DEFAULT_LABELS = ["joy","sadness","anger","fear","neutral","surprise","disgust"]

def _ensure_text_loaded():
    if MODE == "REAL" and _TEXT["pipe"] is None:
        try:
            labels, pipe, meta = _load_text_real()
            _TEXT.update({"labels": labels, "pipe": pipe, "meta": meta})
        except Exception as e:
            print(f"[model_adapters] TEXT load failed: {e}", file=sys.stderr)
    return _TEXT

def _ensure_audio_loaded():
    if MODE == "REAL" and _AUDIO["infer"] is None:
        try:
            labels, infer, meta = _load_audio_real()
            _AUDIO.update({"labels": labels, "infer": infer, "meta": meta})
        except Exception as e:
            print(f"[model_adapters] AUDIO load failed: {e}", file=sys.stderr)
    return _AUDIO

def _seed_from_bytes(b: bytes) -> int:
    return int(hashlib.sha256(b).hexdigest()[:8], 16)

def _softmax(v: np.ndarray) -> np.ndarray:
    v = v - v.max()
    e = np.exp(v)
    return e / e.sum()

def _scores_from_seed(seed: int, labels) -> dict:
    rng = np.random.RandomState(seed)
    logits = rng.randn(len(labels)) * 1.5 + rng.rand(len(labels))
    probs = _softmax(logits).astype(float)
    return {lbl: float(p) for lbl, p in zip(labels, probs)}

# Globals filled at first use
_TEXT = {"labels": DEFAULT_LABELS, "meta": {"name":"bert-goemotions-mock","version":"dev-mock"}, "pipe": None}
_AUDIO = {"labels": DEFAULT_LABELS, "meta": {"name":"speechbrain-ser-mock","version":"dev-mock"}, "infer": None}

def _load_text_real():
    model_dir = _resolve_path(os.getenv("TEXT_MODEL_DIR"))
    labels_path = _resolve_path(os.getenv("TEXT_LABELS_PATH"))

    if not (model_dir and os.path.isdir(model_dir)):
        raise RuntimeError(f"TEXT_MODEL_DIR invalid: {model_dir}")
    if not (labels_path and os.path.isfile(labels_path)):
        raise RuntimeError(f"TEXT_LABELS_PATH invalid: {labels_path}")

    with open(labels_path, "r") as f:
        labels = json.load(f)
    tok = AutoTokenizer.from_pretrained(model_dir)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_dir)
    mdl.eval()

    def pipe(text: str):
        inputs = tok(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = mdl(**inputs).logits[0].cpu().numpy()
        probs = _softmax(logits)  # ok for top_label (sigmoid is fine too if multi-label)
        return {labels[i]: float(probs[i]) for i in range(len(labels))}
    meta = _read_meta(model_dir, fallback_name="bert-goemotions")
    return labels, pipe, meta


def _load_audio_real():
    root_dir = _resolve_path(os.getenv("AUDIO_MODEL_DIR"))
    labels_path = _resolve_path(os.getenv("AUDIO_LABELS_PATH"))

    if not (root_dir and os.path.isdir(root_dir)):
        raise RuntimeError(f"AUDIO_MODEL_DIR invalid: {root_dir}")
    if not (labels_path and os.path.isfile(labels_path)):
        raise RuntimeError(f"AUDIO_LABELS_PATH invalid: {labels_path}")

    # Find TorchScript file
    ts_path = None
    for cand in ["model_best_ts.pt", "model.ts", "model_jit.pt"]:
        p = Path(root_dir) / cand
        if p.exists():
            ts_path = str(p)
            break
    if ts_path is None:
        # Check state_dict case and guide the user
        if (Path(root_dir) / "model_best_state.pt").exists():
            raise RuntimeError("Found model_best_state.pt but no TorchScript file. Please export TorchScript (model_best_ts.pt).")
        # Also check under checkpoint dirs just in case
        for p in Path(root_dir).rglob("model_best_ts.pt"):
            ts_path = str(p); break
    if ts_path is None:
        raise RuntimeError(f"No TorchScript file found under {root_dir} (looked for model_best_ts.pt).")

    # Load labels
    with open(labels_path, "r") as f:
        labels = json.load(f)
    num_labels = len(labels)

    # Load TorchScript
    model = torch.jit.load(ts_path, map_location="cpu")
    model.eval()

    # target sample rate (optional)
    target_sr = int(os.getenv("AUDIO_TARGET_SR", "16000"))

    def infer(path: str):
        wav, sr = torchaudio.load(path)# [C, T], float32 -1..1
        if wav.ndim == 2 and wav.size(0) > 1:
            wav = wav.mean(dim=0, keepdim=True)# mono
        if sr != target_sr:
            wav = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)(wav)
            sr = target_sr

        wav = wav.squeeze(0)# [T]

        # Feature extraction (adjust if needed to match training)
        # Reasonable defaults for CRDNN: 80 mel, 25ms window, 10ms hop, log-mel
        n_mels      = int(os.getenv("AUDIO_N_MELS", "80"))
        win_ms      = float(os.getenv("AUDIO_WIN_MS", "25"))
        hop_ms      = float(os.getenv("AUDIO_HOP_MS", "10"))
        n_fft       = int(os.getenv("AUDIO_N_FFT", "512"))

        win_length  = int(sr * win_ms / 1000.0)
        hop_length  = int(sr * hop_ms / 1000.0)

        melspec = torchaudio.transforms.MelSpectrogram(
            sample_rate=sr, n_fft=n_fft,
            win_length=win_length, hop_length=hop_length,
            n_mels=n_mels, center=True, power=2.0
        )
        mel = melspec(wav)# [n_mels, T_frames]
        mel = torchaudio.transforms.AmplitudeToDB(top_db=80)(mel)# log-mel
        mel = mel.transpose(0, 1) # [T_frames, n_mels]
        feats = mel.unsqueeze(0)# [B=1, T, n_mels]

        # SpeechBrain CRDNN expects relative lengths in [0,1]
        lens = torch.tensor([1.0], dtype=torch.float32)# full length

        with torch.no_grad():
            out = model(feats, lens)

        # Normalize to logits vector
        if isinstance(out, (list, tuple)):
            out = out[0]
        out = torch.as_tensor(out).float().squeeze()
        logits = out.cpu().numpy()

        if logits.shape[0] != num_labels:
            raise RuntimeError(f"Logits dim {logits.shape[0]} != labels {num_labels}. Adjust feature params or export wrapper.")
        probs = _softmax(logits)
        return {labels[i]: float(probs[i]) for i in range(num_labels)}


    meta = _read_meta(root_dir, fallback_name="torchscript-audio")
    return labels, infer, meta

def _ensure_text_loaded():
    if MODE == "REAL" and _TEXT["pipe"] is None:
        try:
            labels, pipe, meta = _load_text_real()
            _TEXT.update({"labels": labels, "pipe": pipe, "meta": meta})
            print(f"[model_adapters] TEXT loaded from {os.getenv('TEXT_MODEL_DIR')}", file=sys.stderr)
        except Exception as e:
            print(f"[model_adapters] TEXT load failed: {e}", file=sys.stderr)
    return _TEXT

def _ensure_audio_loaded():
    if MODE == "REAL" and _AUDIO["infer"] is None:
        try:
            labels, infer, meta = _load_audio_real()
            _AUDIO.update({"labels": labels, "infer": infer, "meta": meta})
            print(f"[model_adapters] AUDIO loaded from {os.getenv('AUDIO_MODEL_DIR')}", file=sys.stderr)
        except Exception as e:
            print(f"[model_adapters] AUDIO load failed: {e}", file=sys.stderr)
    return _AUDIO


def get_text_meta() -> dict:
    return _ensure_text_loaded()["meta"]

def get_audio_meta() -> dict:
    return _ensure_audio_loaded()["meta"]

# Inference APIs used by routes
def predict_text(text: str, lang: str | None):
    t = _ensure_text_loaded()
    if t["pipe"]:
        return t["pipe"](text)
    seed = _seed_from_bytes((text + "|" + (lang or "und")).encode("utf-8"))
    return _scores_from_seed(seed, t["labels"])

def predict_audio(audio_path: str, duration: float, sample_rate: int):
    a = _ensure_audio_loaded()
    if a["infer"]:
        return a["infer"](audio_path)
    seed = _seed_from_bytes(f"{audio_path}|{duration:.3f}|{sample_rate}".encode("utf-8"))
    return _scores_from_seed(seed, a["labels"])

