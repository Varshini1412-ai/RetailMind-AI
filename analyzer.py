"""
TextAnalyzer wraps two pre-trained Hugging Face pipelines:
  1. Sentiment analysis (positive / negative)
  2. Emotion classification (joy, anger, sadness, fear, surprise, etc.)

Using pre-trained models means no training data or GPU is needed -
perfect for a hackathon timeline while still giving genuine NLP results.
"""

from transformers import pipeline


class TextAnalyzer:
    def __init__(self):
        # distilbert-base-uncased-finetuned-sst-2-english: fast, reliable
        # binary sentiment classifier (POSITIVE / NEGATIVE).
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )

        # j-hartmann/emotion-english-distilroberta-base: classifies text
        # into 7 emotions (anger, disgust, fear, joy, neutral, sadness, surprise).
        self.emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
        )

    def analyze(self, text: str) -> dict:
        """
        Runs both pipelines on a single string of text.
        Returns a dict with top sentiment and top emotion, plus full
        emotion distribution (useful for radar/bar charts on the frontend).
        """
        sentiment_result = self.sentiment_pipeline(text)[0]

        emotion_scores = self.emotion_pipeline(text)[0]
        emotion_scores_sorted = sorted(
            emotion_scores, key=lambda x: x["score"], reverse=True
        )
        top_emotion = emotion_scores_sorted[0]

        return {
            "sentiment": {
                "label": sentiment_result["label"],
                "score": round(float(sentiment_result["score"]), 4),
            },
            "emotion": {
                "label": top_emotion["label"],
                "score": round(float(top_emotion["score"]), 4),
            },
            "emotion_distribution": [
                {"label": e["label"], "score": round(float(e["score"]), 4)}
                for e in emotion_scores_sorted
            ],
        }
