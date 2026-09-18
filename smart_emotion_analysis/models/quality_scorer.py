import re
import math


class QualityScorer:
    """
    Computes a 0–100 Comment Quality & Usefulness Score.
    Identifies constructive criticism, high-value suggestions, engagement weight,
    and penalizes toxic or low-effort spam.
    """

    def __init__(self):
        # Patterns signaling constructive suggestions, critique, or questions
        self.constructive_patterns = [
            r"\b(could|would|should|can)\s+(you|we)\b",
            r"\b(suggest|suggestion|recommend|improvement|feedback)\b",
            r"\b(better\s+if|helpful\s+if|easier\s+if|next\s+time)\b",
            r"\b(too\s+(fast|slow|loud|quiet|quick|long|short|confusing|complex))\b",
            r"\b(step\s+\d+|minute\s+\d+|at\s+\d+:\d+|\d+:\d+)\b",  # timestamps / steps
            r"\b(please\s+explain|didn't\s+understand|unclear|clarify|elaborate)\b",
            r"\b(audio\s+is|microphone|sound\s+is|video\s+quality|screen\s+size|font\s+size)\b",
            r"\b(source\s+code|github\s+link|repo|documentation|link\s+in\s+description)\b",
            r"\b(example|use\s+case|real\s+world|difference\s+between)\b",
            r"\b(how\s+do\s+I|how\s+to|what\s+about|why\s+did\s+you)\b"
        ]
        self.compiled_constructive = [re.compile(p, re.IGNORECASE) for p in self.constructive_patterns]

        # Spam / low-effort indicators
        self.spam_patterns = [
            r"^(first|1st|hi|hello|nice|cool|good|ok|lol|wow|bruh|sub|sub4sub|subscribe)$",
            r"^(.)\1{4,}$",  # repeated characters like "aaaaaa" or "!!!!!!"
            r"\b(check\s+out\s+my\s+channel|free\s+crypto|telegram|whatsapp)\b"
        ]
        self.compiled_spam = [re.compile(p, re.IGNORECASE) for p in self.spam_patterns]

    def evaluate_comment(self, text: str, sentiment: str, sentiment_compound: float,
                         toxicity_info: dict, likes: int = 0) -> dict:
        """
        Evaluates a comment and returns:
        - quality_score (0–100)
        - quality_grade ('Excellent', 'Good', 'Average', 'Low', 'Very Low')
        - is_constructive (bool)
        - feedback_type ('Top Praise', 'Constructive Feedback', 'Helpful Question', 'General Discussion', 'Low Effort', 'Critical Complaint', 'Toxic/Abusive')
        - explanation (human readable reason)
        """
        cleaned = text.strip() if text else ""
        word_count = len(cleaned.split())
        char_count = len(cleaned)

        if char_count == 0:
            return {
                "quality_score": 0,
                "quality_grade": "Very Low",
                "is_constructive": False,
                "feedback_type": "Low Effort",
                "explanation": "Empty comment."
            }

        # Check for spam or low effort
        is_spam = any(p.search(cleaned.lower()) for p in self.compiled_spam)
        if is_spam and word_count <= 2:
            return {
                "quality_score": 15,
                "quality_grade": "Very Low",
                "is_constructive": False,
                "feedback_type": "Low Effort",
                "explanation": "Low-effort generic word or repeated character spam."
            }

        # Constructiveness detection
        constructive_hits = sum(1 for p in self.compiled_constructive if p.search(cleaned))
        is_constructive = constructive_hits > 0 or "?" in cleaned

        # Base score components (Total max: 100)
        # 1. Length & Readability (up to 25 pts)
        if word_count < 3:
            length_pts = 5
        elif word_count < 8:
            length_pts = 14
        elif word_count < 35:
            length_pts = 25  # Sweet spot for informative comments
        elif word_count < 80:
            length_pts = 22
        else:
            length_pts = 18  # Very long walls of text slightly tapered

        # 2. Specificity & Constructiveness (up to 30 pts)
        constructive_pts = min(30, constructive_hits * 10)
        if "?" in cleaned and constructive_pts == 0:
            constructive_pts += 10

        # 3. Sentiment & Tone (up to 25 pts)
        # Constructive comments shouldn't be penalized heavily for mild negative tone
        if sentiment == "Positive":
            sentiment_pts = int(15 + max(0, sentiment_compound) * 10)
        elif sentiment == "Neutral":
            sentiment_pts = 18  # Neutral factual feedback is great
        else:  # Negative
            if is_constructive:
                sentiment_pts = 14  # Constructive criticism is still valuable
            else:
                sentiment_pts = 6   # Raw negative venting

        # 4. Engagement / Likes (up to 20 pts)
        # Likes follow logarithmic scaling so 1-10 likes gives a boost, 100+ maxes out
        if likes > 0:
            likes_pts = min(20, int(math.log10(likes + 1) * 7.5))
        else:
            likes_pts = 8  # neutral baseline if likes count unavailable

        # Calculate initial raw score
        raw_score = length_pts + constructive_pts + sentiment_pts + likes_pts

        # 5. Toxicity penalty
        toxicity_score = toxicity_info.get("toxicity_score", 0.0)
        if toxicity_info.get("is_toxic", False):
            raw_score -= int(toxicity_score * 70)  # Severe deduction
        elif toxicity_info.get("status") == "Potentially Harmful":
            raw_score -= 25

        # Clamp between 0 and 100
        quality_score = max(0, min(100, raw_score))

        # Determine Quality Grade
        if quality_score >= 90:
            quality_grade = "Excellent"
        elif quality_score >= 75:
            quality_grade = "Good"
        elif quality_score >= 50:
            quality_grade = "Average"
        elif quality_score >= 25:
            quality_grade = "Low"
        else:
            quality_grade = "Very Low"

        # Determine nuanced feedback category
        if toxicity_info.get("is_toxic", False):
            feedback_type = "Toxic/Abusive"
            explanation = "Comment contains offensive, hostile, or abusive language."
        elif is_constructive and sentiment in ["Negative", "Neutral"]:
            feedback_type = "Constructive Feedback"
            explanation = "Actionable critique or improvement suggestion with specific context."
        elif is_constructive and sentiment == "Positive":
            feedback_type = "Constructive Feedback"
            explanation = "Positive feedback with specific suggestions or thoughtful questions."
        elif sentiment == "Negative":
            feedback_type = "Critical Complaint"
            explanation = "Negative audience reaction expressing dissatisfaction or confusion."
        elif sentiment == "Positive" and quality_score >= 80:
            feedback_type = "Top Praise"
            explanation = "High-quality, thoughtful praise highlighting specific value."
        elif "?" in cleaned:
            feedback_type = "Helpful Question"
            explanation = "Viewer inquiry or clarification request."
        elif word_count <= 3:
            feedback_type = "Low Effort"
            explanation = "Short or generic reaction."
        else:
            feedback_type = "General Discussion"
            explanation = "Standard audience commentary and discussion."

        return {
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "is_constructive": is_constructive,
            "feedback_type": feedback_type,
            "explanation": explanation
        }
