import os
import pickle
from pathlib import Path
from typing import List, Dict

from .model_utils import normalize_text


DEFAULT_ARTIFACT_DIR = Path(__file__).resolve().parents[0] / "artifacts"
DEFAULT_MODEL_PATH = DEFAULT_ARTIFACT_DIR / "model.pkl"


def _default_samples() -> List[Dict[str, str]]:
    # Small built-in samples for MVP/demo and smoke tests
    return [
        {"text": "President signs new law to improve healthcare", "label": "REAL"},
        {"text": "Scientists confirm vaccine is safe and effective", "label": "REAL"},
        {"text": "Shocking! Celebrity endorses miracle cure - click to find out", "label": "FAKE"},
        {"text": "This one weird trick doctors hate — cure for diabetes!", "label": "FAKE"},
        {"text": "Report: local council approves new park", "label": "REAL"},
        {"text": "BREAKING: Aliens landed in my backyard, video inside", "label": "FAKE"},
    ]


def train_and_save(model_path: str = None):
    """Train a model.

    Attempts to use scikit-learn if available. If scikit-learn isn't installed,
    falls back to a lightweight rule-based classifier so the repo can run
    without extra packages (useful for quick MVP/demo).

    Saves model to `model_path` (default: artifacts/model.pkl).

    Returns the path where the model was saved as a string.
    """
    model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    model_path.parent.mkdir(parents=True, exist_ok=True)

    samples = _default_samples()
    texts = [normalize_text(s["text"]) for s in samples]
    labels = [s["label"] for s in samples]

    try:
        # Try to use scikit-learn pipeline for a better baseline
        from sklearn.pipeline import Pipeline
        from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
        from sklearn.linear_model import LogisticRegression

        clf = Pipeline(
            [
                ("vect", CountVectorizer()),
                ("tfidf", TfidfTransformer()),
                ("clf", LogisticRegression(max_iter=1000)),
            ]
        )
        clf.fit(texts, labels)
        model = {"type": "sklearn", "model": clf}
    except Exception:
        # Fallback: simple keyword rule-based model (no external deps)
        keywords_fake = ["miracle", "click", "shocking", "cure", "weird", "video", "aliens"]
        keywords_real = ["report", "said", "confirmed", "approves", "signed", "president", "scientist"]
        model = {"type": "rule", "keywords_fake": keywords_fake, "keywords_real": keywords_real}

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return str(model_path)


if __name__ == "__main__":
    path = train_and_save()
    print("Saved model to:", path)
