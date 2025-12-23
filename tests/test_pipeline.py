import os
import unittest
from pathlib import Path

import sys
# ensure src package is importable when tests are run from workspace root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import train, predict


class PipelineTests(unittest.TestCase):
    def test_train_and_predict(self):
        # Train model (uses built-in samples)
        model_path = train.train_and_save()
        self.assertTrue(Path(model_path).exists())

        # Predict on a known fake-like string
        lbl, sc = predict.predict("This miracle cure will change your life!", model_path=model_path)
        self.assertIn(lbl, ("FAKE", "REAL"))
        self.assertIsInstance(sc, float)


if __name__ == "__main__":
    unittest.main()
