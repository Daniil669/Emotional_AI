# AI Development – Emotion Recognition

This folder contains all code and resources used for building and evaluating the AI models for emotion recognition from voice and text.

---

## Contents

| Folder       | Purpose                            |
|--------------|------------------------------------|
| `data/`      | Downloaded and preprocessed datasets |
| `models/`    | Trained model weights and wrappers  |
| `notebooks/` | Colab notebooks for exploration and fine-tuning |
| `scripts/`   | Python scripts for training, evaluation, and utilities |
| `feedback/`  | SQLite DB storing user corrections for analysis |

---

## Datasets Used

- `GoEmotions` (for text)
- `IEMOCAP` (for voice)

These are accessed via HuggingFace or manually downloaded and stored in `data/`.

---

## Goal

Train and evaluate:
- BERT (or similar) for text emotion classification
- SpeechBrain model for voice-based emotion detection

Compare their performance using standard metrics (accuracy, F1, confusion matrix).

---

## Getting Started

Install dependencies:

```bash
pip install datasets transformers speechbrain
