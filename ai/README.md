# Emotion AI – AI Assets (Models, Metrics, Notebooks)

This folder contains **models, evaluation artifacts, and notebooks** for the Emotion AI thesis project.  
Two modalities are covered:

- **Text**: multi‑label emotion recognition (BERT), **sigmoid + thresholds**.
- **Audio**: single‑label speech emotion recognition (SpeechBrain), **softmax**.

Use these assets with the FastAPI backend (`server/`) via the model adapters.

---

## Layout

```
ai/
├─ models/
│  ├─ audio/
│  │  ├─ checkpoint/                 # trained weights/artifacts, not on github
│  │  └─ eval_test/
│  │     ├─ confusion_matrix_counts.png
│  │     ├─ confusion_matrix_rownorm.png
│  │     ├─ confusion_matrix.npy
│  │     ├─ metrics_overall.json
│  │     ├─ metrics_report.csv
│  │     ├─ labels.json
│  │     └─ model_meta.json
│  └─ text/
│     ├─ eval_test/
│     │  ├─ inference_config.json    # thresholds, top-k, etc.
│     │  ├─ metrics_overall.json
│     │  └─ per_class_metrics_test.csv
│     └─ model/
│        ├─ inference_config.json    # tokenizer/model names, max_len, etc.
│        ├─ labels.json              # ordered label list (27 + neutral)
│        └─ model_meta.json          # training seed, dataset info, notes
├─ notebooks/
│  ├─ audio_emotion_data_prep.ipynb  # audio dataset prep (e.g., RAVDESS)
│  ├─ finetuning_audio_model.ipynb   # SpeechBrain training
│  ├─ finetuning_text_model.ipynb    # BERT training
│  └─ text_emotion_data_prep.ipynb   # GoEmotions prep
└─ scripts/
   └─ plot_confusion_matrix.py
```

> Large binary files are excluded.

---

## What’s in the JSON/CSV files?

### Common
- **`model_meta.json`** – human‑readable metadata (model name, dataset, classes, seed, date, notes).
- **`labels.json`** – ordered list of class names used by the model.

### Text (multi‑label)
- **`inference_config.json`** – tokenizer model name, max sequence length, post‑processing parameters such as **per‑class thresholds** or global threshold, `top_k`, etc.
- **`metrics_overall.json`** – global metrics (micro/macro F1, precision, recall, AUROC, etc. depending on the notebook output).
- **`per_class_metrics_test.csv`** – per‑label precision/recall/F1 and support.

### Audio (single‑label)
- **`metrics_overall.json`** – accuracy, macro F1, etc.
- **`metrics_report.csv`** – per‑class classification report.
- **`confusion_matrix.npy/png`** – raw matrix (`.npy`) and rendered figures (counts and row‑normalized).

---

## Modalities & Heads

- **Text**: BERT‑based, **sigmoid** output for multi‑label. Evaluation uses thresholding (global or per‑class) to decide positive labels.
- **Audio**: SpeechBrain model with **softmax** over discrete emotions (single best label).

These choices are reflected in the evaluation artifacts and in the backend’s result formatting.

---

## Using with the Backend

The FastAPI server can load real models via its adapters (see `server/utils/model_adapters.py`).  
Point the adapters to your exported checkpoints and configs, for example via environment variables:

```
# server/.env (example)
TEXT_MODEL_DIR=ai/models/text/model
AUDIO_MODEL_DIR=ai/models/audio/checkpoint
USE_MOCK_MODELS=false
```

Make sure the following are present in the assigned directories:
- **Text**: `labels.json`, `inference_config.json`, and the model checkpoint (HuggingFace format).
- **Audio**: `labels.json` and the SpeechBrain checkpoint directory (plus any required `hyperparams.yaml` if your setup uses it).

If no real models are found, the server falls back to deterministic **mock** models (useful for dev to how the app works without real models).

---

## Notebooks (Reproducibility)

1. **`text_emotion_data_prep.ipynb`** – clean/simplify GoEmotions, generate splits and label lists.
2. **`finetuning_text_model.ipynb`** – fine‑tune BERT, export model, write `inference_config.json`, compute metrics.
3. **`audio_emotion_data_prep.ipynb`** – prepare audio dataset (e.g., RAVDESS), resampling, labeling, splits.
4. **`finetuning_audio_model.ipynb`** – train SpeechBrain model, export checkpoint, compute metrics & confusion matrices.

> The notebooks are designed for Colab but should also run on a local GPU environment with minor path changes.

---

## Plotting Utilities

`scripts/plot_confusion_matrix.py` renders a confusion matrix from a saved `.npy` file.

Example:
```bash
python scripts/plot_confusion_matrix.py   --input ai/models/audio/eval_test/confusion_matrix.npy   --labels ai/models/audio/eval_test/labels.json   --output ai/models/audio/eval_test/confusion_matrix_counts.png   --normalize none      # or: row
```

---
