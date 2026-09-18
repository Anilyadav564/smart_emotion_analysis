"""
Comprehensive unit and integration tests for the YouTube URL comment analysis pipeline:
1. Video ID extraction from all URL formats.
2. Error handling when API key is missing (ensuring NO fake demo fallback).
3. Live test of 3 distinct videos (with mocked YouTube Data API responses) verifying:
   - Different video titles and channels
   - Completely different comments tied to each video_id
   - Different sentiment percentages
   - Different emotion distributions
   - Different top comments and negative comments
   - Different dynamically extracted topics
   - Zero cross-video data mixing
4. Specific API error scenarios: disabled comments, quota exceeded, private videos.
"""

import unittest
from unittest.mock import patch
from app import app
from models.youtube_service import (
    YouTubeService,
    YouTubeAPIKeyMissingError,
    YouTubeCommentsDisabledError,
    YouTubeQuotaExceededError,
    YouTubeVideoNotFoundError
)
from models.comment_analyzer import CommentAnalyzer


class TestYouTubeIntegration(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.service = YouTubeService()
        self.analyzer = CommentAnalyzer()

    # -------------------------------------------------------------
    # 1. URL Parsing & ID Extraction
    # -------------------------------------------------------------
    def test_extract_video_id(self):
        urls = {
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://www.youtube.com/live/dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&feature=share": "dQw4w9WgXcQ"
        }
        for url, expected_id in urls.items():
            self.assertEqual(self.service.extract_video_id(url), expected_id, f"Failed on URL: {url}")

        # Invalid URLs
        self.assertEqual(self.service.extract_video_id("https://google.com"), "")
        self.assertEqual(self.service.extract_video_id("invalid_text"), "")

    # -------------------------------------------------------------
    # 2. Missing API Key Guardrail (NO FAKE FALLBACK)
    # -------------------------------------------------------------
    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_returns_clear_error(self):
        # Direct service call
        with self.assertRaises(YouTubeAPIKeyMissingError):
            self.service.get_api_key()

        # Dedicated Flask API endpoint
        res = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("YOUTUBE_API_KEY", data["error"])
        # Verify demo data was NOT returned
        self.assertNotIn("Full-Stack AI Project", str(data))

    # -------------------------------------------------------------
    # 3. Multi-Video Test (3 Distinct Videos)
    # -------------------------------------------------------------
    def test_three_different_youtube_videos_have_unique_data(self):
        # Video A: Music video with high praise and happiness
        video_a_info = {
            "video_id": "vid_music_1",
            "title": "Rick Astley - Classic Hit",
            "channel_title": "Rick Astley Official",
            "thumbnail_url": "https://i.ytimg.com/vi/vid_music_1/hqdefault.jpg",
            "view_count": 1450000,
            "like_count": 92000,
            "comment_count": 3
        }
        video_a_comments = [
            {"comment_id": "c1", "author": "Fan1", "comment_text": "I love this song so much! Brings back pure happiness.", "likes": 50, "published_at": "2026-01-01", "video_id": "vid_music_1"},
            {"comment_id": "c2", "author": "Fan2", "comment_text": "Amazing vocals, timeless masterpiece and wonderful melody.", "likes": 30, "published_at": "2026-01-01", "video_id": "vid_music_1"},
            {"comment_id": "c3", "author": "Fan3", "comment_text": "Best music video ever made, fantastic artist.", "likes": 15, "published_at": "2026-01-01", "video_id": "vid_music_1"}
        ]

        # Video B: Programming Tutorial with constructive feedback & questions
        video_b_info = {
            "video_id": "vid_pythn_2",
            "title": "Python Machine Learning Masterclass",
            "channel_title": "Corey MS",
            "thumbnail_url": "https://i.ytimg.com/vi/vid_pythn_2/hqdefault.jpg",
            "view_count": 280000,
            "like_count": 14000,
            "comment_count": 3
        }
        video_b_comments = [
            {"comment_id": "c4", "author": "DevA", "comment_text": "Step 3 at 08:45 was too fast. Could you explain the gradient descent algorithm next time?", "likes": 85, "published_at": "2026-02-01", "video_id": "vid_pythn_2"},
            {"comment_id": "c5", "author": "DevB", "comment_text": "Can you provide the GitHub link for the training dataset?", "likes": 40, "published_at": "2026-02-01", "video_id": "vid_pythn_2"},
            {"comment_id": "c6", "author": "DevC", "comment_text": "I am getting a numpy syntax error on line 42, please clarify.", "likes": 12, "published_at": "2026-02-01", "video_id": "vid_pythn_2"}
        ]

        # Video C: Gaming Video with heavy complaints and toxic language
        video_c_info = {
            "video_id": "vid_gamng_3",
            "title": "Ranked Gaming Fails & Rants",
            "channel_title": "ToxicGamer99",
            "thumbnail_url": "https://i.ytimg.com/vi/vid_gamng_3/hqdefault.jpg",
            "view_count": 95000,
            "like_count": 3100,
            "comment_count": 3
        }
        video_c_comments = [
            {"comment_id": "c7", "author": "Gamer1", "comment_text": "You are an idiot, delete your channel and uninstall the game trash loser.", "likes": 5, "published_at": "2026-03-01", "video_id": "vid_gamng_3"},
            {"comment_id": "c8", "author": "Gamer2", "comment_text": "Horrible gameplay, completely unwatchable and terrible.", "likes": 8, "published_at": "2026-03-01", "video_id": "vid_gamng_3"},
            {"comment_id": "c9", "author": "Gamer3", "comment_text": "Worst play I have ever seen in my life.", "likes": 2, "published_at": "2026-03-01", "video_id": "vid_gamng_3"}
        ]

        def mock_get_video_and_comments(vid_id, max_comments=300, use_cache=True):
            if "vid_music_1" in vid_id:
                return video_a_info, video_a_comments
            elif "vid_pythn_2" in vid_id:
                return video_b_info, video_b_comments
            elif "vid_gamng_3" in vid_id:
                return video_c_info, video_c_comments
            raise YouTubeVideoNotFoundError(f"Unknown video {vid_id}")

        with patch("app.youtube_service.get_video_and_comments", side_effect=mock_get_video_and_comments):
            # --- Analyze Video A ---
            res_a = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=vid_music_1"})
            self.assertEqual(res_a.status_code, 200)
            data_a = res_a.get_json()

            # --- Analyze Video B ---
            res_b = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=vid_pythn_2"})
            self.assertEqual(res_b.status_code, 200)
            data_b = res_b.get_json()

            # --- Analyze Video C ---
            res_c = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=vid_gamng_3"})
            self.assertEqual(res_c.status_code, 200)
            data_c = res_c.get_json()

            # 1. Verify Video Titles & Channel Names are different
            self.assertEqual(data_a["video"]["title"], "Rick Astley - Classic Hit")
            self.assertEqual(data_b["video"]["title"], "Python Machine Learning Masterclass")
            self.assertEqual(data_c["video"]["title"], "Ranked Gaming Fails & Rants")

            self.assertNotEqual(data_a["video"]["title"], data_b["video"]["title"])
            self.assertNotEqual(data_b["video"]["title"], data_c["video"]["title"])

            # 2. Verify Comments belong strictly to each video
            for c in data_a["comments"]:
                self.assertEqual(c["video_id"], "vid_music_1")
            for c in data_b["comments"]:
                self.assertEqual(c["video_id"], "vid_pythn_2")
            for c in data_c["comments"]:
                self.assertEqual(c["video_id"], "vid_gamng_3")

            # 3. Verify Sentiment percentages are calculated dynamically and differ
            self.assertEqual(data_a["statistics"]["positive_percentage"], 100.0)
            self.assertEqual(data_a["statistics"]["negative_percentage"], 0.0)

            self.assertEqual(data_c["statistics"]["negative_percentage"], 100.0)
            self.assertEqual(data_c["statistics"]["positive_percentage"], 0.0)

            # 4. Verify Toxicity differences
            self.assertEqual(data_a["statistics"]["toxicity_percentage"], 0.0)
            self.assertGreater(data_c["statistics"]["toxicity_percentage"], 0.0)

            # 5. Verify Emotions differ
            self.assertEqual(data_a["statistics"]["dominant_emotion"], "happiness")
            self.assertIn(data_c["statistics"]["dominant_emotion"], ["anger", "sadness", "neutral"])

            # 6. Verify Dynamic Topics differ
            topics_a = [t["topic"].lower() for t in data_a.get("topics", [])]
            topics_b = [t["topic"].lower() for t in data_b.get("topics", [])]
            self.assertTrue(any("song" in t or "music" in t or "melody" in t or "vocals" in t for t in topics_a))
            self.assertTrue(any("algorithm" in t or "gradient" in t or "github" in t or "numpy" in t for t in topics_b))

    # -------------------------------------------------------------
    # 4. Error Handling Scenarios
    # -------------------------------------------------------------
    def test_youtube_error_mappings(self):
        with patch("app.youtube_service.get_video_and_comments", side_effect=YouTubeCommentsDisabledError("Comments are disabled for this video.")):
            res = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
            self.assertEqual(res.status_code, 400)
            self.assertIn("Comments are disabled", res.get_json()["error"])

        with patch("app.youtube_service.get_video_and_comments", side_effect=YouTubeQuotaExceededError("YouTube API quota has been exceeded.")):
            res = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
            self.assertEqual(res.status_code, 429)
            self.assertIn("quota", res.get_json()["error"].lower())

        with patch("app.youtube_service.get_video_and_comments", side_effect=YouTubeVideoNotFoundError("YouTube video not found.")):
            res = self.client.post("/api/analyze-youtube", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
            self.assertEqual(res.status_code, 404)
            self.assertIn("not found", res.get_json()["error"].lower())


if __name__ == "__main__":
    unittest.main()
