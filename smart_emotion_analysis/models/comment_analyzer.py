import math
import re
import uuid
from collections import Counter
from datetime import datetime

from utils.text_preprocessing import TextPreprocessor
from models.sentiment_analyzer import SentimentAnalyzer
from models.emotion_analyzer import EmotionAnalyzer
from models.toxicity_analyzer import ToxicityAnalyzer
from models.quality_scorer import QualityScorer


# Common English stop words to exclude from keyword / topic extraction
STOP_WORDS = {
    "the", "and", "is", "in", "to", "of", "for", "a", "an", "this", "that", "it",
    "with", "as", "on", "at", "by", "from", "you", "your", "my", "me", "we", "our",
    "us", "they", "them", "their", "he", "she", "his", "her", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "but", "if", "or",
    "because", "so", "than", "too", "very", "just", "about", "all", "any", "some",
    "can", "will", "would", "should", "could", "there", "when", "where", "how", "what",
    "which", "who", "why", "video", "watch", "watching", "like", "good", "great",
    "nice", "really", "much", "more", "make", "made", "get", "got", "also", "one",
    "know", "see", "think", "time", "day", "even", "then", "now", "well", "way",
    "here", "only", "out", "up", "down", "into", "over", "after", "before", "most",
    "other", "these", "those", "first", "hello", "view", "viewer", "channel", "thank",
    "thanks", "please", "still", "such", "back", "many", "next", "always", "never",
    "ever", "sure", "keep", "love", "loved", "best", "awesome", "comment", "comments"
}


