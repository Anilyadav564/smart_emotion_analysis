import re


class ToxicityAnalyzer:
    """
    Lightweight, high-performance rule-based toxicity analyzer.
    Detects profanity, insults, harassment, threats, and hate-like language.
    Structured so an ML/Transformer model can easily replace or augment it in the future.
    """

    def __init__(self):
        # Specific category lexicons and patterns
        self.categories = {
            "threat": [
                r"\bkill\b", r"\bkilling\b", r"\bmurder\b", r"\bdie\b", r"\bshoot\b",
                r"\bbeat\s+you\b", r"\bhurt\s+you\b", r"\bdestroy\s+you\b",
                r"\bhope\s+you\s+die\b", r"\bwatch\s+your\s+back\b", r"\bpunch\b"
            ],
            "insult": [
                r"\bidiot\b", r"\bmoron\b", r"\bstupid\b", r"\bdumb\b", r"\bclown\b",
                r"\bloser\b", r"\bpathetic\b", r"\bworthless\b", r"\btrash\b",
                r"\bgarbage\b", r"\buseless\s+person\b", r"\bjerk\b", r"\basshole\b",
                r"\bbastard\b", r"\bdick\b", r"\bscam\s*artist\b", r"\bfool\b"
            ],
            "harassment": [
                r"\bget\s+lost\b", r"\bshut\s+up\b", r"\bgo\s+away\b", r"\bunsubscribe\b",
                r"\bstop\s+posting\b", r"\bdelete\s+your\s+channel\b", r"\bnever\s+post\s+again\b",
                r"\bquit\s+youtube\b", r"\bkill\s+yourself\b", r"\bkys\b", r"\bno\s+one\s+likes\s+you\b"
            ],
            "profanity": [
                r"\bfuck\b", r"\bfucking\b", r"\bfucked\b", r"\bshit\b", r"\bbitch\b",
                r"\bdamn\b", r"\bass\b", r"\bcrap\b", r"\bpiss\b", r"\bwtf\b",
                r"\bstfu\b", r"\bwth\b"
            ],
            "hate_speech": [
                r"\bracist\b", r"\bnazi\b", r"\bbigot\b", r"\bhate\s+all\b"
            ]
        }

        # Precompile regexes for optimal batch performance
        self.compiled_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.categories.items()
        }

    def analyze(self, text: str) -> dict:
        """
        Analyzes a single text string for toxicity.
        Returns toxicity score (0.0 to 1.0), flag status, and detected categories.
        """
        if not text or not isinstance(text, str):
            return {
                "is_toxic": False,
                "toxicity_score": 0.0,
                "status": "Safe",
                "categories": [],
                "primary_category": "Non-toxic"
            }

        detected_categories = []
        match_count = 0

        for category, patterns in self.compiled_patterns.items():
            cat_matches = 0
            for pattern in patterns:
                if pattern.search(text):
                    cat_matches += 1
            if cat_matches > 0:
                detected_categories.append(category)
                # Severe categories (threat, hate_speech, harassment) carry extra weight
                weight = 2 if category in ["threat", "harassment", "hate_speech"] else 1
                match_count += cat_matches * weight

        # Continuous score normalization
        if match_count == 0:
            toxicity_score = 0.0
            status = "Safe"
            primary_category = "Non-toxic"
            is_toxic = False
        elif match_count == 1:
            toxicity_score = 0.45
            status = "Potentially Harmful"
            primary_category = detected_categories[0].capitalize()
            is_toxic = False
        elif match_count == 2:
            toxicity_score = 0.75
            status = "Toxic"
            primary_category = detected_categories[0].capitalize()
            is_toxic = True
        else:
            toxicity_score = min(1.0, 0.75 + (match_count - 2) * 0.1)
            status = "Toxic"
            primary_category = detected_categories[0].capitalize()
            is_toxic = True

        return {
            "is_toxic": is_toxic,
            "toxicity_score": round(toxicity_score, 2),
            "status": status,
            "categories": detected_categories,
            "primary_category": primary_category
        }
