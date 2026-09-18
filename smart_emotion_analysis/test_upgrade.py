"""
Comprehensive test script for AI YouTube Comment Intelligence upgrade.
Validates backwards compatibility, model integrity, parsers, and Flask endpoints.
"""

import io
import json
import unittest
from app import app
from models.sentiment_analyzer import SentimentAnalyzer
from models.emotion_analyzer import EmotionAnalyzer
from models.toxicity_analyzer import ToxicityAnalyzer
from models.quality_scorer import QualityScorer
from utils.comment_parser import CommentParser
from utils.demo_data import get_demo_comments
from utils.data_manager import DataManager


class TestYouTubeCommentIntelligence(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.data_manager = DataManager()

    # 1. Backwards Compatibility: Sentiment & Emotion
    def test_sentiment_analyzer(self):
        analyzer = SentimentAnalyzer()
        sent, scores = analyzer.analyze("This tutorial is absolutely amazing!")
        self.assertEqual(sent, "Positive")
        self.assertGreater(scores["compound"], 0.05)

        sent_neg, scores_neg = analyzer.analyze("This is awful and broken.")
        self.assertEqual(sent_neg, "Negative")
        self.assertLess(scores_neg["compound"], -0.05)

    def test_emotion_analyzer(self):
        analyzer = EmotionAnalyzer()
        emo, scores = analyzer.analyze("I am so happy and excited about this!")
        self.assertEqual(emo, "happiness")
        self.assertIn("happiness", scores)
        self.assertIn("sadness", scores)
        self.assertIn("anger", scores)
        self.assertIn("fear", scores)
        self.assertIn("surprise", scores)
        self.assertIn("neutral", scores)

    # 2. Toxicity Analyzer
    def test_toxicity_analyzer(self):
        tox = ToxicityAnalyzer()
        # Safe comment
        res_safe = tox.analyze("Great job on the code walkthrough!")
        self.assertFalse(res_safe["is_toxic"])
        self.assertEqual(res_safe["status"], "Safe")

        # Toxic insult/harassment
        res_toxic = tox.analyze("You are an idiot, shut up and delete your channel loser.")
        self.assertTrue(res_toxic["is_toxic"])
        self.assertEqual(res_toxic["status"], "Toxic")
        self.assertIn("insult", res_toxic["categories"])

    # 3. Quality Scorer & Constructive Feedback
    def test_quality_scorer(self):
        scorer = QualityScorer()
        tox_info = {"is_toxic": False, "toxicity_score": 0.0, "status": "Safe"}

        # Constructive critique
        res_constructive = scorer.evaluate_comment(
            text="The video was great, but step 3 at 08:45 was too fast. Could you explain the auth flow next time?",
            sentiment="Neutral",
            sentiment_compound=0.0,
            toxicity_info=tox_info,
            likes=45
        )
        self.assertTrue(res_constructive["is_constructive"])
        self.assertEqual(res_constructive["feedback_type"], "Constructive Feedback")
        self.assertGreaterEqual(res_constructive["quality_score"], 65)

        # Spam/low effort
        res_spam = scorer.evaluate_comment(
            text="first",
            sentiment="Neutral",
            sentiment_compound=0.0,
            toxicity_info=tox_info,
            likes=0
        )
        self.assertLess(res_spam["quality_score"], 35)

    # 4. Comment Parser
    def test_comment_parser_csv(self):
        csv_data = (
            "author,comment,likes\n"
            "Alice,Fantastic explanation!,12\n"
            "Bob,Could you slow down step 2?,5\n"
        ).encode("utf-8")
        parsed = CommentParser.parse_csv_content(csv_data)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["author"], "Alice")
        self.assertEqual(parsed[0]["likes"], 12)

    def test_youtube_url_extractor(self):
        self.assertEqual(CommentParser.extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(CommentParser.extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(CommentParser.extract_youtube_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    # 5. Flask Endpoints
    def test_single_text_analyze_endpoint(self):
        response = self.client.post("/analyze", data={"text": "I am so proud and happy with my results!"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"happiness", response.data.lower())
        self.assertIn(b"positive", response.data.lower())

    def test_all_pages_render_200(self):
        pages = [
            "/",
            "/dashboard",
            "/youtube-comments",
            "/comments",
            "/top-comments",
            "/negative-comments",
            "/emotions",
            "/insights",
            "/history",
            "/report"
        ]
        for page in pages:
            res = self.client.get(page)
            self.assertEqual(res.status_code, 200, f"Failed on page: {page}")

    def test_api_batch_analyze(self):
        # Ingest demo data
        res = self.client.post("/api/analyze-comments", data={"is_demo": "true"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        session_id = data["session_id"]
        self.assertTrue(session_id.startswith("sess_"))

        # Fetch session
        res_sess = self.client.get(f"/api/session/{session_id}")
        self.assertEqual(res_sess.status_code, 200)
        sess_data = res_sess.get_json()
        self.assertIn("metrics", sess_data)
        self.assertIn("insights", sess_data)
        self.assertIn("best_comments", sess_data)

        # Export CSV
        res_export_csv = self.client.get(f"/api/export/{session_id}?format=csv")
        self.assertEqual(res_export_csv.status_code, 200)
        self.assertEqual(res_export_csv.mimetype, "text/csv")

        # Export JSON
        res_export_json = self.client.get(f"/api/export/{session_id}?format=json")
        self.assertEqual(res_export_json.status_code, 200)
        self.assertEqual(res_export_json.mimetype, "application/json")

        # Delete session
        res_del = self.client.delete(f"/api/history/{session_id}")
        self.assertEqual(res_del.status_code, 200)


if __name__ == "__main__":
    unittest.main()
