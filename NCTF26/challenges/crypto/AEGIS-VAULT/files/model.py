import math
import os
import numpy as np
D = 24
DEMB = 40
S = 255.0
C0 = -1.5
CLASSES = ["OTHER", "SEALED"]
SEALED = 1
OTHER = 0
_HERE = os.path.dirname(os.path.abspath(__file__))
class Vault:
    def __init__(self, weights_path: str | None = None):
        if weights_path is None:
            weights_path = os.path.join(_HERE, "weights.npz")
        with np.load(weights_path) as z:
            self.E = z["E"].astype(np.float64)
        self.M = self.E.T @ self.E
    def score(self, probe, record) -> float:
        p = np.asarray(probe, dtype=np.float64).reshape(D)
        r = np.asarray(record, dtype=np.float64).reshape(D)
        return float((p / S) @ self.M @ (r / S)) + C0
    def confidence(self, probe, record) -> dict:
        s = self.score(probe, record)
        z = np.array([0.0, s], dtype=np.float64)
        z = z - z.max()
        e = np.exp(z)
        prob = e / e.sum()
        return {"OTHER": float(prob[0]), "SEALED": float(prob[1])}