class CommentAnalyzer:
    """
    Core batch processing engine for AI YouTube Comment Intelligence.
    Orchestrates cleaning, sentiment, emotion, toxicity, quality scoring,
    top-tier ranking, dynamic audience insights, and topic extraction.
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.toxicity_analyzer = ToxicityAnalyzer()
        self.quality_scorer = QualityScorer()

    def process_comments(self, comments: list, video_title: str = "YouTube Video Analysis",
                         video_info: dict = None) -> dict:
        """
        Executes full analysis pipeline across a list of comments.
        Returns a rich session dictionary with metrics, ranked categories, insights, and topics.
        """
        if not comments:
            return self._empty_result(video_title, video_info)

        analyzed_comments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        emotion_totals = {
            "happiness": 0,
            "sadness": 0,
            "anger": 0,
            "fear": 0,
            "surprise": 0,
            "neutral": 0
        }
        toxic_count = 0
        constructive_count = 0
        total_quality_score = 0

        # Step 1 & 2: Process individual comments
        for c in comments:
            raw_text = c.get("comment_text") or c.get("text") or ""
            raw_text = str(raw_text).strip()
            if not raw_text:
                continue

            cleaned_text = self.preprocessor.clean_text(raw_text)
            likes = int(c.get("likes", 0))

            # Analyzers
            sentiment, sentiment_scores = self.sentiment_analyzer.analyze(cleaned_text or raw_text)
            primary_emotion, emotion_scores = self.emotion_analyzer.analyze(cleaned_text or raw_text)
            toxicity_info = self.toxicity_analyzer.analyze(raw_text)
            quality_info = self.quality_scorer.evaluate_comment(
                text=raw_text,
                sentiment=sentiment,
                sentiment_compound=sentiment_scores.get("compound", 0.0),
                toxicity_info=toxicity_info,
                likes=likes
            )

            # Best comment composite score calculation
            compound = sentiment_scores.get("compound", 0.0)
            engagement_boost = min(15.0, math.log10(likes + 1) * 6.0)
            constructive_boost = 12.0 if quality_info["is_constructive"] else 0.0
            sentiment_boost = (compound + 1.0) * 15.0  # Range: 0 to 30
            toxicity_penalty = toxicity_info["toxicity_score"] * 60.0

            best_score = round(
                (quality_info["quality_score"] * 0.4) +
                sentiment_boost +
                engagement_boost +
                constructive_boost -
                toxicity_penalty,
                1
            )

            # Accumulate overall stats
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            if toxicity_info["is_toxic"]:
                toxic_count += 1
            if quality_info["is_constructive"]:
                constructive_count += 1
            total_quality_score += quality_info["quality_score"]

            for emo, sc in emotion_scores.items():
                emotion_totals[emo] = emotion_totals.get(emo, 0) + sc

            analyzed_item = {
                "comment_id": c.get("comment_id") or ("c_" + uuid.uuid4().hex[:8]),
                "author": c.get("author") or "Anonymous Viewer",
                "comment_text": raw_text,
                "cleaned_text": cleaned_text,
                "likes": likes,
                "reply_count": c.get("reply_count", 0),
                "published_at": c.get("published_at") or datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_at": c.get("updated_at") or "",
                "video_id": c.get("video_id") or (video_info.get("video_id") if video_info else ""),
                "sentiment": sentiment,
                "sentiment_scores": sentiment_scores,
                "primary_emotion": primary_emotion,
                "emotion_scores": emotion_scores,
                "toxicity": toxicity_info,
                "quality": quality_info,
                "best_score": best_score,
                "is_favorite": False
            }
            analyzed_comments.append(analyzed_item)

        total_analyzed = len(analyzed_comments)
        if total_analyzed == 0:
            return self._empty_result(video_title, video_info)

        # Percentages
        pos_pct = round((sentiment_counts["Positive"] / total_analyzed) * 100, 1)
        neu_pct = round((sentiment_counts["Neutral"] / total_analyzed) * 100, 1)
        neg_pct = round((sentiment_counts["Negative"] / total_analyzed) * 100, 1)
        toxic_pct = round((toxic_count / total_analyzed) * 100, 1)
        avg_quality = round(total_quality_score / total_analyzed, 1)

        # Dominant emotion calculation
        dominant_emotion = max(emotion_totals, key=emotion_totals.get)
        total_emo_hits = sum(emotion_totals.values()) or 1
        dominant_emotion_pct = round((emotion_totals[dominant_emotion] / total_emo_hits) * 100, 1)

        # Dynamic interpretation for emotions
        emotion_interpretation = self._generate_emotion_interpretation(
            dominant_emotion, dominant_emotion_pct, pos_pct, neg_pct, emotion_totals
        )

        # Categorized comments
        safe_comments = [c for c in analyzed_comments if not c["toxicity"]["is_toxic"]]
        best_comments = sorted(safe_comments, key=lambda x: x["best_score"], reverse=True)[:10]

        constructive_comments = [c for c in safe_comments if c["quality"]["is_constructive"]]
        constructive_comments = sorted(constructive_comments, key=lambda x: (x["quality"]["quality_score"], x["likes"]), reverse=True)[:10]

        most_engaged = sorted(analyzed_comments, key=lambda x: x["likes"], reverse=True)[:10]
        most_positive = sorted(
            [c for c in safe_comments if c["sentiment"] == "Positive"],
            key=lambda x: x["sentiment_scores"].get("compound", 0),
            reverse=True
        )[:10]

        negative_all = [c for c in analyzed_comments if c["sentiment"] == "Negative" or c["toxicity"]["is_toxic"]]
        constructive_criticism = [c for c in negative_all if c["quality"]["feedback_type"] == "Constructive Feedback"]
        critical_complaints = [c for c in negative_all if c["quality"]["feedback_type"] == "Critical Complaint"]
        toxic_comments = [c for c in analyzed_comments if c["toxicity"]["is_toxic"]]

        # AI Insights Synthesis
        insights = self._generate_insights(
            analyzed_comments, pos_pct, neu_pct, neg_pct, toxic_pct,
            constructive_comments, critical_complaints, toxic_comments, dominant_emotion
        )

        # Dynamic Topic / Keyword Extraction
        topics = self._extract_topics(analyzed_comments, top_n=10)

        resolved_title = (video_info.get("title") if video_info else None) or video_title or "YouTube Video Analysis"
        resolved_channel = (video_info.get("channel_title") if video_info else None) or "YouTube Channel"
        resolved_video_id = (video_info.get("video_id") if video_info else None) or ""

        session_id = "sess_" + uuid.uuid4().hex[:10]
        session_data = {
            "session_id": session_id,
            "video_id": resolved_video_id,
            "video_title": resolved_title,
            "channel_name": resolved_channel,
            "video_info": video_info or {
                "video_id": resolved_video_id,
                "title": resolved_title,
                "channel_title": resolved_channel,
                "thumbnail_url": "",
                "view_count": 0,
                "like_count": 0,
                "comment_count": total_analyzed
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_comments": total_analyzed,
            "metrics": {
                "total_comments": total_analyzed,
                "positive_count": sentiment_counts["Positive"],
                "positive_percentage": pos_pct,
                "neutral_count": sentiment_counts["Neutral"],
                "neutral_percentage": neu_pct,
                "negative_count": sentiment_counts["Negative"],
                "negative_percentage": neg_pct,
                "toxic_count": toxic_count,
                "toxicity_percentage": toxic_pct,
                "constructive_count": constructive_count,
                "constructive_percentage": round((constructive_count / total_analyzed) * 100, 1),
                "average_quality": avg_quality,
                "dominant_emotion": dominant_emotion,
                "dominant_emotion_percentage": dominant_emotion_pct,
                "emotion_totals": emotion_totals,
                "emotion_interpretation": emotion_interpretation
            },
            "topics": topics,
            "insights": insights,
            "best_comments": best_comments,
            "constructive_comments": constructive_comments,
            "most_engaged": most_engaged,
            "most_positive": most_positive,
            "negative_comments": {
                "constructive_criticism": constructive_criticism[:8],
                "critical_complaints": critical_complaints[:8],
                "toxic_comments": toxic_comments[:8]
            },
            "toxic_comments": toxic_comments,
            "comments": analyzed_comments
        }

        return session_data

    def _extract_topics(self, comments: list, top_n: int = 10) -> list:
        """
        Extracts frequently occurring meaningful words and topics from comments,
        filtering out common stop words. Completely dynamic per video.
        """
        words = []
        bigrams = []

        for c in comments:
            text = c.get("cleaned_text") or c.get("comment_text", "").lower()
            tokens = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()) if w not in STOP_WORDS]
            words.extend(tokens)

            # Meaningful bigrams
            if len(tokens) >= 2:
                for i in range(len(tokens) - 1):
                    bigram = f"{tokens[i]} {tokens[i+1]}"
                    bigrams.append(bigram)

        unigram_counts = Counter(words)
        bigram_counts = Counter([b for b in bigrams if bigram_counts_filter(b)])

        # Combine single words and multi-word topics
        combined_topics = []
        
        # Add bigrams that appeared at least twice
        for phrase, count in bigram_counts.most_common(5):
            if count >= 2:
                combined_topics.append({"topic": phrase.title(), "count": count, "type": "phrase"})

        # Fill remaining with top unigrams
        for word, count in unigram_counts.most_common(top_n * 2):
            # Avoid single words already in bigram
            if not any(word in t["topic"].lower() for t in combined_topics):
                combined_topics.append({"topic": word.capitalize(), "count": count, "type": "word"})
            if len(combined_topics) >= top_n:
                break

        return combined_topics[:top_n]

    def _generate_emotion_interpretation(self, dominant_emotion: str, dominant_pct: float,
                                         pos_pct: float, neg_pct: float, emotion_totals: dict) -> str:
        """Generates dynamic natural language description of emotional patterns."""
        if dominant_emotion == "happiness":
            return (
                f"Most viewers responded warmly to the content, with Happiness detected as the dominant emotion "
                f"({dominant_pct}% of emotional signals). Viewers consistently expressed gratitude, enjoyment, "
                f"and appreciation for the presentation."
            )
        elif dominant_emotion == "surprise":
            return (
                f"Viewers experienced high engagement with unexpected discoveries and 'aha' moments, with Surprise "
                f"leading at {dominant_pct}%. Concepts or demonstrations resonated as novel and eye-opening."
            )
        elif dominant_emotion == "fear":
            return (
                f"Audience reactions reflected apprehension or confusion ({dominant_pct}% Fear signals), "
                f"frequently around challenging implementation steps, prerequisites, or installation friction."
            )
        elif dominant_emotion == "anger":
            return (
                f"A notable portion of viewers felt frustrated or annoyed ({dominant_pct}% Anger signals), "
                f"typically tied to technical errors, pacing issues, or audio balance."
            )
        elif dominant_emotion == "sadness":
            return (
                f"Viewer sentiment leaned towards disappointment or struggle ({dominant_pct}% Sadness signals), "
                f"often stemming from troubleshooting difficulties or feeling overwhelmed."
            )
        else:
            return (
                f"Audience response was largely objective and analytical, with Neutral/Informational commentary "
                f"dominating. Overall positive sentiment stands at {pos_pct}%, reflecting practical, constructive dialogue."
            )

    def _generate_insights(self, comments: list, pos_pct: float, neu_pct: float, neg_pct: float,
                           toxic_pct: float, constructive: list, complaints: list,
                           toxic: list, dominant_emotion: str) -> dict:
        """
        Dynamically extracts audience mood, loved highlights, complaints,
        potential risks, and actionable creator recommendations.
        """
        if pos_pct >= 70:
            mood_summary = f"Exceptionally positive audience sentiment ({pos_pct}% positive). The community is highly supportive, appreciative, and enthusiastic."
            mood_status = "Excellent"
        elif pos_pct >= 50:
            mood_summary = f"Solid healthy audience reception ({pos_pct}% positive, {neu_pct}% neutral). General feedback is constructive and engaged."
            mood_status = "Good"
        elif neg_pct > pos_pct:
            mood_summary = f"Critical audience reception ({neg_pct}% negative vs {pos_pct}% positive). Significant friction detected in content delivery or topic reception."
            mood_status = "Attention Needed"
        else:
            mood_summary = f"Balanced, discussion-driven reaction ({neu_pct}% neutral, {pos_pct}% positive). Audience is focused on practical questions and analysis."
            mood_status = "Balanced"

        # What Viewers Loved (Dynamic extraction from positive comments)
        loved_themes = []
        positive_comments = [c for c in comments if c["sentiment"] == "Positive"]
        positive_texts = " ".join([c["comment_text"].lower() for c in positive_comments])
        
        theme_checks = [
            (r"\b(clear|clearly|clarity|well\s+explained)\b", "Crystal clear explanations and easy-to-follow pacing"),
            (r"\b(diagram|visual|visuals|architecture)\b", "Visual architecture breakdowns and illustrative diagrams"),
            (r"\b(code|walkthrough|practical|example|hands\s*on)\b", "Practical, hands-on coding demonstrations"),
            (r"\b(project|final\s+year|portfolio|assignment)\b", "High real-world relevance for portfolios and academic projects"),
            (r"\b(fast|concise|no\s+waste|straight\s+to\s+the\s+point)\b", "Concise delivery without unnecessary fluff or self-promotion"),
            (r"\b(dark\s+mode|clean\s+ui|design)\b", "Aesthetic design and user interface quality"),
            (r"\b(responsive|performance|batch)\b", "Speed and responsiveness of demonstrated features"),
            (r"\b(music|soundtrack|song|audio)\b", "Engaging soundtrack and sound design"),
            (r"\b(funny|hilarious|laugh|comedy)\b", "Entertaining presentation style and humor")
        ]
        for pattern, label in theme_checks:
            if re.search(pattern, positive_texts):
                loved_themes.append(label)

        if not loved_themes and positive_comments:
            # Fallback to quoting an actual top positive sentence
            sample_phrase = positive_comments[0]["comment_text"][:80] + "..."
            loved_themes.append(f"Viewers appreciated positive aspects like: \"{sample_phrase}\"")
        elif not loved_themes:
            loved_themes.append("Overall tutorial quality, guidance, and helpful insights.")

        # Common Complaints & Friction
        complaint_themes = []
        negative_texts = " ".join([c["comment_text"].lower() for c in comments if c["sentiment"] == "Negative" or c["quality"]["is_constructive"]])

        friction_checks = [
            (r"\b(too\s+fast|slow\s+down|quick)\b", "Pacing in certain intermediate steps felt rushed for beginners"),
            (r"\b(audio|volume|sound|microphone|quiet|loud|music)\b", "Audio equalization or background music volume inconsistencies"),
            (r"\b(too\s+long|length|shorten|minutes)\b", "Video length felt slightly extended for busy viewers"),
            (r"\b(github|repo|source\s+code|link)\b", "Requests for direct source code, repository links, or starter files"),
            (r"\b(error|bug|modulenotfound|failed|broken)\b", "Setup / environment dependency issues experienced by viewers"),
            (r"\b(subtitle|subtitles|transcript|translation)\b", "Viewer requests for subtitles and multilingual translations"),
            (r"\b(ads|sponsor|sponsored|commercial)\b", "Viewer feedback regarding ad placement or sponsorship duration")
        ]
        for pattern, label in friction_checks:
            if re.search(pattern, negative_texts):
                complaint_themes.append(label)

        if not complaint_themes:
            complaint_themes.append("No major widespread complaints detected; isolated minor questions only.")

        # Potential Problems
        potential_problems = []
        if toxic_pct > 5.0:
            potential_problems.append(f"Elevated toxicity rate ({toxic_pct}%): Consider moderating abusive comments or enabling strict filter rules.")
        elif toxic_pct > 0:
            potential_problems.append(f"Low toxicity detected ({toxic_pct}%): Normal online noise, within healthy creator platform boundaries.")
        else:
            potential_problems.append("Zero detected toxicity! Comment section community health is exemplary.")

        if neg_pct > 25.0:
            potential_problems.append(f"High negative sentiment ({neg_pct}%): Audience confusion or discontent indicates a need for pinned clarification comments.")

        # Actionable Content Suggestions
        recommendations = []
        if any("audio" in t.lower() for t in complaint_themes):
            recommendations.append("Normalize microphone volume and dial down background music during detailed voiceovers.")
        if any("too fast" in t.lower() for t in complaint_themes):
            recommendations.append("Add on-screen chapter bookmarks and brief recap checkpoints after complex steps.")
        if any("source code" in t.lower() or "github" in t.lower() for t in complaint_themes):
            recommendations.append("Pin a comment with links to the GitHub repository, dependencies list, and documentation.")
        if any("practical" in t.lower() for t in loved_themes):
            recommendations.append("Double-down on practical, real-world demos — viewers consistently cite this as your strongest differentiator.")
        if any("error" in t.lower() for t in complaint_themes):
            recommendations.append("Create a pinned FAQ addressing common environment/setup questions to save viewer troubleshooting time.")

        if not recommendations:
            recommendations.append("Continue the current pacing and structure; viewers find the instructional style highly effective.")
            recommendations.append("Engage with top constructive comments to foster deeper community retention.")

        return {
            "audience_mood": mood_summary,
            "mood_status": mood_status,
            "what_viewers_loved": loved_themes[:5],
            "common_complaints": complaint_themes[:5],
            "potential_problems": potential_problems[:3],
            "recommendations": recommendations[:5]
        }

    def _empty_result(self, video_title: str, video_info: dict = None) -> dict:
        """Fallback for empty comments list."""
        resolved_title = (video_info.get("title") if video_info else None) or video_title or "YouTube Video Analysis"
        resolved_channel = (video_info.get("channel_title") if video_info else None) or "YouTube Channel"
        resolved_video_id = (video_info.get("video_id") if video_info else None) or ""

        return {
            "session_id": "sess_empty",
            "video_id": resolved_video_id,
            "video_title": resolved_title,
            "channel_name": resolved_channel,
            "video_info": video_info or {
                "video_id": resolved_video_id,
                "title": resolved_title,
                "channel_title": resolved_channel,
                "thumbnail_url": "",
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_comments": 0,
            "metrics": {
                "total_comments": 0,
                "positive_count": 0,
                "positive_percentage": 0.0,
                "neutral_count": 0,
                "neutral_percentage": 0.0,
                "negative_count": 0,
                "negative_percentage": 0.0,
                "toxic_count": 0,
                "toxicity_percentage": 0.0,
                "constructive_count": 0,
                "constructive_percentage": 0.0,
                "average_quality": 0.0,
                "dominant_emotion": "neutral",
                "dominant_emotion_percentage": 0.0,
                "emotion_totals": {"happiness": 0, "sadness": 0, "anger": 0, "fear": 0, "surprise": 0, "neutral": 0},
                "emotion_interpretation": "No comments available for analysis."
            },
            "topics": [],
            "insights": {
                "audience_mood": "No comments analyzed yet.",
                "mood_status": "N/A",
                "what_viewers_loved": [],
                "common_complaints": [],
                "potential_problems": [],
                "recommendations": []
            },
            "best_comments": [],
            "constructive_comments": [],
            "most_engaged": [],
            "most_positive": [],
            "negative_comments": {
                "constructive_criticism": [],
                "critical_complaints": [],
                "toxic_comments": []
            },
            "toxic_comments": [],
            "comments": []
        }


def bigram_counts_filter(bigram: str) -> bool:
    """Helper to check if bigram contains only alphabetic terms."""
    parts = bigram.split()
    return len(parts) == 2 and all(p not in STOP_WORDS for p in parts)
