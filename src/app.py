from flask import Flask, request, jsonify
from pathlib import Path

from .predict import predict

app = Flask(__name__)
MODEL_PATH = Path(__file__).resolve().parents[0] / "artifacts" / "model.pkl"


@app.route("/predict", methods=["POST"])
def predict_route():
    data = request.get_json(force=True)
    if not data or "text" not in data:
        return jsonify({"error": "missing required field 'text'"}), 400
    text = data["text"]
    try:
        label, score = predict(text, model_path=str(MODEL_PATH))
    except FileNotFoundError:
        return jsonify({"error": "model not found. Please run training first."}), 500
    return jsonify({"label": label, "score": score})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
