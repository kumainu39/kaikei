"""AI classifier stub that can load an ML model when available."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

import logging

from utils.logging_config import setup_logging
from utils.settings import settings

setup_logging()
logger = logging.getLogger(__name__)


class AIClassifier:
    def __init__(self) -> None:
        self.model = None
        self.vectorizer = None
        self._load_models()

    def _load_models(self) -> None:
        model_path = Path(settings.ai_model_path)
        vectorizer_path = Path(settings.ai_vectorizer_path)
        if model_path.exists() and vectorizer_path.exists():
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)

    def predict(self, summary: str, amount: float) -> dict[str, Any]:
        if self.model and self.vectorizer:
            vector = self.vectorizer.transform([summary])
            prediction = self.model.predict(vector)[0]
            return {"debit": prediction.get("debit"), "credit": prediction.get("credit")}
        logger.info("AI model unavailable, returning neutral prediction")
        return {"debit": None, "credit": None}


def get_classifier() -> AIClassifier:
    return AIClassifier()
