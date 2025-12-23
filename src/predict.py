import pickle
from pathlib import Path
from typing import Optional, Tuple

from .model_utils import normalize_text

_MODEL = None


def _load_model(path: Optional[str] = None):
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    model_path = Path(path) if path else Path(__file__).resolve().parents[0] / "artifacts" / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Run training first.")
    with open(model_path, "rb") as f:
        _MODEL = pickle.load(f)
    return _MODEL


def predict(text: str, model_path: Optional[str] = None) -> Tuple[str, float]:
    """Return (label, score) where label is 'FAKE' or 'REAL'.

    Score is a float in [0,1] indicating confidence (higher -> more likely predicted label).
    """
    model = _load_model(model_path)
    clean = normalize_text(text)

    if model["type"] == "sklearn":
        clf = model["model"]
        try:
            probs = clf.predict_proba([clean])[0]
            classes = clf.classes_
            # pick highest
            idx = int(probs.argmax())
            label = classes[idx]
            score = float(probs[idx])
            return label, score
        except Exception:
            # If predict_proba not available, fallback to predict
            label = clf.predict([clean])[0]
            return label, 0.5
    else:
        # rule-based
        text_tokens = clean.split()
        fake_hits = sum(1 for k in model.get("keywords_fake", []) if k in text_tokens)
        real_hits = sum(1 for k in model.get("keywords_real", []) if k in text_tokens)
        if fake_hits == real_hits:
            # default to REAL on tie
            return "REAL", 0.5
        label = "FAKE" if fake_hits > real_hits else "REAL"
        # confidence proportional to difference, normalized
        score = min(0.99, 0.5 + abs(fake_hits - real_hits) * 0.25)
        return label, float(score)


if __name__ == "__main__":
    # quick manual check
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Breaking: This miraculous cure will change your life!"
    lbl, sc = predict(text)
    print(lbl, sc)
