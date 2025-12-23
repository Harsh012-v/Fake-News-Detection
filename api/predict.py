from http.server import BaseHTTPRequestHandler
import json
import pickle
from pathlib import Path
import re

# Simple normalization to avoid complex local imports in serverless
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_model():
    # PATH: /var/task/src/artifacts/model.pkl on Vercel
    # Locally: relative from root
    model_path = Path(__file__).resolve().parent.parent / "src" / "artifacts" / "model.pkl"
    if not model_path.exists():
        # Fallback for different build environments
        model_path = Path("src/artifacts/model.pkl")
    
    with open(model_path, "rb") as f:
        return pickle.load(f)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        text = data.get("text", "")
        if not text:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "missing required field 'text'"}).encode())
            return

        try:
            model_data = load_model()
            clean = normalize_text(text)
            
            if model_data["type"] == "sklearn":
                clf = model_data["model"]
                probs = clf.predict_proba([clean])[0]
                classes = clf.classes_
                idx = int(probs.argmax())
                label = classes[idx]
                score = float(probs[idx])
            else:
                # rule-based fallback
                tokens = clean.split()
                fake_hits = sum(1 for k in model_data.get("keywords_fake", []) if k in tokens)
                real_hits = sum(1 for k in model_data.get("keywords_real", []) if k in tokens)
                
                if fake_hits == real_hits:
                    label, score = "REAL", 0.5
                elif fake_hits > real_hits:
                    label = "FAKE"
                    score = min(0.99, 0.5 + (fake_hits - real_hits) * 0.25)
                else:
                    label = "REAL"
                    score = min(0.99, 0.5 + (real_hits - fake_hits) * 0.25)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"label": label, "score": score}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        return
