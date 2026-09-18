from utils.text_preprocessing import TextPreprocessor
from models.emotion_analyzer import EmotionAnalyzer
from models.sentiment_analyzer import SentimentAnalyzer
from models.comment_analyzer import CommentAnalyzer


class AnalysisService:

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.emotion_analyzer = EmotionAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.comment_analyzer = CommentAnalyzer()

    def analyze_text(self, text):
        """Original single-text analysis method preserved 100%."""
        # Step 1: Clean text
        cleaned_text = self.preprocessor.clean_text(text)

        # Step 2: Analyze emotion
        primary_emotion, emotion_scores = \
            self.emotion_analyzer.analyze(cleaned_text)

        # Step 3: Analyze sentiment
        sentiment, sentiment_scores = \
            self.sentiment_analyzer.analyze(cleaned_text)

        # Step 4: Return complete result
        result = {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_scores,
            "sentiment": sentiment,
            "sentiment_scores": sentiment_scores
        }

        return result

    def analyze_comments(self, comments: list, video_title: str = "YouTube Video Analysis",
                         video_info: dict = None) -> dict:
        """Batch YouTube comment analysis pipeline with optional real video metadata."""
        return self.comment_analyzer.process_comments(comments, video_title=video_title, video_info=video_info)